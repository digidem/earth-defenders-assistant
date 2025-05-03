from typing import Dict, List, Optional

from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.tools import ConversationMemoryTool
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines

config = ConfigLoader.get_config()

# Create the model instance using settings from config
model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.groq,
    temperature=config.ai_models["standard"].temperature,
)

def get_agent(platform: str = "whatsapp", variables: Optional[Dict] = None):
    """
    Returns the manager agent to be used by the API.

    Args:
        platform: The platform name (e.g., "whatsapp", "telegram")
        variables: Optional variables to pass to the agent

    Returns:
        CodeAgent: The configured manager agent with appropriate formatting
    """
    if variables is None:
        variables = {}

    # Initialize tools
    memory_tool = ConversationMemoryTool()

    # Create a manager agent with the tools
    manager_agent = CodeAgent(
        tools=[memory_tool],  # Add memory search tool
        model=model,
        max_steps=3,
    )

    # Apply conversation history limit from config
    history_limit = config.services.ai_api.conversation_history_limit
    variables["conversation_history_limit"] = history_limit

    return manager_agent
