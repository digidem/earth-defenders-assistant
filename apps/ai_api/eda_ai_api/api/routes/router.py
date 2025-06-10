from fastapi import APIRouter

from eda_ai_api.api.routes import (
    heartbeat,
    message_handler,
    document_handler,
    transcription_handler,
    tts_handler,
    global_knowledge_handler,
)

api_router = APIRouter()

# Health check endpoints
api_router.include_router(heartbeat.router, tags=["Health"], prefix="/health")

# Core AI endpoints
api_router.include_router(
    message_handler.router, tags=["AI Chat"], prefix="/message_handler"
)

# Document processing endpoints
api_router.include_router(
    document_handler.router, tags=["Documents"], prefix="/documents"
)

# Global knowledge base endpoints
api_router.include_router(
    global_knowledge_handler.router,
    tags=["Global Knowledge"],
    prefix="/global_knowledge",
)

# Audio processing endpoints
api_router.include_router(
    transcription_handler.router,
    tags=["Audio Transcription"],
    prefix="/transcription",
)

# Text-to-Speech endpoints
api_router.include_router(
    tts_handler.router,
    tags=["Text-to-Speech"],
    prefix="/tts",
)
