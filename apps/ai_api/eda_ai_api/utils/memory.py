import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from loguru import logger
from supabase import create_client, Client as SupabaseClient

from eda_config.config import ConfigLoader
from eda_ai_api.models.message_handler import MessageHistory

config = ConfigLoader.get_config()


class SupabaseMemory:
    """Memory manager using Supabase for conversation storage and retrieval"""

    def __init__(self):
        """Initialize Supabase client with configuration"""
        try:
            self.supabase_url = config.databases.supabase.url
            self.supabase_key = config.api_keys.supabase.service_key

            # Fix: Use proper initialization without extra parameters
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("SupabaseMemory initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SupabaseMemory: {str(e)}")
            raise RuntimeError(
                f"Supabase initialization error: {str(e)}"
            ) from e

    async def get_user(
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
        full_name: Optional[str] = None,
        email: Optional[str] = None,
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
            if full_name:
                user_data["full_name"] = full_name
            if email:
                user_data["email"] = email

            response = self.client.table("users").insert(user_data).execute()
            logger.info(f"Created new user for {platform}:{platform_user_id}")

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
        full_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict:
        """
        Get existing user or create a new user record.
        Uses platform-specific ID fields (whatsapp_id, telegram_id, etc.)
        """
        try:
            # Try to find existing user
            user = await self.get_user(platform, platform_user_id)

            if user:
                return user

            # Create new user if not found
            return await self.create_user(
                platform, platform_user_id, full_name, email
            )
        except Exception as e:
            logger.error(f"Failed to get/create user: {str(e)}")
            raise

    async def add_message_to_history(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        platform: str = "whatsapp",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Store a message exchange in the messages table using JSONB content"""
        try:
            # First get or create a user based on session_id (as platform_user_id)
            user = await self.get_or_create_user(platform, session_id)
            user_id = user["id"]

            # Current timestamp
            current_time = datetime.now().isoformat()

            # Create user message entry
            user_message_entry = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": {
                    "type": "user_message",
                    "text": user_message,
                    "session_id": session_id,
                    "platform": platform,
                    "metadata": metadata or {},
                },
                "created_at": current_time,
                "updated_at": current_time,
            }

            # Create assistant response entry
            assistant_message_entry = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": {
                    "type": "assistant_response",
                    "text": assistant_response,
                    "session_id": session_id,
                    "platform": platform,
                    "metadata": metadata or {},
                },
                "created_at": current_time,
                "updated_at": current_time,
            }

            # Insert both messages
            self.client.table("messages").insert(
                [user_message_entry, assistant_message_entry]
            ).execute()

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
        Formats messages from JSONB content in the messages table
        """
        try:
            # First, find users with the session_id in any platform field
            platform_fields = [
                "whatsapp_id",
                "telegram_id",
                "website_id",
                "api_id",
            ]
            user = None

            # Try each platform field
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

            # Query conversation history from messages table
            # Filter by content->session_id using Supabase filter syntax
            response = (
                self.client.table("messages")
                .select("*")
                .eq("user_id", user_id)
                .filter("content->>session_id", "eq", session_id)
                .order("created_at", desc=True)
                .limit(limit * 2)  # Get twice the limit to pair messages
                .execute()
            )

            messages = response.data
            logger.info(
                f"Retrieved {len(messages)} messages for session {session_id}"
            )

            # Group messages into user-assistant pairs
            user_messages = {}
            assistant_responses = {}

            for msg in messages:
                content = msg.get("content", {})
                msg_type = content.get("type")
                text = content.get("text", "")
                created_at = msg.get("created_at")

                if msg_type == "user_message":
                    user_messages[created_at] = text
                elif msg_type == "assistant_response":
                    assistant_responses[created_at] = text

            # Match messages into pairs
            pairs = []

            # Sort timestamps for better matching
            user_times = sorted(user_messages.keys(), reverse=True)
            asst_times = sorted(assistant_responses.keys(), reverse=True)

            # Create pairs based on available messages
            # This is simplified - in a real system you might want a more robust pairing logic
            for i in range(min(len(user_times), len(asst_times), limit)):
                user_time = user_times[i]
                asst_time = asst_times[i]

                pairs.append(
                    {
                        "user_message": user_messages[user_time],
                        "assistant_response": assistant_responses[asst_time],
                        "timestamp": user_time,
                    }
                )

            # Log the history for debugging
            logger.debug("\n===== CONVERSATION HISTORY =====")
            for idx, pair in enumerate(pairs, 1):
                logger.debug(f"\nMessage Pair {idx}:")
                logger.debug(f"User: {pair['user_message']}")
                logger.debug(f"Assistant: {pair['assistant_response']}")
                logger.debug("-" * 40)
            logger.debug("==============================\n")

            return pairs
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
            logger.info(f"Supabase connection successful - found data")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
