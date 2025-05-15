from fastapi import APIRouter

from eda_ai_api.api.routes import classifier, grant, heartbeat, onboarding

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(grant.router, tags=["discovery"], prefix="/grant")
api_router.include_router(classifier.router, tags=["classifier"], prefix="/classifier")
api_router.include_router(onboarding.router, tags=["onboarding"], prefix="/onboarding")
