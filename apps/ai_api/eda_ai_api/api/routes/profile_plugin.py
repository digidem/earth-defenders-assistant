from fastapi import APIRouter
from profile_plugin.crew import ProfilePluginCrew
from pydantic import BaseModel


class ProfilePluginResponse(BaseModel):
    guide: str


router = APIRouter()


@router.get("/guide", response_model=ProfilePluginResponse, name="guide")
async def get_bot_guide() -> ProfilePluginResponse:
    """Generate a user guide explaining how to use the Earth Defenders Assistant."""
    crew_output = ProfilePluginCrew().crew().kickoff()
    # Extract the raw string content from the CrewOutput object
    guide_text = str(crew_output.raw)
    return ProfilePluginResponse(guide=guide_text)
