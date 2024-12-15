#!/usr/bin/env python
import os
import sys
from opportunity_finder.crew import OpportunityFinderCrew
from langtrace_python_sdk import langtrace
# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
def init_langtrace():
    """Initialize langtrace with environment variables."""
    langtrace.init(
        api_key=os.environ.get('LANGTRACE_API_KEY'),
        api_host=os.environ.get('LANGTRACE_API_HOST', 'http://localhost:3000/api/trace'),
    )

def run():
    """
    Run the crew with default topics.
    """
    init_langtrace()
    inputs = {
        'topics': 'Climate Justice, Indigenous Land Defense, Sociobiodiveristy'
    }
    OpportunityFinderCrew().crew().kickoff(inputs=inputs)

def main(topics: str):
    """
    Run the crew with specified topics.

    Args:
        topics: Comma-separated string of topics to search for opportunities
    """
    init_langtrace()
    inputs = {
        'topics': topics
    }
    return OpportunityFinderCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run src/opportunity_finder/main.py 'topic1, topic2, topic3'")
        sys.exit(1)
    main(sys.argv[1])

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'topics': 'Climate Justice, Indigenous Land Defense, Sociobiodiveristy'
    }
    try:
        OpportunityFinderCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        OpportunityFinderCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'topics': 'Climate Justice, Indigenous Land Defense, Sociobiodiveristy'
    }
    try:
        OpportunityFinderCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
