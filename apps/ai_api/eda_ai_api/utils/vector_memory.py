import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

from eda_config.config import ConfigLoader
from eda_ai_api.utils.memory import PocketBaseMemory

config = ConfigLoader.get_config()

class VectorMemory(PocketBaseMemory):
    """Enhanced memory manager that adds vector search capabilities for retrieving relevant conversation history"""

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

            # Create or get the collection for storing conversation embeddings
            self.collection = self.chroma_client.get_or_create_collection(
                name="conversation_history",
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )

            logger.info("VectorMemory initialized successfully with ChromaDB")
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
        """
        Store a message exchange in both PocketBase and vector database

        Args:
            session_id: User's platform ID
            user_message: Message from the user
            assistant_response: Response from the assistant
            platform: Platform identifier (whatsapp, telegram, etc.)
            metadata: Optional additional data

        Returns:
            bool: Success status
        """
        # First, store in PocketBase using parent method
        result = await super().add_message_to_history(
            session_id, user_message, assistant_response, platform, metadata
        )

        if not result:
            logger.error("Failed to add message to PocketBase")
            return False

        # Then add to vector database
        try:
            # Create combined text for embedding (user message + assistant response)
            combined_text = f"USER: {user_message}\nASSISTANT: {assistant_response}"

            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()

            # Create document ID
            doc_id = f"{platform}_{session_id}_{datetime.now().isoformat()}"

            # Prepare metadata
            doc_metadata = {
                "platform": platform,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response
            }

            # Add any additional metadata if provided
            if metadata:
                doc_metadata.update(metadata)

            # Add to ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[combined_text]
            )

            logger.info(f"Added message pair to vector database for session {session_id}")
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
        """
        Retrieve relevant conversation history based on semantic similarity

        Args:
            session_id: User's platform ID
            query: Search query text
            platform: Platform identifier
            limit: Maximum number of results to return
            filter_by_session: Whether to limit results to the current session

        Returns:
            List of relevant conversation snippets with metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepare metadata filter if filtering by session
            where_filter = None
            if filter_by_session:
                where_filter = {"session_id": session_id}

            # Execute search query
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=['metadatas', 'documents', 'distances'] # Ensure distances are included
            )

            # Format results
            formatted_results = []
            # Check if results and the necessary keys exist and are not empty
            if results and results.get('ids') and results['ids'][0]:
                num_results = len(results['ids'][0])
                for i in range(num_results):
                    result = {
                        "id": results['ids'][0][i],
                        # Ensure documents list exists and has the index
                        "text": results['documents'][0][i] if results.get('documents') and len(results['documents'][0]) > i else None,
                        # Ensure metadatas list exists and has the index
                        "metadata": results['metadatas'][0][i] if results.get('metadatas') and len(results['metadatas'][0]) > i else None,
                        # Ensure distances list exists and has the index
                        "similarity": 1 - results['distances'][0][i] if results.get('distances') and results['distances'][0] and len(results['distances'][0]) > i else None # Convert distance to similarity (assuming cosine)
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
            self.collection.delete(
                where={"session_id": session_id, "platform": platform}
            )
            logger.info(f"Cleared vector history for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector history: {str(e)}")
            return False