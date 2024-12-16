from fast_graphrag import GraphRAG
import json
from pathlib import Path
import importlib.resources as pkg_resources
import product_support

DOMAIN = "Analyze product documentation to understand features, usage patterns, technical capabilities, integrations, and provide accurate support responses."

# Get the directory this file is in
current_dir = Path(__file__).parent

# Get plugin root, handling both direct use and package import cases
try:
    # First try going up one level from current file
    plugin_root = current_dir.parent
    qa_test_path = plugin_root / "qa.json"
    if not qa_test_path.exists():
        raise FileNotFoundError
except (FileNotFoundError, PermissionError):
    # If that fails, try to find it relative to the package installation
    plugin_root = Path(pkg_resources.files(product_support))

qa_path = plugin_root / "qa.json"
EXAMPLE_QUERIES = []

if not qa_path.exists():
    # Create empty qa.json with default structure
    default_qa = {
        "examples": []
    }
    with open(qa_path, "w") as f:
        json.dump(default_qa, f, indent=4)

try:
    with open(qa_path) as f:
        qa_data = json.load(f)
        EXAMPLE_QUERIES = [example["query"] for example in qa_data["examples"]]
except Exception as e:
    print(f"Warning: Could not load qa.json: {str(e)}")

ENTITY_TYPES = ["Feature", "Component", "User", "Action", "Platform", "Data"]
def initialize_grag():
    print("Initializing GraphRAG...")
    # Create graph directory if it doesn't exist
    graph_dir = plugin_root / "graph"
    if not graph_dir.exists():
        graph_dir.mkdir(parents=True)

    grag = GraphRAG(
        working_dir=str(graph_dir),
        domain=DOMAIN,
        example_queries="\n".join(EXAMPLE_QUERIES),
        entity_types=ENTITY_TYPES
    )

    # Read all txt files in documentation directory
    docs_dir = plugin_root / "documentation"
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documentation directory not found at {docs_dir}")
        
    for filename in docs_dir.glob("*.txt"):
        try:
            content = filename.read_text()
            print(f"Processing file: {filename.name}")
            grag.insert(content)
            print(f"Successfully inserted content from {filename.name}")
        except Exception as e:
            print(f"Error processing file {filename.name}: {str(e)}")
    return grag

def query(question: str, grag: GraphRAG = None):
    if grag is None:
        grag = initialize_grag()
    return grag.query(question).response
