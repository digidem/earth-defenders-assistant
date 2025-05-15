from pydantic import BaseModel


class OnboardingResponse(BaseModel):
    """Response model for onboarding explanations"""

    explanation: str


class OnboardingRequest(BaseModel):
    """Request model for onboarding queries"""

    topic: str | None = None
