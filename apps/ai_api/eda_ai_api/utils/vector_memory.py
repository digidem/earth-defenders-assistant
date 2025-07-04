import chromadb
import uuid
import pandas as pd
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from eda_config.config import ConfigLoader
from eda_ai_api.utils.memory import PocketBaseMemory

config = ConfigLoader.get_config()


class VectorMemory(PocketBaseMemory):
    """Enhanced memory manager for conversations and documents with TTL - user-specific collections"""

    # Singleton instance
    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern to prevent multiple expensive initializations"""
        if cls._instance is None:
            cls._instance = super(VectorMemory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize PocketBase and ChromaDB clients - only once due to singleton pattern"""
        # Prevent multiple initializations
        if self._initialized:
            return

        super().__init__()
        try:
            # Initialize embeddings model
            self.embedding_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

            # Initialize ChromaDB persistent client
            persist_directory = "./chroma_conversation_db"
            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory
            )
            logger.info(
                f"ChromaDB client initialized with persistence directory: {persist_directory}"
            )

            # Initialize text splitter for documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
            )

            # Initialize global knowledge base collection
            self.global_knowledge_collection = self.chroma_client.get_or_create_collection(
                name="global_knowledge_base",
                metadata={
                    "hnsw:space": "cosine",
                    "type": "global_knowledge",
                    "description": "Global knowledge base accessible to all users",
                },
            )

            logger.info(
                "VectorMemory initialized successfully with user-specific collection support and global knowledge base"
            )

            # Mark as initialized to prevent re-initialization
            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize VectorMemory: {str(e)}")
            raise RuntimeError(
                f"Vector memory initialization error: {str(e)}"
            ) from e

    def _get_user_collection_names(
        self, session_id: str, platform: str = "whatsapp"
    ) -> Tuple[str, str]:
        """Generate user-specific collection names"""
        # Create a consistent user identifier
        user_id = (
            f"{platform}_{session_id}".replace("-", "_")
            .replace("@", "_at_")
            .replace(".", "_dot_")
        )
        # Ensure collection names are valid (alphanumeric + underscore)
        user_id = "".join(
            c if c.isalnum() or c == "_" else "_" for c in user_id
        )

        conversation_collection_name = f"conv_{user_id}"
        document_collection_name = f"docs_{user_id}"

        return conversation_collection_name, document_collection_name

    def _get_user_collections(
        self, session_id: str, platform: str = "whatsapp"
    ):
        """Get or create user-specific collections"""
        conv_name, doc_name = self._get_user_collection_names(
            session_id, platform
        )

        # Get or create conversation collection for this user
        conversation_collection = self.chroma_client.get_or_create_collection(
            name=conv_name,
            metadata={
                "hnsw:space": "cosine",
                "type": "conversation",
                "user": session_id,
                "platform": platform,
            },
        )

        # Get or create document collection for this user
        document_collection = self.chroma_client.get_or_create_collection(
            name=doc_name,
            metadata={
                "hnsw:space": "cosine",
                "type": "document",
                "user": session_id,
                "platform": platform,
            },
        )

        return conversation_collection, document_collection

    async def add_message_to_history(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        platform: str = "whatsapp",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Store a message exchange in both PocketBase and user-specific conversation vector database"""
        # First, store in PocketBase using parent method
        result = await super().add_message_to_history(
            session_id, user_message, assistant_response, platform, metadata
        )

        if not result:
            logger.error("Failed to add message to PocketBase")
            return False

        try:
            # Get user-specific collections
            conversation_collection, _ = self._get_user_collections(
                session_id, platform
            )

            # Create combined text for embedding
            combined_text = (
                f"USER: {user_message}\nASSISTANT: {assistant_response}"
            )

            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()

            # Create document ID
            doc_id = f"{platform}_{session_id}_{datetime.now().isoformat()}"

            # Prepare metadata - flatten nested dictionaries
            doc_metadata = {
                "type": "conversation",
                "platform": platform,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response,
            }

            # If additional metadata is provided, flatten it
            if metadata:
                flattened = {}
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        flattened[key] = value
                    elif isinstance(value, dict):
                        # Flatten nested dict with dot notation
                        for k, v in value.items():
                            if isinstance(v, (str, int, float, bool)):
                                flattened[f"{key}_{k}"] = v
                doc_metadata.update(flattened)

            # Add to user-specific conversation collection
            conversation_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[combined_text],
            )

            logger.info(
                f"Added message pair to user-specific conversation collection for session {session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add message to vector database: {str(e)}")
            return False

    async def semantic_search(
        self,
        session_id: str,
        query: str,
        platform: str = "whatsapp",
        limit: int = 5,
        filter_by_session: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search conversation history using semantic similarity in user-specific collection"""
        try:
            # Get user-specific collections
            conversation_collection, _ = self._get_user_collections(
                session_id, platform
            )

            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Since we're using user-specific collections, we don't need session filtering
            # but we can still filter by type for consistency
            where_filter = {"type": "conversation"}

            # Execute search query on user-specific conversation collection
            results = conversation_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=["metadatas", "documents", "distances"],
            )

            # Format results
            formatted_results = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    result = {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i],
                    }
                    formatted_results.append(result)

            logger.info(
                f"Semantic search returned {len(formatted_results)} results for user {session_id}"
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    async def get_relevant_history(
        self,
        session_id: str,
        current_query: str,
        platform: str = "whatsapp",
        limit: int = 3,
        cross_session: bool = False,
    ) -> List[Dict]:
        """
        Get conversation history relevant to the current query from user-specific collection

        Args:
            session_id: User's platform ID
            current_query: The current user message
            platform: Platform identifier
            limit: Maximum number of relevant items to return
            cross_session: Whether to search across all sessions (ignored since collections are user-specific)

        Returns:
            List of relevant conversation exchanges in formatted context
        """
        try:
            # Get semantically relevant conversation snippets from user-specific collection
            relevant_items = await self.semantic_search(
                session_id=session_id,
                query=current_query,
                platform=platform,
                limit=limit,
                filter_by_session=True,  # This doesn't matter since collection is user-specific
            )

            # Format for context
            formatted_history = []
            for item in relevant_items:
                metadata = item.get("metadata")  # Use .get for safety
                if metadata:  # Check if metadata exists
                    formatted_history.append(
                        {
                            "user": metadata.get("user_message", ""),
                            "assistant": metadata.get("assistant_response", ""),
                            "timestamp": metadata.get("timestamp", ""),
                            "relevance": item.get(
                                "similarity"
                            ),  # Use the calculated similarity
                        }
                    )

            # Sort by relevance (higher similarity first)
            formatted_history.sort(
                key=lambda x: x.get("relevance", 0), reverse=True
            )

            return formatted_history

        except Exception as e:
            logger.error(f"Error retrieving relevant history: {str(e)}")
            return []

    async def clear_vector_history(
        self, session_id: str, platform: str = "whatsapp"
    ) -> bool:
        """
        Remove all vectorized conversation history for a specific user

        Args:
            session_id: User's platform ID
            platform: Platform identifier

        Returns:
            bool: Success status
        """
        try:
            # Get user-specific collection names
            conv_name, doc_name = self._get_user_collection_names(
                session_id, platform
            )

            # Delete the entire user-specific conversation collection
            try:
                self.chroma_client.delete_collection(name=conv_name)
                logger.info(
                    f"Cleared vector history collection for user {session_id}"
                )
            except Exception as e:
                # Collection might not exist, which is fine
                logger.info(
                    f"No conversation collection found for user {session_id}"
                )

            return True
        except Exception as e:
            logger.error(f"Error clearing vector history: {str(e)}")
            return False

    async def add_document(
        self,
        session_id: str,
        file_path: str,
        content_type: str,
        platform: str = "whatsapp",
        ttl_days: int = 30,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Generic document processor that handles both PDF and CSV for specific user"""
        try:
            # Get user-specific collections
            _, document_collection = self._get_user_collections(
                session_id, platform
            )

            all_chunks = []
            expiration_date = datetime.now() + timedelta(days=ttl_days)
            # Store as numeric timestamp for ChromaDB queries
            expiration_timestamp = expiration_date.timestamp()

            if content_type == "application/pdf":
                # PDF processing
                pdf = PdfReader(file_path)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text.strip():
                        chunks = self.text_splitter.split_text(text)
                        for chunk in chunks:
                            all_chunks.append(
                                {"content": chunk, "page": page_num + 1}
                            )

            elif content_type in ["text/csv", "application/csv"]:
                # CSV processing
                with open(file_path, "r", encoding="utf-8") as f:
                    csv_content = f.read()
                all_chunks = self._process_csv_content(csv_content)

            # Prepare document chunks for storage
            chunk_ids = []
            chunk_texts = []
            chunk_embeddings = []
            chunk_metadatas = []

            for chunk in all_chunks:
                chunk_id = f"doc_{session_id}_{uuid.uuid4()}"
                if "page" in chunk:
                    chunk_id += f"_page_{chunk['page']}"
                elif "row" in chunk:
                    chunk_id += f"_row_{chunk['row']}"

                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk["content"])

                # Generate embedding
                embedding = self.embedding_model.encode(
                    chunk["content"]
                ).tolist()
                chunk_embeddings.append(embedding)

                # Prepare metadata
                chunk_metadata = {
                    "type": "document",
                    "source": file_path,
                    "session_id": session_id,
                    "platform": platform,
                    "expiration_timestamp": expiration_timestamp,  # Numeric timestamp for queries
                    "document_type": (
                        "pdf" if content_type == "application/pdf" else "csv"
                    ),
                }

                # Add specific metadata for CSV/PDF
                if "row" in chunk:
                    chunk_metadata.update(
                        {
                            "row": str(chunk["row"]),
                            "columns": chunk["columns"],
                        }
                    )
                elif "page" in chunk:
                    chunk_metadata.update({"page": str(chunk["page"])})

                # Add any additional metadata
                if metadata:
                    # Convert any non-string/number values to strings
                    sanitized_metadata = {
                        k: (
                            str(v)
                            if not isinstance(v, (str, int, float, bool))
                            else v
                        )
                        for k, v in metadata.items()
                    }
                    chunk_metadata.update(sanitized_metadata)

                chunk_metadatas.append(chunk_metadata)

            # Store in user-specific document collection
            if chunk_ids:
                document_collection.add(
                    ids=chunk_ids,
                    documents=chunk_texts,
                    embeddings=chunk_embeddings,
                    metadatas=chunk_metadatas,
                )

                logger.info(
                    f"Added document with {len(chunk_ids)} chunks for user {session_id} with {ttl_days} days TTL"
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False

    def search_documents(
        self,
        session_id: str,
        query: str,
        platform: str = "whatsapp",
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Search document chunks with TTL filtering in user-specific collection"""
        try:
            # Get user-specific collections
            _, document_collection = self._get_user_collections(
                session_id, platform
            )

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Current timestamp for TTL checking
            current_timestamp = datetime.now().timestamp()

            # Search in user-specific document collection with TTL filter
            results = document_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
                * 2,  # Get extra results in case some are expired
                where={
                    "$and": [
                        {"type": "document"},
                        {"expiration_timestamp": {"$gt": current_timestamp}},
                    ]
                },
                include=["metadatas", "documents", "distances"],
            )

            # Format and filter results
            formatted_results = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    similarity = 1 - results["distances"][0][i]
                    result = {
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                    }
                    formatted_results.append(result)

            # Sort by similarity and limit results
            formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
            logger.info(
                f"Document search returned {len(formatted_results[:limit])} results for user {session_id}"
            )
            return formatted_results[:limit]

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    async def cleanup_expired_documents(
        self, session_id: str = None, platform: str = "whatsapp"
    ) -> int:
        """Remove expired document chunks from user-specific or all document collections"""
        try:
            current_timestamp = datetime.now().timestamp()
            total_removed = 0

            if session_id:
                # Clean up for specific user
                logger.info(
                    f"Running cleanup for user {session_id} documents expired before timestamp: {current_timestamp}"
                )

                _, document_collection = self._get_user_collections(
                    session_id, platform
                )

                all_docs = document_collection.get(include=["metadatas"])

                expired_ids = []
                if all_docs and all_docs["ids"]:
                    for i in range(len(all_docs["ids"])):
                        doc_id = all_docs["ids"][i]
                        metadata = all_docs["metadatas"][i]

                        if (
                            metadata
                            and "expiration_timestamp" in metadata
                            and metadata["expiration_timestamp"]
                            < current_timestamp
                        ):
                            expired_ids.append(doc_id)

                if expired_ids:
                    document_collection.delete(ids=expired_ids)
                    logger.info(
                        f"Successfully deleted {len(expired_ids)} expired document chunks for user {session_id}"
                    )
                    total_removed = len(expired_ids)
            else:
                # Clean up for all users
                logger.info(
                    f"Running system-wide cleanup for documents expired before timestamp: {current_timestamp}"
                )

                all_collections = self.chroma_client.list_collections()

                for collection_info in all_collections:
                    collection_name = collection_info.name
                    if collection_name.startswith("docs_"):
                        try:
                            collection = self.chroma_client.get_collection(
                                collection_name
                            )
                            all_docs = collection.get(include=["metadatas"])

                            expired_ids = []
                            if all_docs and all_docs["ids"]:
                                for i in range(len(all_docs["ids"])):
                                    doc_id = all_docs["ids"][i]
                                    metadata = all_docs["metadatas"][i]

                                    if (
                                        metadata
                                        and "expiration_timestamp" in metadata
                                        and metadata["expiration_timestamp"]
                                        < current_timestamp
                                    ):
                                        expired_ids.append(doc_id)

                            if expired_ids:
                                collection.delete(ids=expired_ids)
                                logger.info(
                                    f"Deleted {len(expired_ids)} expired documents from {collection_name}"
                                )
                                total_removed += len(expired_ids)

                        except Exception as e:
                            logger.warning(
                                f"Error cleaning up collection {collection_name}: {str(e)}"
                            )

            logger.info(
                f"Total cleanup completed. Removed {total_removed} expired document chunks."
            )
            return total_removed

        except Exception as e:
            logger.error(
                f"Error during cleanup of expired documents: {str(e)}",
                exc_info=True,
            )
            return 0

    def _process_csv_content(self, csv_content: str) -> List[Dict[str, Any]]:
        """Process CSV content into chunks suitable for vector storage"""
        try:
            # Read CSV content
            df = pd.read_csv(io.StringIO(csv_content))

            # Convert each row to a text chunk
            chunks = []
            columns = list(df.columns)

            for index, row in df.iterrows():
                # Convert row to string representation
                row_text = " | ".join(
                    f"{col}: {val}" for col, val in row.items() if pd.notna(val)
                )

                chunks.append(
                    {
                        "content": row_text,
                        "row": index,
                        "columns": ",".join(columns),
                    }
                )

            return chunks

        except Exception as e:
            logger.error(f"Error processing CSV content: {str(e)}")
            raise

    # Keep the old method for backward compatibility but mark it as deprecated
    async def add_pdf_document(
        self, pdf_path: str, ttl_days: int = 30, metadata: Optional[Dict] = None
    ) -> bool:
        """DEPRECATED: Use add_document with session_id instead"""
        logger.warning(
            "add_pdf_document is deprecated. Use add_document with session_id parameter."
        )
        return False

    async def add_global_knowledge(
        self,
        file_path: str,
        content_type: str,
        source_name: str = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Add content to the global knowledge base

        Args:
            file_path: Path to the file to process
            content_type: MIME type of the file
            source_name: Human-readable name for the source
            metadata: Additional metadata

        Returns:
            bool: Success status
        """
        try:
            all_chunks = []

            if content_type == "application/pdf":
                # PDF processing
                pdf = PdfReader(file_path)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text.strip():
                        chunks = self.text_splitter.split_text(text)
                        for chunk in chunks:
                            all_chunks.append(
                                {
                                    "content": chunk,
                                    "page": page_num + 1,
                                    "type": "pdf",
                                }
                            )

            elif content_type in ["text/csv", "application/csv"]:
                # CSV processing
                with open(file_path, "r", encoding="utf-8") as f:
                    csv_content = f.read()
                all_chunks = self._process_csv_content(csv_content)

            elif content_type == "text/plain":
                # Plain text processing
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                chunks = self.text_splitter.split_text(text)
                for i, chunk in enumerate(chunks):
                    all_chunks.append(
                        {"content": chunk, "chunk": i + 1, "type": "text"}
                    )

            # Prepare document chunks for storage
            chunk_ids = []
            chunk_texts = []
            chunk_embeddings = []
            chunk_metadatas = []

            for chunk in all_chunks:
                chunk_id = f"global_{uuid.uuid4()}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk["content"])

                # Generate embedding
                embedding = self.embedding_model.encode(
                    chunk["content"]
                ).tolist()
                chunk_embeddings.append(embedding)

                # Prepare metadata
                doc_metadata = {
                    "type": "global_knowledge",
                    "source": source_name or file_path,
                    "added_date": datetime.now().isoformat(),
                }

                # Add chunk-specific metadata
                if "page" in chunk:
                    doc_metadata["page"] = chunk["page"]
                elif "row" in chunk:
                    doc_metadata["row"] = chunk["row"]
                elif "chunk" in chunk:
                    doc_metadata["chunk"] = chunk["chunk"]

                # Flatten any additional metadata
                if metadata:
                    flattened = self._flatten_metadata(metadata)
                    doc_metadata.update(flattened)

                chunk_metadatas.append(doc_metadata)

            # Store in global knowledge collection
            if chunk_ids:
                self.global_knowledge_collection.add(
                    ids=chunk_ids,
                    embeddings=chunk_embeddings,
                    metadatas=chunk_metadatas,
                    documents=chunk_texts,
                )

                logger.info(
                    f"Added {len(chunk_ids)} chunks to global knowledge base from {source_name or file_path}"
                )
                return True
            else:
                logger.warning("No content chunks generated from the document")
                return False

        except Exception as e:
            logger.error(f"Error adding global knowledge: {str(e)}")
            return False

    def search_global_knowledge(
        self,
        query: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Search the global knowledge base using semantic similarity

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Simple filter - just search all global knowledge
            where_filter = {"type": "global_knowledge"}

            # Search in global knowledge collection
            results = self.global_knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=["metadatas", "documents", "distances"],
            )

            # Format results
            formatted_results = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append(
                        {
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "similarity": 1
                            - results["distances"][0][
                                i
                            ],  # Convert distance to similarity
                        }
                    )

            # Sort by similarity
            formatted_results.sort(key=lambda x: x["similarity"], reverse=True)

            logger.info(
                f"Global knowledge search returned {len(formatted_results)} results"
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching global knowledge: {str(e)}")
            return []

    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """Flatten nested metadata dictionaries for ChromaDB compatibility"""
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    flattened_key = f"{key}_{nested_key}"
                    if isinstance(nested_value, (str, int, float, bool)):
                        flattened[flattened_key] = nested_value
                    else:
                        flattened[flattened_key] = str(nested_value)
            elif isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            else:
                flattened[key] = str(value)
        return flattened

    def list_global_knowledge(self) -> List[Dict[str, Any]]:
        """
        Get a list of all documents in the global knowledge base

        Returns:
            List of documents with their metadata
        """
        try:
            # Get all documents from the global knowledge collection
            results = self.global_knowledge_collection.get(
                include=["metadatas", "documents"]
            )

            if not results or not results.get("ids"):
                return []

            # Group by source to get document summaries
            documents_by_source = {}

            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                content = results["documents"][i]
                source = metadata.get("source", "Unknown")

                if source not in documents_by_source:
                    documents_by_source[source] = {
                        "source": source,
                        "content_type": metadata.get("content_type"),
                        "added_date": metadata.get("added_date"),
                        "chunk_count": 0,
                        "sample_content": (
                            content[:200] + "..."
                            if len(content) > 200
                            else content
                        ),
                    }

                documents_by_source[source]["chunk_count"] += 1

            # Convert to list
            documents = list(documents_by_source.values())

            logger.info(
                f"Listed {len(documents)} documents from global knowledge base"
            )
            return documents

        except Exception as e:
            logger.error(f"Error listing global knowledge: {str(e)}")
            return []

    def delete_global_knowledge_document(self, source_name: str) -> int:
        """
        Delete all chunks of a specific document from the global knowledge base

        Args:
            source_name: The source name/filename to delete

        Returns:
            Number of chunks deleted
        """
        try:
            # Get all chunks for this source
            results = self.global_knowledge_collection.get(
                where={"source": source_name}, include=["metadatas"]
            )

            if not results or not results.get("ids"):
                logger.warning(f"No documents found with source: {source_name}")
                return 0

            chunk_ids = results["ids"]

            # Delete all chunks for this document
            self.global_knowledge_collection.delete(ids=chunk_ids)

            deleted_count = len(chunk_ids)
            logger.info(
                f"Deleted {deleted_count} chunks for document: {source_name}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting global knowledge document: {str(e)}")
            return 0

    def clear_global_knowledge(self) -> int:
        """
        Clear all documents from the global knowledge base

        Returns:
            Number of chunks deleted
        """
        try:
            # Get all document IDs
            results = self.global_knowledge_collection.get(
                include=["metadatas"]
            )

            if not results or not results.get("ids"):
                logger.info("No documents to clear from global knowledge base")
                return 0

            chunk_ids = results["ids"]

            # Delete all chunks
            self.global_knowledge_collection.delete(ids=chunk_ids)

            deleted_count = len(chunk_ids)
            logger.info(
                f"Cleared all global knowledge: {deleted_count} chunks deleted"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error clearing global knowledge: {str(e)}")
            return 0
