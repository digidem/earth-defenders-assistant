import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pocketbase import PocketBase
from loguru import logger

from eda_config.config import ConfigLoader

config = ConfigLoader.get_config()


class PocketBaseMemory:
    """Memory manager using PocketBase for conversation storage and retrieval"""

    def __init__(self):
        """Initialize PocketBase client with configuration"""
        try:
            self.pocketbase_url = config.databases.pocketbase.url
            self.client = PocketBase(self.pocketbase_url)

            # Authenticate as admin
            self.client.admins.auth_with_password(
                config.databases.pocketbase.admin.email,
                config.databases.pocketbase.admin.password,
            )

            logger.info(
                "PocketBaseMemory initialized and authenticated successfully"
            )
        except Exception as e:
            logger.error(f"Failed to initialize PocketBaseMemory: {str(e)}")
            raise RuntimeError(
                f"PocketBase initialization error: {str(e)}"
            ) from e

    async def get_user_by_platform_id(
        self, platform: str, platform_user_id: str
    ) -> Optional[Dict]:
        """Get user by platform and platform_user_id"""
        try:
            column_name = f"{platform.lower()}_id"
            result = self.client.collection("botUsers").get_list(
                1, 1, {f"filter": f'{column_name} = "{platform_user_id}"'}
            )

            if result.items:
                logger.info(
                    f"Found existing user for {platform}:{platform_user_id}"
                )
                return result.items[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            return None

    async def create_user(
        self,
        platform: str,
        platform_user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Dict:
        """Create a new user"""
        try:
            user_data = {
                f"{platform.lower()}_id": platform_user_id,
            }

            # Add optional fields if provided
            if name:
                user_data["name"] = name
            if email:
                user_data["email"] = email
            if phone:
                user_data["phone"] = phone

            # Create user
            user = self.client.collection("botUsers").create(user_data)
            logger.info(f"Created new user for {platform}:{platform_user_id}")

            # Create initial empty conversation history
            self.client.collection("messages").create(
                {"user_id": user.id, "content": []}
            )

            logger.info(
                f"Created initial conversation history for user {user.id}"
            )
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    async def get_conversation_history_entry(
        self, user_id: str
    ) -> Optional[Dict]:
        """Get the conversation history entry for a user"""
        try:
            result = self.client.collection("messages").get_list(
                1, 1, {"filter": f'user_id = "{user_id}"'}
            )

            if result.items:
                return result.items[0]

            # Create new entry if none exists
            entry = {"user_id": user_id, "content": []}

            created_entry = self.client.collection("messages").create(entry)
            logger.info(f"Created new conversation history for user {user_id}")
            return created_entry

        except Exception as e:
            logger.error(
                f"Error retrieving conversation history entry: {str(e)}"
            )
            return None

    async def add_message_to_history(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        platform: str = "whatsapp",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Store a message exchange in the messages collection"""
        try:
            user = await self.get_or_create_user(platform, session_id)
            history_entry = await self.get_conversation_history_entry(user.id)

            if not history_entry:
                logger.error(
                    "Failed to get or create conversation history entry"
                )
                return False

            current_time = datetime.now().isoformat()
            new_message_pair = {
                "timestamp": current_time,
                "user_message": user_message,
                "assistant_response": assistant_response,
            }

            content = history_entry.content or []
            content.append(new_message_pair)

            # Update the record
            self.client.collection("messages").update(
                history_entry.id, {"content": content}
            )

            logger.info(
                f"Added message pair to history for session {session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add message to history: {str(e)}")
            return False

    async def get_conversation_history(
        self, session_id: str, limit: int = 5
    ) -> List[Dict]:
        """Retrieve conversation history for a specific session"""
        try:
            platform_fields = [
                "whatsapp_id",
                "telegram_id",
                "website_id",
                "api_id",
            ]
            user = None

            # Try each platform field to find the user
            for field in platform_fields:
                result = self.client.collection("botUsers").get_list(
                    1, 1, {"filter": f'{field} = "{session_id}"'}
                )
                if result.items:
                    user = result.items[0]
                    break

            if not user:
                logger.warning(f"No user found for session_id: {session_id}")
                return []

            history_entry = await self.get_conversation_history_entry(user.id)

            if not history_entry or not hasattr(history_entry, "content"):
                logger.warning(
                    f"No conversation history found for user_id: {user.id}"
                )
                return []

            content = history_entry.content or []
            history_filtered = content[-limit:] if content else []

            # Log the history for debugging
            logger.debug("\n===== CONVERSATION HISTORY =====")
            for idx, pair in enumerate(history_filtered, 1):
                logger.debug(f"\nMessage Pair {idx}:")
                logger.debug(f"User: {pair.get('user_message', '')}")
                logger.debug(f"Assistant: {pair.get('assistant_response', '')}")
                logger.debug("-" * 40)
            logger.debug("==============================\n")

            return history_filtered

        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []

    async def test_connection(self) -> bool:
        """Test the PocketBase connection"""
        try:
            self.client.health.check()
            logger.info("PocketBase connection successful")
            return True
        except Exception as e:
            logger.error(f"PocketBase connection test failed: {str(e)}")
            return False

    async def get_or_create_user(
        self, platform: str, platform_user_id: str
    ) -> Dict:
        """Get existing user or create new one if not found"""
        try:
            # First try to get existing user
            existing_user = await self.get_user_by_platform_id(
                platform, platform_user_id
            )
            if existing_user:
                return existing_user

            # If not found, create new user
            new_user = await self.create_user(
                platform=platform, platform_user_id=platform_user_id
            )
            return new_user

        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}")
            raise RuntimeError(f"Failed to get or create user: {str(e)}") from e

    async def format_history_for_context(
        self, history: List[Dict]
    ) -> List[Dict]:
        """Format conversation history for the prompt context"""
        formatted_history = []
        for entry in history:
            formatted_history.append(
                {
                    "user": entry.get("user_message", ""),
                    "assistant": entry.get("assistant_response", ""),
                }
            )
        return formatted_history
