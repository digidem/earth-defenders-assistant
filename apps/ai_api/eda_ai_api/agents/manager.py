from typing import Dict, List, Optional
from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.document_search_agent import get_document_search_agent
from eda_ai_api.agents.memory_search_agent import get_memory_search_agent
from eda_ai_api.agents.global_knowledge_agent import get_global_knowledge_agent
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines

config = ConfigLoader.get_config()

# Use a vision-capable model for the manager (since it needs to process images)
manager_model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)


def get_agent(
    platform: str = "whatsapp",
    session_id: str = None,
    variables: Optional[Dict] = None,
):
    """
    Returns the manager agent configured with specialized sub-agents.

    Args:
        platform: The platform name (e.g., "whatsapp", "telegram")
        session_id: User's session/platform ID for scoping tools
        variables: Optional variables to pass to the agent

    Returns:
        CodeAgent: The configured manager agent
    """
    if variables is None:
        variables = {}

    if not session_id:
        raise ValueError(
            "session_id is required to initialize user-specific agents"
        )

    # Initialize specialized agents with user context
    doc_agent = get_document_search_agent(
        session_id=session_id, platform=platform
    )
    mem_agent = get_memory_search_agent(
        session_id=session_id, platform=platform
    )

    # Initialize global knowledge agent (no user context needed)
    global_knowledge_agent = get_global_knowledge_agent()

    # Create the manager agent with vision capabilities
    manager_agent = CodeAgent(
        tools=[],
        managed_agents=[
            doc_agent,
            mem_agent,
            global_knowledge_agent,  # Add the global knowledge agent
        ],
        model=manager_model,  # Vision-capable model
        max_steps=5,
    )

    # Apply conversation history limit from config (passed to prompt template)
    history_limit = config.services.ai_api.conversation_history_limit
    variables["conversation_history_limit"] = history_limit

    return manager_agent
