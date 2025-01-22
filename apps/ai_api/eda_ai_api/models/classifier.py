from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel


class MessageHistory(BaseModel):
    human: str
    ai: str
    timestamp: str

    def to_context_format(self) -> str:
        return f"Human: {self.human}\nAssistant: {self.ai}"


class ClassifierRequest(BaseModel):
    message: Optional[str] = None
    audio: Optional[UploadFile] = None
    session_id: Optional[str] = None
    message_history: Optional[List[MessageHistory]] = None
    platform: Optional[str] = None  # Add platform field

    class Config:
        arbitrary_types_allowed = True


class ClassifierResponse(BaseModel):
    result: str
