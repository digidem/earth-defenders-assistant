from typing import Dict, Optional, List
from pydantic import BaseModel


class GlobalKnowledgeUploadResponse(BaseModel):
    """Response model for global knowledge upload endpoint"""

    success: bool
    message: str
    filename: Optional[str] = None


class GlobalKnowledgeSearchResponse(BaseModel):
    """Response model for global knowledge search endpoint"""

    success: bool
    results: List[Dict]
    message: str = ""


class GlobalKnowledgeDocument(BaseModel):
    """Model for a global knowledge document"""

    source: str
    content_type: Optional[str] = None
    added_date: Optional[str] = None
    chunk_count: int
    sample_content: Optional[str] = None


class GlobalKnowledgeListResponse(BaseModel):
    """Response model for listing global knowledge documents"""

    success: bool
    documents: List[GlobalKnowledgeDocument]
    total_count: int
    message: str = ""


class GlobalKnowledgeDeleteResponse(BaseModel):
    """Response model for deleting global knowledge documents"""

    success: bool
    message: str
    deleted_chunks: int
