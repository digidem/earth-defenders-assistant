from src.main import initialize_grag, query

def main():
    print("Welcome to Product Support Assistant!")
    print("Ask questions about the product. Type 'exit' or 'quit' to end the session.")
    
    # Initialize the GraphRAG once
    grag = initialize_grag()
    
    while True:
        question = input("\nYour question: ").strip()
        
        if question.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if not question:
            print("Please enter a valid question.")
            continue
            
        try:
            response = query(question, grag)
            print("\nAnswer:", response)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
