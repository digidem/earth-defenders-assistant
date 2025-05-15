from typing import Dict, Optional
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint"""
    success: bool
    message: str
    document_id: Optional[str] = None
    metadata: Optional[Dict] = None


class DocumentSearchResponse(BaseModel):
    """Response model for document search endpoint"""
    success: bool
    results: list
    message: str = ""