from fastapi import APIRouter

from eda_ai_api.api.routes import heartbeat, message_handler

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(
    message_handler.router, tags=["message_handler"], prefix="/message_handler"
)
