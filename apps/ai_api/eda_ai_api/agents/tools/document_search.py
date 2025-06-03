from typing import Dict, Optional
from smolagents import Tool
from eda_ai_api.utils.vector_memory import VectorMemory


class DocumentSearchTool(Tool):
    """Tool for searching through stored documents using semantic similarity"""

    name = "document_search"
    description = "Searches through stored documents to find relevant information based on your query"
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant document sections",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of relevant document sections to return",
            "default": 3,
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, session_id: str, platform: str = "whatsapp"):
        super().__init__()
        self.memory = VectorMemory()
        self.session_id = session_id
        self.platform = platform

    def forward(
        self,
        query: str,
        limit: int = 3,
    ) -> str:
        # Use the injected session_id and platform automatically
        results = self.memory.search_documents(
            session_id=self.session_id,
            query=query,
            platform=self.platform,
            limit=limit,
        )

        if not results:
            return "No relevant document content found."

        # Format the results
        output = "Here are the most relevant document sections:\n\n"
        for i, result in enumerate(results):
            metadata = result.get("metadata", {})
            similarity = result.get("similarity", 0)

            output += f"Section {i+1}:\n"
            output += f"Content: {result.get('content', '')}\n"
            output += f"Source: {metadata.get('source', 'Unknown')}\n"
            output += f"Page: {metadata.get('page', 'Unknown')}\n"
            output += f"Relevance: {similarity:.2f}\n\n"

        return output
