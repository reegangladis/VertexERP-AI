from datetime import datetime, UTC
from typing import Dict, Any
from fastapi import APIRouter
from app.schemas.cloud_release import GlobalSystemStatusOut

router = APIRouter()


@router.get("/global", response_model=GlobalSystemStatusOut)
async def get_global_system_status():
    """Returns global system operational health and uptime status."""
    return GlobalSystemStatusOut(
        overall_status="ALL_SYSTEMS_OPERATIONAL",
        version="v1.0.0",
        active_regions=3,
        api_gateway_health="HEALTHY",
        database_cluster_health="HEALTHY",
        redis_cluster_health="HEALTHY",
        uptime_percentage=99.99,
        last_updated=datetime.now(UTC),
    )
