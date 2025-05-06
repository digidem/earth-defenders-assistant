import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from eda_config.config import ConfigLoader
from eda_ai_api.utils.memory import PocketBaseMemory

config = ConfigLoader.get_config()

class VectorMemory(PocketBaseMemory):
    """Enhanced memory manager for conversations and documents with TTL"""

    def __init__(self):
        """Initialize PocketBase and ChromaDB clients"""
        super().__init__()
        try:
            # Initialize embeddings model
            self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

            # Initialize ChromaDB persistent client
            persist_directory = "./chroma_conversation_db"
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"ChromaDB client initialized with persistence directory: {persist_directory}")

            # Create separate collections for conversations and documents
            self.conversation_collection = self.chroma_client.get_or_create_collection(
                name="conversation_history",
                metadata={"hnsw:space": "cosine", "type": "conversation"}
            )

            self.document_collection = self.chroma_client.get_or_create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine", "type": "document"}
            )

            # Initialize text splitter for documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
            )

            logger.info("VectorMemory initialized successfully with separate collections")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorMemory: {str(e)}")
            raise RuntimeError(f"Vector memory initialization error: {str(e)}") from e

    async def add_message_to_history(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        platform: str = "whatsapp",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Store a message exchange in both PocketBase and conversation vector database"""
        # First, store in PocketBase using parent method
        result = await super().add_message_to_history(
            session_id, user_message, assistant_response, platform, metadata
        )

        if not result:
            logger.error("Failed to add message to PocketBase")
            return False

        try:
            # Create combined text for embedding
            combined_text = f"USER: {user_message}\nASSISTANT: {assistant_response}"

            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()

            # Create document ID
            doc_id = f"{platform}_{session_id}_{datetime.now().isoformat()}"

            # Prepare metadata
            doc_metadata = {
                "type": "conversation",
                "platform": platform,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response,
                **(metadata or {})
            }

            # Add to conversation collection
            self.conversation_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[combined_text]
            )

            logger.info(f"Added message pair to conversation collection for session {session_id}")
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
        filter_by_session: bool = True
    ) -> List[Dict[str, Any]]:
        """Search conversation history using semantic similarity"""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepare metadata filter if filtering by session
            where_filter = {"$and": [{"type": "conversation"}]}
            if filter_by_session:
                where_filter["$and"].append({"session_id": session_id})

            # Execute search query on conversation collection
            results = self.conversation_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=['metadatas', 'documents', 'distances']
            )

            # Format results
            formatted_results = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "similarity": 1 - results['distances'][0][i]
                    }
                    formatted_results.append(result)

            logger.info(f"Semantic search returned {len(formatted_results)} results for {session_id}")
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
        cross_session: bool = False
    ) -> List[Dict]:
        """
        Get conversation history relevant to the current query

        Args:
            session_id: User's platform ID
            current_query: The current user message
            platform: Platform identifier
            limit: Maximum number of relevant items to return
            cross_session: Whether to search across all sessions

        Returns:
            List of relevant conversation exchanges in formatted context
        """
        try:
            # Get semantically relevant conversation snippets
            relevant_items = await self.semantic_search(
                session_id=session_id,
                query=current_query,
                platform=platform,
                limit=limit,
                filter_by_session=not cross_session
            )

            # Format for context
            formatted_history = []
            for item in relevant_items:
                metadata = item.get("metadata") # Use .get for safety
                if metadata: # Check if metadata exists
                    formatted_history.append({
                        "user": metadata.get("user_message", ""),
                        "assistant": metadata.get("assistant_response", ""),
                        "timestamp": metadata.get("timestamp", ""),
                        "relevance": item.get("similarity") # Use the calculated similarity
                    })

            # Sort by relevance (higher similarity first)
            formatted_history.sort(key=lambda x: x.get('relevance', 0), reverse=True)

            return formatted_history

        except Exception as e:
            logger.error(f"Error retrieving relevant history: {str(e)}")
            return []

    async def clear_vector_history(self, session_id: str, platform: str = "whatsapp") -> bool:
        """
        Remove all vectorized conversation history for a specific session

        Args:
            session_id: User's platform ID
            platform: Platform identifier

        Returns:
            bool: Success status
        """
        try:
            self.conversation_collection.delete(
                where={"session_id": session_id, "platform": platform}
            )
            logger.info(f"Cleared vector history for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector history: {str(e)}")
            return False

    async def add_pdf_document(
        self,
        pdf_path: str,
        ttl_days: int = 30,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Process and store PDF document with TTL in document collection"""
        try:
            # Read PDF
            pdf = PdfReader(pdf_path)
            
            # Extract text from each page
            texts = []
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text.strip():
                    texts.append({
                        'content': text,
                        'page': page_num + 1
                    })

            # Split texts into chunks
            all_chunks = []
            for text_item in texts:
                chunks = self.text_splitter.split_text(text_item['content'])
                for chunk in chunks:
                    all_chunks.append({
                        'content': chunk,
                        'page': text_item['page']
                    })

            # Calculate expiration timestamp
            expiration_date = datetime.now() + timedelta(days=ttl_days)
            
            # Prepare document chunks for storage
            chunk_ids = []
            chunk_texts = []
            chunk_embeddings = []
            chunk_metadata = []
            
            for chunk in all_chunks:
                chunk_id = f"pdf_{pdf_path}_{chunk['page']}_{datetime.now().isoformat()}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk['content'])
                
                # Generate embedding
                embedding = self.embedding_model.encode(chunk['content']).tolist()
                chunk_embeddings.append(embedding)
                
                # Prepare metadata
                chunk_metadata.append({
                    "type": "document",
                    "document_type": "pdf",
                    "page": chunk['page'],
                    "source": pdf_path,
                    "expiration_date": expiration_date.isoformat(),
                    **(metadata or {})
                })

            # Store in document collection
            self.document_collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                embeddings=chunk_embeddings,
                metadatas=chunk_metadata
            )

            logger.info(f"Added PDF document with {len(chunk_ids)} chunks and {ttl_days} days TTL")
            return True

        except Exception as e:
            logger.error(f"Error adding PDF document: {str(e)}")
            return False

    def search_documents(
        self,
        query: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Search document chunks with TTL filtering"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Current timestamp for TTL checking
            current_time = datetime.now().isoformat()
            
            # Search in document collection with TTL filter
            results = self.document_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # Get extra results in case some are expired
                where={
                    "$and": [
                        {"type": "document"},
                        {"expiration_date": {"$gt": current_time}}
                    ]
                },
                include=['metadatas', 'documents', 'distances']
            )

            # Format and filter results
            formatted_results = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    similarity = 1 - results['distances'][0][i]
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': similarity
                    }
                    formatted_results.append(result)

            # Sort by similarity and limit results
            formatted_results.sort(key=lambda x: x['similarity'], reverse=True)
            return formatted_results[:limit]

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    async def cleanup_expired_documents(self) -> int:
        """Remove expired document chunks from document collection"""
        try:
            current_time_iso = datetime.now().isoformat()
            logger.info(f"Running cleanup for documents expired before: {current_time_iso}")

            all_docs = self.document_collection.get(
                include=["metadatas"] # Only need metadatas to check expiration
            )

            expired_ids = []
            if all_docs and all_docs['ids']:
                for i in range(len(all_docs['ids'])):
                    doc_id = all_docs['ids'][i]
                    metadata = all_docs['metadatas'][i]
                    # Use 'expiration_date' as per your inspect_chroma.py output
                    if metadata and 'expiration_date' in metadata:
                        expiration_date_str = metadata['expiration_date']
                        # Ensure consistent ISO format for comparison
                        if expiration_date_str < current_time_iso:
                            expired_ids.append(doc_id)
                    elif metadata and metadata.get('type') == 'document': # Check type to ensure it's a document chunk
                        logger.warning(f"Document chunk {doc_id} is missing 'expiration_date' in metadata.")


            if expired_ids:
                logger.info(f"Found {len(expired_ids)} expired document chunks to delete.")
                self.document_collection.delete(ids=expired_ids)
                logger.info(f"Successfully deleted {len(expired_ids)} expired document chunks.")
                return len(expired_ids)
            else:
                logger.info("No expired document chunks found to delete.")
                return 0

        except Exception as e:
            logger.error(f"Error during cleanup of expired documents: {str(e)}", exc_info=True)
            return 0