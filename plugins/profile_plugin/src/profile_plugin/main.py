#!/usr/bin/env python
import os
import sys
from profile_plugin.crew import ProfileCrew
from langtrace_python_sdk import langtrace

def init_langtrace():
    """Initialize langtrace with environment variables."""
    langtrace.init(
        api_key=os.environ.get('LANGTRACE_API_KEY'),
        api_host=os.environ.get('LANGTRACE_API_HOST', 'http://localhost:3000/api/trace'),
    )

def run():
    """
    Run the crew with sample profile data.
    """
    init_langtrace()
    
    # Sample profile data for testing
    profile_data = {
        "userId": "user123",
        "biome": "Amazon Rainforest",
        "ethnicGroup": "Guarani",
        "territory": "Terra Indígena Guarani",
        "community": "Aldeia Tekoa",
        "meta": {
            "language": "Portuguese",
            "contactPreference": "WhatsApp"
        }
    }
    
    ProfileCrew(profile_data=profile_data).crew().kickoff()

def main(profile_data: dict):
    """
    Run the crew with specified profile data.
    
    Args:
        profile_data: Dictionary containing user profile information
    """
    init_langtrace()
    return ProfileCrew(profile_data=profile_data).crew().kickoff()

def train():
    """
    Train the crew for a given number of iterations.
    """
    sample_data = {
        "userId": "test_user",
        "biome": "Test Biome",
        "ethnicGroup": "Test Group"
    }
    
    try:
        ProfileCrew(profile_data=sample_data).crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2]
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ProfileCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    sample_data = {
        "userId": "test_user",
        "biome": "Test Biome",
        "ethnicGroup": "Test Group"
    }
    
    try:
        ProfileCrew(profile_data=sample_data).crew().test(
            n_iterations=int(sys.argv[1]),
            openai_model_name=sys.argv[2]
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
