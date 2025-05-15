from fastapi import APIRouter
from onboarding.crew import OnboardingCrew
from pydantic import BaseModel


class OnboardingGuideResponse(BaseModel):
    guide: str


router = APIRouter()


@router.get("/guide", response_model=OnboardingGuideResponse, name="guide")
async def get_bot_guide() -> OnboardingGuideResponse:
    """Generate a user guide explaining how to use the Earth Defenders Assistant."""
    crew_output = OnboardingCrew().crew().kickoff()
    # Extract the raw string content from the CrewOutput object
    guide_text = str(crew_output.raw)
    return OnboardingGuideResponse(guide=guide_text)
