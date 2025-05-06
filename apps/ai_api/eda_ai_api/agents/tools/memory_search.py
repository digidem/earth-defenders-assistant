from typing import Dict
from smolagents import Tool
from eda_ai_api.utils.vector_memory import VectorMemory

class ConversationMemoryTool(Tool):
    """Tool for searching conversation history using semantic similarity"""
    
    name = "memory_search"
    description = "Uses semantic search to find relevant past conversations from long-term memory (beyond recent context)"
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant conversation history"
        },
        "limit": {
            "type": "integer", 
            "description": "Maximum number of relevant conversations to return",
            "default": 3,
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()
        self.memory = VectorMemory()

    def forward(self, query: str, limit: int = 3) -> str:
        # Search in conversation collection
        relevant_history = self.memory.conversation_collection.query(
            query_embeddings=[self.memory.embedding_model.encode(query).tolist()],
            n_results=limit,
            include=['metadatas', 'documents', 'distances']
        )

        if not relevant_history or not relevant_history.get('ids') or not relevant_history['ids'][0]:
            return "No relevant conversation history found."

        # Format the results
        output = "Here are the most relevant past conversations:\n\n"
        for i in range(len(relevant_history['ids'][0])):
            metadata = relevant_history['metadatas'][0][i]
            similarity = 1 - relevant_history['distances'][0][i]
            
            output += f"Conversation {i+1}:\n"
            output += f"User: {metadata.get('user_message', '')}\n"
            output += f"Assistant: {metadata.get('assistant_response', '')}\n"
            output += f"Relevance: {similarity:.2f}\n\n"

        return output