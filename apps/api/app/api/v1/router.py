from fastapi import APIRouter

from app.api.v1.endpoints import health, version

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(version.router, prefix="/version", tags=["system"])
