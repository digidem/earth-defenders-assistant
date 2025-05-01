from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel


class MessageHistory(BaseModel):
    human: str
    ai: str
    timestamp: str

    def to_context_format(self) -> str:
        return f"Human: {self.human}\nAssistant: {self.ai}"


class MessageHandlerRequest(BaseModel):
    message: Optional[str] = None
    user_platform_id: Optional[str] = None
    platform: str = "whatsapp"


class MessageHandlerResponse(BaseModel):
    result: str
    user_platform_id: Optional[str] = None
