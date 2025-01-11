import uuid
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from eda_ai_api.models.classifier import MessageHistory
from loguru import logger
from mem0 import Memory

# Load environment variables
load_dotenv()


class Mem0ConversationManager:
    def __init__(self):
        # Validate API keys
        groq_api_key = os.getenv("GROQ_API_KEY")
        huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is not set")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        config = {
            "version": "v1.1",
            "graph_store": {
                "provider": "neo4j",
                "config": {
                    "url": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "password",
                },
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-mpnet-base-v2",
                    "api_key": huggingface_api_key,
                },
            },
            "llm": {
                "provider": "groq",
                "config": {
                    "model": "llama-3.3-70b-versatile",
                    "api_key": groq_api_key,
                    "max_tokens": 1000,
                },
            },
        }
        self.memory = Memory.from_config(config_dict=config)

    async def get_or_create_session(
        self, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> str:
        """Get existing session or create new one"""
        try:
            if not user_id:
                user_id = uuid.uuid4().hex

            if session_id:
                # Check if session exists by trying to get memories
                memories = self.memory.get_all(user_id=session_id)
                if memories:
                    logger.info(f"Found existing session: {session_id}")
                    return session_id

            # Create new session
            new_session_id = session_id or uuid.uuid4().hex
            # Add initial empty memory to establish session
            self.memory.add(
                "Session started",
                user_id=new_session_id,
                metadata={"type": "session_start", "original_user": user_id},
            )
            logger.info(f"Created new session: {new_session_id}")
            return new_session_id

        except Exception as e:
            raise RuntimeError(f"Session error: {str(e)}") from e

    async def add_conversation(
        self, session_id: str, user_message: str, assistant_response: str
    ) -> None:
        """Store conversation messages"""
        try:
            # Add user message
            self.memory.add(
                user_message,
                user_id=session_id,
                metadata={"role": "user", "timestamp": uuid.uuid1().hex},
            )

            # Add assistant response
            self.memory.add(
                assistant_response,
                user_id=session_id,
                metadata={"role": "assistant", "timestamp": uuid.uuid1().hex},
            )
        except Exception as e:
            logger.error(f"Failed to add conversation: {str(e)}")
            raise

    async def get_conversation_history(
        self, session_id: str, limit: int = 5
    ) -> List[Dict[str, str]]:
        """Get conversation history with detailed logging"""
        try:
            # Get all memories for the session
            memories = self.memory.get_all(user_id=session_id)

            # Sort by timestamp and limit
            sorted_memories = sorted(
                memories, key=lambda x: x.metadata.get("timestamp", "0"), reverse=True
            )[:limit]

            # Format for consistency with previous implementation
            history = [
                {"role": memory.metadata["role"], "content": memory.text}
                for memory in sorted_memories
            ]

            # Log the history
            logger.info("\n===== CONVERSATION HISTORY =====")
            for idx, msg in enumerate(history, 1):
                logger.info(f"\nMessage {idx}:")
                logger.info(f"Role: {msg['role']}")
                logger.info(f"Content: {msg['content']}")
                logger.info("-" * 40)
            logger.info("==============================\n")

            return history

        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []


class SupabaseMemory:
    """Simple memory manager using Supabase for short-term storage"""

    @staticmethod
    def format_history(history: List[MessageHistory]) -> str:
        """Format conversation history for context"""
        if not history:
            return ""
        formatted_messages = [msg.to_context_format() for msg in history[-5:]]
        return "\n\n".join(formatted_messages)
