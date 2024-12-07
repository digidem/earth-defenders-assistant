from pydantic import BaseModel


class ProfilePluginResponse(BaseModel):
    """Response model for onboarding explanations"""

    explanation: str


class ProfilePluginRequest(BaseModel):
    """Request model for onboarding queries"""

    topic: str | None = None
