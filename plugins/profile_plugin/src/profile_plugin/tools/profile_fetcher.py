from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any

class ProfileFetcherTool(BaseTool):
    name: str = "Profile Fetcher"
    description: str = "Fetches user profiles from the Trigger.dev API"

    def _run(self, user_id: str) -> Dict[Any, Any]:
        # Reference the task ID from get-profiles.ts
        trigger_api_url = "https://api.trigger.dev"
        trigger_api_key = os.environ.get("TRIGGER_API_KEY")
        project_id = os.environ.get("TRIGGER_PROJECT_ID")
        
        try:
            # Call the get-profiles task
            response = requests.post(
                f"{trigger_api_url}/api/v1/projects/{project_id}/jobs/get-profiles/run",
                headers={
                    "Authorization": f"Bearer {trigger_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "userId": user_id
                },
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                print(f"API Error: {data.get('error', 'Unknown error')}")
                return None
                
            profiles = data.get("profiles", [])
            if not profiles:
                print("No profiles found")
                return None
                
            return profiles[0]
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Trigger.dev: {str(e)}")
            print(f"URL: {trigger_api_url}")
            print(f"Project ID: {project_id}")
            return None 