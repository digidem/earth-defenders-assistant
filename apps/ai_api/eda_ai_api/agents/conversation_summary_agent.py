from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.tools import (
    ConversationHistoryTool,
    GlobalKnowledgeSearchTool,
    ConversationMemoryTool,
    DocumentSearchTool,  # <-- Add this import
)

config = ConfigLoader.get_config()

# Use a standard model for this specialized agent
model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)

def get_conversation_summary_agent(session_id: str, platform: str = "whatsapp"):
    """
    Returns a specialized agent for generating short summaries of the user's conversation.
    The agent has access to:
      - ConversationHistoryTool (for retrieving conversation history by date)
      - GlobalKnowledgeSearchTool (for referencing global knowledge)
      - ConversationMemoryTool (for semantic search in user's memory)
      - DocumentSearchTool (for searching stored documents)
    Args:
        session_id: User's session/platform ID
        platform: Platform identifier (e.g., 'whatsapp')
    """
    tools = [
        ConversationHistoryTool(session_id=session_id),
        GlobalKnowledgeSearchTool(),
        ConversationMemoryTool(session_id=session_id, platform=platform),
        DocumentSearchTool(session_id=session_id, platform=platform),  # <-- Add this line
    ]

    agent = CodeAgent(
        name="conversation_summary_agent",
        description="Agent specialized in creating short summaries about the user's conversation. "
                    "It can retrieve conversation history by date, search global knowledge, perform semantic memory search, and search documents.",
        tools=tools,
        model=model,
        max_steps=3,
    )
    return agent