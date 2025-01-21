#!/usr/bin/env python
import os
import sys
import json
from eda_config import ConfigLoader
from proposal_writer.crew import ProposalWriterCrew
from langtrace_python_sdk import langtrace

# Get config
config = ConfigLoader.get_config()

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    langtrace.init(api_key=config.api_keys.langtrace)
    print("Running the ProposalWriterCrew")
    with open("tests/project_example_cache.json", "r", encoding="utf-8") as f:
        project = json.loads(f.read())
    with open("tests/teia.json", "r", encoding="utf-8") as f:
        grant = json.loads(f.read())
    inputs = [
        {
            "community_project": project,  # Details about the community project/initiative
            "grant_call": grant,  # Information about the grant/funding opportunity
        }
    ]
    print("inputs:", inputs)
    crew = ProposalWriterCrew(community_project=project, grant_call=grant)
    crew.crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        ProposalWriterCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ProposalWriterCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        ProposalWriterCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
