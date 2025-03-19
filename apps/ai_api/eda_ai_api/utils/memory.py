import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from loguru import logger
from supabase import create_client

from eda_config.config import ConfigLoader

config = ConfigLoader.get_config()


class SupabaseMemory:
    """Memory manager using Supabase for conversation storage and retrieval"""

    def __init__(self):
        """Initialize Supabase client with configuration"""
        try:
            self.supabase_url = config.databases.supabase.url
            self.supabase_key = config.api_keys.supabase.service_key

            # Initialize Supabase client
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("SupabaseMemory initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SupabaseMemory: {str(e)}")
            raise RuntimeError(
                f"Supabase initialization error: {str(e)}"
            ) from e

    async def get_user_by_platform_id(
        self, platform: str, platform_user_id: str
    ) -> Optional[Dict]:
        """Get user by platform and platform_user_id"""
        try:
            # Choose the appropriate ID field based on platform
            column_name = f"{platform.lower()}_id"

            response = (
                self.client.table("users")
                .select("*")
                .eq(column_name, platform_user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                logger.info(
                    f"Found existing user for {platform}:{platform_user_id}"
                )
                return response.data[0]
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
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                f"{platform.lower()}_id": platform_user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # Add optional fields if provided
            if name:
                user_data["name"] = name
            if email:
                user_data["email"] = email
            if phone:
                user_data["phone"] = phone

            response = self.client.table("users").insert(user_data).execute()
            logger.info(f"Created new user for {platform}:{platform_user_id}")

            # Create an initial empty conversation history entry
            # The content field is now directly an empty array
            self.client.table("messages").insert(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "content": [],  # Direct array instead of nested object
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ).execute()

            logger.info(
                f"Created initial conversation history for user {user_id}"
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            raise Exception("User creation failed - no data returned")
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    async def get_or_create_user(
        self,
        platform: str,
        platform_user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Dict:
        """
        Get existing user or create a new user record.
        Uses platform-specific ID fields (whatsapp_id, telegram_id, etc.)
        """
        try:
            # Try to find existing user
            user = await self.get_user_by_platform_id(
                platform, platform_user_id
            )

            if user:
                return user

            # Create new user if not found
            return await self.create_user(
                platform, platform_user_id, name, email, phone
            )
        except Exception as e:
            logger.error(f"Failed to get/create user: {str(e)}")
            raise

    async def get_conversation_history_entry(
        self, user_id: str
    ) -> Optional[Dict]:
        """Get the conversation history entry for a user"""
        try:
            response = (
                self.client.table("messages")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                # Return the first entry (should be only one per user)
                return response.data[0]

            # If no entry exists, create an empty one
            entry = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": [],  # Direct array instead of nested object
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            self.client.table("messages").insert(entry).execute()
            logger.info(f"Created new conversation history for user {user_id}")

            return entry
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
        metadata: Optional[Dict] = None,  # We'll ignore this parameter
    ) -> bool:
        """Store a message exchange in the messages table as part of the JSONB content"""
        try:
            # First get or create a user based on session_id (as platform_user_id)
            user = await self.get_or_create_user(platform, session_id)
            user_id = user["id"]

            # Get the conversation history entry
            history_entry = await self.get_conversation_history_entry(user_id)

            if not history_entry:
                logger.error(
                    "Failed to get or create conversation history entry"
                )
                return False

            # Current timestamp in ISO format (compatible with timestamptz)
            current_time = datetime.now().isoformat()

            # Create the new message pair with simplified structure
            new_message_pair = {
                "timestamp": current_time,
                "user_message": user_message,
                "assistant_response": assistant_response,
            }

            # Get current content - directly an array
            content = history_entry.get("content", [])

            # Ensure content is a list (might be null or something else if data corrupt)
            if not isinstance(content, list):
                content = []

            # Add new message pair to the content array
            content.append(new_message_pair)

            # Update the record
            self.client.table("messages").update(
                {"content": content, "updated_at": current_time}
            ).eq("id", history_entry["id"]).execute()

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
        """
        Retrieve conversation history for a specific session
        Returns the most recent 'limit' message pairs
        """
        try:
            # Find the user with the given platform ID
            platform_fields = [
                "whatsapp_id",
                "telegram_id",
                "website_id",
                "api_id",
            ]
            user = None

            # Try each platform field to find the user
            for field in platform_fields:
                response = (
                    self.client.table("users")
                    .select("id")
                    .eq(field, session_id)
                    .execute()
                )

                if response.data and len(response.data) > 0:
                    user = response.data[0]
                    break

            if not user:
                logger.warning(f"No user found for session_id: {session_id}")
                return []

            user_id = user["id"]

            # Get the conversation history entry
            history_entry = await self.get_conversation_history_entry(user_id)

            if not history_entry or "content" not in history_entry:
                logger.warning(
                    f"No conversation history found for user_id: {user_id}"
                )
                return []

            # Get the content array directly
            content = history_entry.get("content", [])

            # Ensure content is a list
            if not isinstance(content, list):
                logger.warning(f"Content is not a list for user_id: {user_id}")
                return []

            # Return the most recent 'limit' entries
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
            logger.error(
                f"Failed to get conversation history: {str(e)}", exc_info=True
            )
            return []

    async def format_history_for_context(
        self, history: List[Dict]
    ) -> List[Dict]:
        """Format conversation history for use in agent context"""
        conversation_pairs = []
        for msg_pair in history:
            conversation_pairs.append(
                {
                    "user": msg_pair.get("user_message", ""),
                    "assistant": msg_pair.get("assistant_response", ""),
                }
            )
        return conversation_pairs

    async def test_connection(self) -> bool:
        """Test the Supabase connection"""
        try:
            response = (
                self.client.table("users")
                .select("count", count="exact")
                .limit(1)
                .execute()
            )
            logger.info("Supabase connection successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
