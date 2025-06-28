from typing import List, Dict, Optional
from loguru import logger
from smolagents import Tool
from eda_ai_api.utils.memory import PocketBaseMemory
from datetime import datetime
import asyncio

class ConversationHistoryTool(Tool):
    """
    Tool for retrieving conversation history from PocketBase messages table within a specific date range.
    Filters by the user's session_id provided at initialization.
    """

    name = "conversation_history"
    description = (
        "Retrieves all conversation messages for the current user from PocketBase "
        "between start_date and end_date. Dates must be YYYY-MM-DD."
    )
    inputs = {
        "start_date": {
            "type": "string",
            "description": "Start date in YYYY-MM-DD format.",
        },
        "end_date": {
            "type": "string",
            "description": "End date in YYYY-MM-DD format.",
        },
    }
    output_type = "string"

    def __init__(self, session_id: str):
        super().__init__()
        self.memory = PocketBaseMemory()
        self.session_id = session_id

    def _parse_date(self, date_str: str) -> str:
        """Ensure date is in YYYY-MM-DD format and return as string."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            raise ValueError("Date must be in YYYY-MM-DD format.")

    def _get_user_id(self) -> Optional[str]:
        """Find the user_id in botUsers for the current session_id."""
        platform_fields = ["whatsapp_id", "telegram_id", "website_id", "api_id"]
        for field in platform_fields:
            result = self.memory.client.collection("botUsers").get_list(
                1, 1, {"filter": f'{field} = "{self.session_id}"'}
            )
            if result.items:
                return result.items[0].id
        return None

    def _get_conversation_history(self, start_date: str, end_date: str) -> List[Dict]:
        user_id = self._get_user_id()
        if not user_id:
            return []

        # Build date filter (inclusive)
        filter_str = (
            f'user_id = "{user_id}" && created >= "{start_date}" && created <= "{end_date} 23:59:59"'
        )

        messages = self.memory.client.collection("messages").get_list(
            1, 500, {"filter": filter_str, "sort": "created"}
        )

        history = []
        for msg in messages.items:
            content = msg.content or []
            for entry in content:
                # Only include entries whose timestamp is within the date range
                ts = entry.get("timestamp")
                if ts:
                    ts_date = ts[:10]
                    if start_date <= ts_date <= end_date:
                        history.append({
                            "timestamp": ts,
                            "user_message": entry.get("user_message", ""),
                            "assistant_response": entry.get("assistant_response", ""),
                        })
        logger.debug(f"Retrieved {len(history)} messages from {start_date} to {end_date}.")
        logger.debug(f"Conversation history: {history}")
        return history

    def forward(self, start_date: str, end_date: str) -> str:
        try:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date)
            if start > end:
                return "Start date must be before or equal to end date."

            history = self._get_conversation_history(start, end)
            if not history:
                return f"No conversation history found between {start} and {end}."

            output = f"Conversation history from {start} to {end}:\n"
            for i, entry in enumerate(history, 1):
                output += (
                    f"\n--- Message {i} ---\n"
                    f"Timestamp: {entry['timestamp']}\n"
                    f"User: {entry['user_message']}\n"
                    f"Assistant: {entry['assistant_response']}\n"
                )
            return output

        except Exception as e:
            return f"Error retrieving conversation history: {str(e)}"