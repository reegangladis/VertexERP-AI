"""Central AI Domain Router."""

from fastapi import APIRouter

from app.modules.ai.api.copilot_endpoints import router as copilot_router
from app.modules.ai.api.gateway_endpoints import router as gateway_router
from app.modules.ai.api.rag_endpoints import router as rag_router
from app.modules.ai.api.usage_endpoints import router as usage_router

ai_router = APIRouter(prefix="/ai", tags=["AI Platform & Copilot"])

ai_router.include_router(copilot_router)
ai_router.include_router(gateway_router)
ai_router.include_router(rag_router)
ai_router.include_router(usage_router)
