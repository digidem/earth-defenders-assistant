# Example script to inspect ChromaDB data
import chromadb
from loguru import logger

def inspect_chroma_data(collection_name="document_chunks", limit=10): # Changed default collection and limit
    """Connects to ChromaDB and retrieves a few records from the specified collection."""
    try:
        persist_directory = "./chroma_conversation_db" # Ensure this path is correct from where you run the script
        client = chromadb.PersistentClient(path=persist_directory)
        
        logger.info(f"Attempting to get collection: {collection_name}")
        try:
            collection = client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Failed to get collection '{collection_name}'. Does it exist? Error: {e}")
            logger.info(f"Available collections: {[col.name for col in client.list_collections()]}")
            return

        collection_count = collection.count()
        logger.info(f"Collection '{collection_name}' count: {collection_count}")

        if collection_count == 0:
            logger.warning(f"No data found in the collection '{collection_name}'.")
            return

        # Get a sample of records
        results = collection.get(
            limit=limit,
            include=['metadatas', 'documents'] # Specify what data to retrieve
        )

        if not results or not results.get('ids'):
            logger.warning(f"No data retrieved from the collection '{collection_name}' with get().")
            return

        logger.info(f"Retrieved {len(results['ids'])} records from '{collection_name}':")
        for i in range(len(results['ids'])):
            print("-" * 20)
            print(f"ID: {results['ids'][i]}")
            # print(f"Document: {results['documents'][i][:200] + '...' if results['documents'][i] and len(results['documents'][i]) > 200 else results['documents'][i]}") # Print snippet of document
            print(f"Metadata: {results['metadatas'][i]}")
            # Specifically log expiration_timestamp if present
            if results['metadatas'][i] and 'expiration_timestamp' in results['metadatas'][i]:
                print(f"Expiration Timestamp: {results['metadatas'][i]['expiration_timestamp']}")
            print("-" * 20)

    except Exception as e:
        logger.error(f"Error inspecting ChromaDB: {e}", exc_info=True)

if __name__ == "__main__":
    # Run this script directly (e.g., python inspect_chroma.py)
    # Make sure to run it from the directory where ./chroma_conversation_db is located
    # or adjust the persist_directory path accordingly.
    
    # Inspect document chunks
    inspect_chroma_data(collection_name="document_chunks", limit=10)
    
    # Optionally, inspect conversation history as well
    # inspect_chroma_data(collection_name="conversation_history", limit=5)