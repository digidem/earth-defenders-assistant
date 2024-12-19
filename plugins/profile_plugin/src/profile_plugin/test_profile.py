import os
import pytest
from profile_plugin.crew import ProfilePluginCrew

def test_profile_analysis():
    # Set up environment variables for testing
    os.environ["TRIGGER_API_KEY"] = ""  # Replace with your actual test key
    os.environ["TRIGGER_API_URL"] = ""  # Update if different
    
    # Test with a real user ID
    crew = ProfilePluginCrew(user_id="")
    result = crew.crew().kickoff()
    
    # Print the result for inspection
    print("Analysis result:", result.raw)
    
    # Basic validation
    assert result.raw is not None
    assert len(result.raw) > 0

def test_profile_analysis_no_user():
    # Should raise an error when no user_id provided
    with pytest.raises(ValueError):
        crew = ProfilePluginCrew()
        crew.crew().kickoff()

if __name__ == "__main__":
    # Set up environment variables for testing
    os.environ["TRIGGER_API_KEY"] = "your-trigger-api-key"
    os.environ["GROQ_API_KEY"] = "your-groq-api-key"
    
    # Run tests
    test_profile_analysis()
    test_profile_analysis_no_user() 