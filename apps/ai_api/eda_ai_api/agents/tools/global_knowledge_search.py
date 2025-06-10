from typing import Dict, Optional
from smolagents import Tool
from eda_ai_api.utils.vector_memory import VectorMemory


class GlobalKnowledgeSearchTool(Tool):
    """Tool for searching through global knowledge base available to all users"""

    name = "global_knowledge_search"
    description = "Searches through the global knowledge base for general information, FAQs, policies, and shared knowledge available to all users using semantic similarity"
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant information from the global knowledge base",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of relevant knowledge sections to return",
            "default": 3,
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__()
        self.memory = VectorMemory()

    def forward(
        self,
        query: str,
        limit: int = 3,
    ) -> str:
        # Search the global knowledge base (no session_id or category needed)
        results = self.memory.search_global_knowledge(
            query=query,
            limit=limit,
        )

        if not results:
            return "No relevant information found in the global knowledge base."

        # Format the results
        output = "Here is relevant information from the knowledge base:\n\n"
        for i, result in enumerate(results):
            metadata = result.get("metadata", {})
            similarity = result.get("similarity", 0)

            output += f"Knowledge {i+1}:\n"
            output += f"Content: {result.get('content', '')}\n"
            output += f"Source: {metadata.get('source', 'Unknown')}\n"
            if metadata.get("page"):
                output += f"Page: {metadata.get('page')}\n"
            output += f"Relevance: {similarity:.2f}\n\n"

        return output
