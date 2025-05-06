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
            "description": "The search query to find relevant document sections"
        },
        "limit": {
            "type": "integer", 
            "description": "Maximum number of relevant document sections to return",
            "default": 3,
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()
        self.memory = VectorMemory()

    def forward(self, query: str, limit: int = 3) -> str:
        # Search in document collection
        relevant_docs = self.memory.document_collection.query(
            query_embeddings=[self.memory.embedding_model.encode(query).tolist()],
            n_results=limit,
            where={"type": "document"},  # Filter for document chunks only
            include=['metadatas', 'documents', 'distances']
        )

        if not relevant_docs or not relevant_docs.get('ids') or not relevant_docs['ids'][0]:
            return "No relevant document content found."

        # Format the results
        output = "Here are the most relevant document sections:\n\n"
        for i in range(len(relevant_docs['ids'][0])):
            metadata = relevant_docs['metadatas'][0][i]
            similarity = 1 - relevant_docs['distances'][0][i]
            
            output += f"Section {i+1}:\n"
            output += f"Content: {relevant_docs['documents'][0][i]}\n"
            output += f"Source: {metadata.get('source', 'Unknown')}\n"
            output += f"Page: {metadata.get('page', 'Unknown')}\n"
            output += f"Relevance: {similarity:.2f}\n\n"

        return output