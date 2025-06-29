from typing import Dict, List, Optional
from loguru import logger

from eda_ai_api.utils.memory_manager import get_vector_memory
from eda_config.config import ConfigLoader

config = ConfigLoader.get_config()


async def build_enhanced_context(
    user_platform_id: str,
    current_message: str,
    platform: str = "whatsapp",
    recent_history_limit: int = 5,
    relevant_history_limit: int = 3,
    cross_session: bool = False,
) -> Dict:
    """
    Build an enhanced context for the AI by combining recent and semantically relevant conversation history

    Args:
        user_platform_id: User's platform ID
        current_message: The current message from the user
        platform: Platform identifier
        recent_history_limit: Number of recent conversation turns to include
        relevant_history_limit: Number of semantically relevant conversation turns to include
        cross_session: Whether to include relevant history from other sessions

    Returns:
        Dict containing context information including conversation history
    """
    try:
        memory = get_vector_memory()
        context = {}

        # Get recent sequential history
        recent_history = await memory.get_conversation_history(
            session_id=user_platform_id, limit=recent_history_limit
        )

        # Format recent history for context
        recent_formatted = await memory.format_history_for_context(
            recent_history
        )
        context["recent_history"] = recent_formatted

        # Get semantically relevant history
        relevant_history = await memory.get_relevant_history(
            session_id=user_platform_id,
            current_query=current_message,
            platform=platform,
            limit=relevant_history_limit,
            cross_session=cross_session,
        )

        # Remove duplicates from relevant history that are already in recent history
        recent_messages = set()
        for exchange in recent_formatted:
            recent_messages.add(exchange.get("user", ""))

        unique_relevant = []
        for exchange in relevant_history:
            if exchange.get("user", "") not in recent_messages:
                unique_relevant.append(exchange)

        context["relevant_history"] = unique_relevant

        # Add merged history for easy access
        merged_history = recent_formatted + unique_relevant
        context["merged_history"] = merged_history

        logger.info(
            f"Built enhanced context with {len(recent_formatted)} recent and "
            f"{len(unique_relevant)} relevant history items"
        )
        return context

    except Exception as e:
        logger.error(f"Error building enhanced context: {str(e)}")
        return {
            "recent_history": [],
            "relevant_history": [],
            "merged_history": [],
        }
