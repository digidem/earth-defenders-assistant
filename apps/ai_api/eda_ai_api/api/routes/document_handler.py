import json
import os
import tempfile
from typing import Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.models.document_handler import (
    DocumentUploadResponse,
    DocumentSearchResponse,
)
from eda_ai_api.utils.vector_memory import VectorMemory

config = ConfigLoader.get_config()
router = APIRouter()
memory = VectorMemory()

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": "pdf",
    "text/csv": "csv",
    "application/csv": "csv",
}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    ttl_days: Optional[int] = Form(1),
    user_platform_id: Optional[str] = Form(None),
    platform: Optional[str] = Form("whatsapp"),
    group_id: Optional[str] = Form(None),  # Add group_id parameter
    sender_name: Optional[str] = Form(None),  # Add sender_name parameter
) -> DocumentUploadResponse:
    """
    Upload a document (PDF or CSV) for processing and storage

    Args:
        file: The document file to upload
        ttl_days: Number of days until document expires (optional, default: 1)
        user_platform_id: User's platform ID for recording in conversation history
        platform: Platform identifier (default: whatsapp)
        group_id: Group ID if this is from a group message (optional)
        sender_name: Name of the sender if this is from a group message (optional)
    """
    try:
        # Validate required user_platform_id
        if not user_platform_id:
            raise HTTPException(
                status_code=400,
                detail="user_platform_id is required for document upload",
            )

        # Validate file type
        if file.content_type not in ALLOWED_DOCUMENT_TYPES:
            error_msg = f"Unsupported file type. Allowed types: {list(ALLOWED_DOCUMENT_TYPES.keys())}"

            # Record failed attempt in conversation history if we have a user ID
            if user_platform_id:
                await memory.add_message_to_history(
                    session_id=user_platform_id,
                    user_message=f"[SYSTEM] Attempted to upload file: {file.filename}",
                    assistant_response=f"[SYSTEM] Upload failed: {error_msg}",
                    platform=platform,
                    metadata={
                        "event_type": "document_upload",
                        "status": "failed",
                        "group_id": group_id,
                        "sender_name": sender_name,
                    },
                )

            raise HTTPException(status_code=400, detail=error_msg)

        # Create temp file to store upload
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{ALLOWED_DOCUMENT_TYPES[file.content_type]}"
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Add the document to user-specific vector storage
            doc_metadata = {
                "filename": file.filename,
                "content_type": file.content_type,
                "group_id": group_id,
                "sender_name": sender_name,
                "source_type": "group_upload" if group_id else "direct_upload",
            }

            success = await memory.add_document(
                session_id=user_platform_id,  # Pass user session
                file_path=temp_path,
                content_type=file.content_type,
                platform=platform,  # Pass platform
                ttl_days=ttl_days,
                metadata=doc_metadata,
            )

            if not success:
                error_msg = "Failed to process and store document"

                # Record failure in conversation history
                if user_platform_id:
                    await memory.add_message_to_history(
                        session_id=user_platform_id,
                        user_message=f"[SYSTEM] Attempted to upload document: {file.filename}",
                        assistant_response=f"[SYSTEM] Document processing failed: {error_msg}",
                        platform=platform,
                        metadata={
                            "event_type": "document_upload",
                            "status": "failed",
                            "group_id": group_id,
                            "sender_name": sender_name,
                        },
                    )

                raise HTTPException(status_code=500, detail=error_msg)

            # Record successful upload in conversation history
            if user_platform_id:
                upload_message = f"[DOCUMENT UPLOADED]: {file.filename}"
                if group_id and sender_name:
                    upload_message = f"{sender_name}: {upload_message}"

                await memory.add_message_to_history(
                    session_id=user_platform_id,
                    user_message=upload_message,
                    assistant_response="",  # No response for passive storage
                    platform=platform,
                    metadata={
                        "event_type": "document_upload",
                        "status": "success",
                        "document_metadata": doc_metadata,
                        "group_id": group_id,
                        "sender_name": sender_name,
                        "message_type": "group_passive" if group_id else "direct",
                    },
                )

            return DocumentUploadResponse(
                success=True,
                message=f"Document {file.filename} uploaded and processed successfully",
                document_id=file.filename,
                metadata=doc_metadata,
            )

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Error processing document: {str(e)}"

        # Record unexpected error in conversation history
        if user_platform_id:
            await memory.add_message_to_history(
                session_id=user_platform_id,
                user_message=f"[SYSTEM] Attempted to upload document: {file.filename}",
                assistant_response=f"[SYSTEM] Unexpected error: {error_msg}",
                platform=platform,
                metadata={
                    "event_type": "document_upload", 
                    "status": "error",
                    "group_id": group_id,
                    "sender_name": sender_name,
                },
            )

        logger.error(f"Error processing document upload: {str(e)}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/search", response_model=DocumentSearchResponse)
async def search_documents(
    query: str,
    user_platform_id: str,  # Make this required
    platform: Optional[str] = "whatsapp",  # Add platform parameter
    limit: Optional[int] = 3,
) -> DocumentSearchResponse:
    """
    Search through stored documents using semantic search

    Args:
        query: The search query
        user_platform_id: User's platform ID to search their documents
        platform: Platform identifier (default: whatsapp)
        limit: Maximum number of results to return (optional, default: 3)
    """
    try:
        results = memory.search_documents(
            session_id=user_platform_id,  # Pass user session
            query=query,
            platform=platform,  # Pass platform
            limit=limit,
        )

        return DocumentSearchResponse(success=True, results=results)

    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return DocumentSearchResponse(
            success=False,
            results=[],
            message=f"Error searching documents: {str(e)}",
        )


@router.delete("/cleanup")
async def cleanup_expired_documents():
    """Remove expired documents from storage"""
    try:
        removed_count = await memory.cleanup_expired_documents()
        return {"success": True, "removed_count": removed_count}
    except Exception as e:
        logger.error(f"Error cleaning up documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error cleaning up documents: {str(e)}"
        )
