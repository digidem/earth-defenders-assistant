import uuid
from typing import Dict, List, Optional

from loguru import logger
from zep_python.client import AsyncZep
from zep_python.types import Message


class ZepConversationManager:
    def __init__(
        self, api_key: str = "abc123", base_url: str = "http://localhost:3002"
    ):
        self.client = AsyncZep(api_key=api_key, base_url=base_url, timeout=30)

    async def get_or_create_session(
        self, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> str:
        """Get existing session or create new one"""
        try:
            if session_id:
                try:
                    await self.client.memory.get(session_id=session_id)
                    return session_id
                except Exception:
                    pass

            user_id = user_id or uuid.uuid4().hex
            await self.client.user.add(
                user_id=user_id, metadata={"source": "classifier_api"}
            )

            new_session_id = uuid.uuid4().hex
            await self.client.memory.add_session(
                session_id=new_session_id, user_id=user_id
            )

            await self.client.memory.add(session_id=new_session_id, messages=[])

            return new_session_id

        except Exception as e:
            raise RuntimeError(f"Session error: {str(e)}") from e

    async def add_conversation(
        self, session_id: str, user_message: str, assistant_response: str
    ) -> None:
        """Store conversation messages"""
        await self.client.memory.add(
            session_id=session_id,
            messages=[
                Message(role_type="user", content=user_message),
                Message(role_type="assistant", content=str(assistant_response)),
            ],
        )

    async def get_conversation_history(
        self, session_id: str, limit: int = 5
    ) -> List[Dict[str, str]]:
        """Get conversation history with detailed logging"""
        memory = await self.client.memory.get(session_id=session_id)

        logger.info("\n===== CONVERSATION HISTORY =====")
        for idx, msg in enumerate(memory.messages[-limit:], 1):
            logger.info(f"\nMessage {idx}:")
            logger.info(f"Role: {msg.role_type}")
            logger.info(f"Content: {msg.content}")
            logger.info("-" * 40)
        logger.info("==============================\n")

        return [
            {"role": msg.role_type, "content": msg.content}
            for msg in memory.messages[-limit:]
        ]
