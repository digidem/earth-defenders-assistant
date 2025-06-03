from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.tools import ConversationMemoryTool

config = ConfigLoader.get_config()

# Use a standard model for this specialized agent
model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)


def get_memory_search_agent():
    """
    Returns a specialized agent for searching conversation history.
    """
    memory_tool = ConversationMemoryTool()

    agent = CodeAgent(
        name="memory_search_agent",
        description="Specialized agent to search through past conversation history using semantic similarity.",
        tools=[memory_tool],
        model=model,
        max_steps=2,  # Limit steps as it's a focused task
    )
    return agent
