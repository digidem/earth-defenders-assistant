from typing import Dict, List, Optional

from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader

from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines

config = ConfigLoader.get_config()

# Create the model instance using settings from config
model = LiteLLMModel(
    model_id=f"{config.ai_models['premium'].provider}/{config.ai_models['premium'].model}",
    api_key=config.api_keys.openrouter,
    temperature=config.ai_models["premium"].temperature,
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

    # Create a manager agent with the necessary tools
    # You can add your specific tools here as needed
    manager_agent = CodeAgent(
        tools=[],  # Add your tools here
        model=model,
        max_steps=3,
    )

    return manager_agent
