# Example script to inspect ChromaDB data
import chromadb
from loguru import logger

def inspect_chroma_data(limit=5):
    """Connects to ChromaDB and retrieves a few records."""
    try:
        persist_directory = "./chroma_conversation_db"
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_collection(name="conversation_history")

        logger.info(f"Collection count: {collection.count()}")

        # Get a sample of records
        results = collection.get(
            limit=limit,
            include=['metadatas', 'documents'] # Specify what data to retrieve
        )

        if not results or not results.get('ids'):
            logger.warning("No data found in the collection.")
            return

        logger.info(f"Retrieved {len(results['ids'])} records:")
        for i in range(len(results['ids'])):
            print("-" * 20)
            print(f"ID: {results['ids'][i]}")
            print(f"Document: {results['documents'][i]}")
            print(f"Metadata: {results['metadatas'][i]}")
            print("-" * 20)

    except Exception as e:
        logger.error(f"Error inspecting ChromaDB: {e}")

if __name__ == "__main__":
    # Run this script directly (e.g., python inspect_chroma.py)
    # Make sure to run it from the directory where ./chroma_conversation_db is located
    # or adjust the persist_directory path accordingly.
    inspect_chroma_data(limit=5)