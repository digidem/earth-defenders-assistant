from fast_graphrag import GraphRAG
import json
import os

DOMAIN = "Analyze product documentation to understand features, usage patterns, technical capabilities, integrations, and provide accurate support responses."

with open("qa.json") as f:
    qa_data = json.load(f)
    EXAMPLE_QUERIES = [example["query"] for example in qa_data["examples"]]

ENTITY_TYPES = ["Feature", "Component", "User", "Action", "Platform", "Data"]
def initialize_grag():
    print("Initializing GraphRAG...")
    # Create docs directory if it doesn't exist
    if not os.path.exists("./graph"):
        os.makedirs("./graph")

    grag = GraphRAG(
        working_dir="./graph",
        domain=DOMAIN,
        example_queries="\n".join(EXAMPLE_QUERIES),
        entity_types=ENTITY_TYPES
    )

    # Read all txt files in docs directory
    for filename in os.listdir("./documentation"):
        if filename.endswith(".txt"):
            file_path = os.path.join("./documentation", filename)
            try:
                with open(file_path) as f:
                    content = f.read()
                    print(f"Processing file: {filename}")
                    grag.insert(content)
                    print(f"Successfully inserted content from {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
    return grag

def query(question: str, grag: GraphRAG = None):
    if grag is None:
        grag = initialize_grag()
    return grag.query(question).response
