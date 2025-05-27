from typing import Dict, List, Optional
from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.document_search_agent import get_document_search_agent
from eda_ai_api.agents.memory_search_agent import get_memory_search_agent
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines

config = ConfigLoader.get_config()

# Manager agent model (can be premium as before)
manager_model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)


def get_agent(platform: str = "whatsapp", variables: Optional[Dict] = None):
    """
    Returns the manager agent configured with specialized sub-agents.

    Args:
        platform: The platform name (e.g., "whatsapp", "telegram")
        variables: Optional variables to pass to the agent

    Returns:
        CodeAgent: The configured manager agent
    """
    if variables is None:
        variables = {}

    # Initialize specialized agents
    doc_agent = get_document_search_agent()
    mem_agent = get_memory_search_agent()

    # Create the manager agent, providing the specialized agents
    manager_agent = CodeAgent(
        tools=[],
        managed_agents=[
            doc_agent,
            mem_agent,
        ],  # List of agents it can delegate to
        model=manager_model,
        max_steps=5,  # Increase steps slightly to allow for delegation
    )

    # Apply conversation history limit from config (passed to prompt template)
    history_limit = config.services.ai_api.conversation_history_limit
    variables["conversation_history_limit"] = history_limit

    return manager_agent
