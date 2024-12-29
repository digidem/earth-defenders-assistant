from typing import Optional, List, Dict
from fastapi import UploadFile
from pydantic import BaseModel


class MessageHistory(BaseModel):
    human: str
    ai: str
    timestamp: str


class ClassifierRequest(BaseModel):
    message: Optional[str] = None
    audio: Optional[UploadFile] = None
    session_id: Optional[str] = None
    message_history: Optional[List[MessageHistory]] = None

    class Config:
        arbitrary_types_allowed = True


class ClassifierResponse(BaseModel):
    result: str
