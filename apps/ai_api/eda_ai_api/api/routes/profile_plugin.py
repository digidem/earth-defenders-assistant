from fastapi import APIRouter
from profile_plugin.crew import ProfilePluginCrew
from pydantic import BaseModel


class ProfilePluginResponse(BaseModel):
    profile_analyzer: str


router = APIRouter()


@router.get("/profile", response_model=ProfilePluginResponse, name="profile")
async def get_profile_plugin() -> ProfilePluginResponse:
    """Generate a user guide explaining how to use the Earth Defenders Assistant."""
    crew_output = ProfilePluginCrew().crew().kickoff()
    # Extract the raw string content from the CrewOutput object
    profile_text = str(crew_output.raw)
    return ProfilePluginResponse(profile_analyst=profile_text)
