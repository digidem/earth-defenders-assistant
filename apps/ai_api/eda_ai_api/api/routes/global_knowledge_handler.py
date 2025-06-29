import os
import tempfile
from typing import Dict, List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from loguru import logger

from eda_ai_api.models.global_knowledge_handler import (
    GlobalKnowledgeUploadResponse,
    GlobalKnowledgeSearchResponse,
    GlobalKnowledgeListResponse,
    GlobalKnowledgeDeleteResponse,
    GlobalKnowledgeDocument,
)
from eda_ai_api.utils.memory_manager import get_vector_memory

router = APIRouter()
memory = get_vector_memory()

ALLOWED_GLOBAL_KNOWLEDGE_TYPES = {
    "application/pdf": "pdf",
    "text/csv": "csv",
    "application/csv": "csv",
    "text/plain": "txt",
}


@router.post("/upload", response_model=GlobalKnowledgeUploadResponse)
async def upload_global_knowledge(
    file: UploadFile = File(...),
) -> GlobalKnowledgeUploadResponse:
    """
    Upload content to the global knowledge base

    Args:
        file: The document file to upload
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_GLOBAL_KNOWLEDGE_TYPES:
            error_msg = f"Unsupported file type. Allowed types: {list(ALLOWED_GLOBAL_KNOWLEDGE_TYPES.keys())}"
            raise HTTPException(status_code=400, detail=error_msg)

        # Create temp file to store upload
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{ALLOWED_GLOBAL_KNOWLEDGE_TYPES[file.content_type]}",
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Add to global knowledge base - just use the filename
            success = await memory.add_global_knowledge(
                file_path=temp_path,
                content_type=file.content_type,
                source_name=file.filename,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                },
            )

            if not success:
                error_msg = "Failed to process and store global knowledge"
                raise HTTPException(status_code=500, detail=error_msg)

            return GlobalKnowledgeUploadResponse(
                success=True,
                message=f"Global knowledge from {file.filename} uploaded successfully",
                filename=file.filename,
            )

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Error processing global knowledge: {str(e)}"
        logger.error(f"Error processing global knowledge upload: {str(e)}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/search", response_model=GlobalKnowledgeSearchResponse)
async def search_global_knowledge(
    query: str,
    limit: Optional[int] = 3,
) -> GlobalKnowledgeSearchResponse:
    """
    Search through the global knowledge base using semantic similarity

    Args:
        query: The search query
        limit: Maximum number of results to return (optional, default: 3)
    """
    try:
        results = memory.search_global_knowledge(
            query=query,
            limit=limit,
        )

        return GlobalKnowledgeSearchResponse(success=True, results=results)

    except Exception as e:
        logger.error(f"Error searching global knowledge: {str(e)}")
        return GlobalKnowledgeSearchResponse(
            success=False,
            results=[],
            message=f"Error searching global knowledge: {str(e)}",
        )


@router.get("/list", response_model=GlobalKnowledgeListResponse)
async def list_global_knowledge() -> GlobalKnowledgeListResponse:
    """
    Get a list of all documents in the global knowledge base

    Returns:
        List of all documents with their metadata
    """
    try:
        documents = memory.list_global_knowledge()

        return GlobalKnowledgeListResponse(
            success=True, documents=documents, total_count=len(documents)
        )

    except Exception as e:
        logger.error(f"Error listing global knowledge: {str(e)}")
        return GlobalKnowledgeListResponse(
            success=False,
            documents=[],
            total_count=0,
            message=f"Error listing global knowledge: {str(e)}",
        )


@router.delete(
    "/document/{source_name}", response_model=GlobalKnowledgeDeleteResponse
)
async def delete_global_knowledge_document(
    source_name: str,
    confirm: bool = Query(
        False, description="Confirmation flag to prevent accidental deletion"
    ),
) -> GlobalKnowledgeDeleteResponse:
    """
    Delete all chunks of a specific document from the global knowledge base

    Args:
        source_name: The source name/filename of the document to delete
        confirm: Must be True to actually delete the document
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Must set confirm=true to delete document",
            )

        deleted_count = memory.delete_global_knowledge_document(source_name)

        if deleted_count == 0:
            return GlobalKnowledgeDeleteResponse(
                success=False,
                message=f"No document found with source name: {source_name}",
                deleted_chunks=0,
            )

        return GlobalKnowledgeDeleteResponse(
            success=True,
            message=f"Successfully deleted document '{source_name}' ({deleted_count} chunks)",
            deleted_chunks=deleted_count,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting global knowledge document: {str(e)}")
        return GlobalKnowledgeDeleteResponse(
            success=False,
            message=f"Error deleting document: {str(e)}",
            deleted_chunks=0,
        )


@router.delete("/clear", response_model=GlobalKnowledgeDeleteResponse)
async def clear_global_knowledge(
    confirm: bool = Query(
        False, description="Confirmation flag to prevent accidental deletion"
    )
) -> GlobalKnowledgeDeleteResponse:
    """
    Clear all documents from the global knowledge base

    Args:
        confirm: Must be True to actually clear all knowledge
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Must set confirm=true to clear all global knowledge",
            )

        deleted_count = memory.clear_global_knowledge()

        return GlobalKnowledgeDeleteResponse(
            success=True,
            message=f"Successfully cleared all global knowledge ({deleted_count} chunks deleted)",
            deleted_chunks=deleted_count,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error clearing global knowledge: {str(e)}")
        return GlobalKnowledgeDeleteResponse(
            success=False,
            message=f"Error clearing global knowledge: {str(e)}",
            deleted_chunks=0,
        )
