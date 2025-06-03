from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.tools import DocumentSearchTool

config = ConfigLoader.get_config()

# Use a standard model for this specialized agent
model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)


def get_document_search_agent():
    """
    Returns a specialized agent for searching documents.
    """
    document_tool = DocumentSearchTool()

    agent = CodeAgent(
        name="document_search_agent",
        description="Specialized agent to search through stored PDF documents based on a query.",
        tools=[document_tool],
        model=model,
        max_steps=2,  # Limit steps as it's a focused task
    )
    return agent
