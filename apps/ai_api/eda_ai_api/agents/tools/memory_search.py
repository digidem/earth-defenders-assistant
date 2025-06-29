from typing import Dict
from smolagents import Tool
from eda_ai_api.utils.memory_manager import get_vector_memory
import asyncio


class ConversationMemoryTool(Tool):
    """Tool for searching conversation history using semantic similarity"""

    name = "memory_search"
    description = "Uses semantic search to find relevant past conversations from long-term memory (beyond recent context)"
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant conversation history",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of relevant conversations to return",
            "default": 3,
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, session_id: str, platform: str = "whatsapp"):
        super().__init__()
        self.memory = get_vector_memory()  # Use centralized memory manager
        self.session_id = session_id
        self.platform = platform

    def forward(self, query: str, limit: int = 3) -> str:
        # Use asyncio.run to handle the async call in the synchronous context
        try:
            relevant_history = asyncio.run(
                self.memory.semantic_search(
                    session_id=self.session_id,
                    query=query,
                    platform=self.platform,
                    limit=limit,
                )
            )
        except RuntimeError as e:
            if (
                "asyncio.run() cannot be called from a running event loop"
                in str(e)
            ):
                # If we're already in an event loop, get it and run the coroutine
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a new task
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self.memory.semantic_search(
                                session_id=self.session_id,
                                query=query,
                                platform=self.platform,
                                limit=limit,
                            ),
                        )
                        relevant_history = future.result()
                else:
                    relevant_history = loop.run_until_complete(
                        self.memory.semantic_search(
                            session_id=self.session_id,
                            query=query,
                            platform=self.platform,
                            limit=limit,
                        )
                    )
            else:
                raise e

        if not relevant_history:
            return "No relevant conversation history found."

        # Format the results
        output = "Here are the most relevant past conversations:\n\n"
        for i, result in enumerate(relevant_history):
            metadata = result.get("metadata", {})
            similarity = result.get("similarity", 0)

            output += f"Conversation {i+1}:\n"
            output += f"User: {metadata.get('user_message', '')}\n"
            output += f"Assistant: {metadata.get('assistant_response', '')}\n"
            output += f"Relevance: {similarity:.2f}\n\n"

        return output
