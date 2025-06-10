from smolagents import CodeAgent, LiteLLMModel
from eda_config.config import ConfigLoader
from eda_ai_api.agents.tools import GlobalKnowledgeSearchTool

config = ConfigLoader.get_config()

# Use a standard model for this specialized agent
model = LiteLLMModel(
    model_id=f"{config.ai_models['standard'].provider}/{config.ai_models['standard'].model}",
    api_key=config.api_keys.google_ai_studio,
    temperature=config.ai_models["standard"].temperature,
)


def get_global_knowledge_agent():
    """
    Returns a specialized agent for searching the global knowledge base.
    This agent doesn't need user context since it searches global knowledge.
    """
    # Initialize tool (no user context needed)
    knowledge_tool = GlobalKnowledgeSearchTool()

    agent = CodeAgent(
        name="global_knowledge_agent",
        description="Specialized agent to search through the global knowledge base for general information, FAQs, and policies.",
        tools=[knowledge_tool],
        model=model,
        max_steps=2,  # Limit steps as it's a focused task
    )
    return agent
