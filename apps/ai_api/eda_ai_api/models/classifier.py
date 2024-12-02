from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel


class ClassifierRequest(BaseModel):
    message: Optional[str] = None
    audio: Optional[UploadFile] = None

    class Config:
        arbitrary_types_allowed = True


class ClassifierResponse(BaseModel):
    result: str
