#!/usr/bin/env python
import sys
from profile_plugin.crew import ProfilePluginCrew

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Single mock profile for testing
MOCK_PROFILE = {
    "userId": "051991233224",
    "biome": "Tropical Rainforest",
    "ethnicGroup": "",
    "territory": "Amazonas, Brazil",
    "community": "",
}

def run():
    """
    Run the crew to analyze the mock profile.
    """
    crew = ProfilePluginCrew(mock_profile=MOCK_PROFILE)
    crew.crew().kickoff()

if __name__ == "__main__":
    run()
