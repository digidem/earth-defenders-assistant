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
    attachment: Optional[UploadFile] = None
    user_platform_id: Optional[str] = None
    platform: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class MessageHandlerResponse(BaseModel):
    result: str
    user_platform_id: Optional[str] = None
