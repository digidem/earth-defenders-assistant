from fastapi import APIRouter

from eda_ai_api.api.routes import grant, heartbeat, onboarding, profile_plugin, supervisor

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(grant.router, tags=["discovery"], prefix="/grant")
api_router.include_router(supervisor.router, tags=["supervisor"], prefix="/supervisor")
api_router.include_router(onboarding.router, tags=["onboarding"], prefix="/onboarding")
api_router.include_router(profile_plugin.router, tags=["profile_plugin"], prefix="/profile_plugin")
