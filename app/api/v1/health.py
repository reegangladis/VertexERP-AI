"""Health, Readiness, and Liveness Probe Endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.constants import ServiceStatus
from app.infrastructure.database.session import check_db_health
from app.infrastructure.redis.client import check_redis_health

router = APIRouter(prefix="/health", tags=["Health & Observability"])


class LivenessResponse(BaseModel):
    status: str
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: str
    checks: dict[str, Any]


class AppInfoResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    status: str
    timestamp: str


@router.get(
    "/live",
    response_model=LivenessResponse,
    summary="Liveness Probe",
    description="Returns 200 OK if the ASGI application event loop is active and responsive.",
)
async def liveness_probe() -> LivenessResponse:
    """Kubernetes liveness check."""
    return LivenessResponse(
        status="ALIVE",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description=(
        "Validates downstream dependencies (PostgreSQL, Redis). "
        "Returns 503 if critical dependencies are down."
    ),
)
async def readiness_probe(response: Response) -> ReadinessResponse:
    """Kubernetes readiness check evaluating PostgreSQL and Redis."""
    db_status = await check_db_health()
    redis_status = await check_redis_health()

    is_db_healthy = db_status.get("status") == ServiceStatus.HEALTHY.value
    is_redis_healthy = redis_status.get("status") == ServiceStatus.HEALTHY.value

    overall_status = ServiceStatus.HEALTHY.value
    if not is_db_healthy or not is_redis_healthy:
        overall_status = ServiceStatus.UNHEALTHY.value
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=overall_status,
        environment=settings.APP_ENV.value,
        version=settings.APP_VERSION,
        timestamp=datetime.now(UTC).isoformat(),
        checks={
            "database": db_status,
            "redis": redis_status,
        },
    )


@router.get(
    "/startup",
    response_model=LivenessResponse,
    summary="Startup Probe",
    description="Kubernetes startup check confirming initial bootstrap completion.",
)
async def startup_probe() -> LivenessResponse:
    """Kubernetes startup check."""
    return LivenessResponse(
        status="STARTED",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/info",
    response_model=AppInfoResponse,
    summary="Application Information",
    description="Returns public application version and environment metadata.",
)
async def app_info() -> AppInfoResponse:
    """Application metadata overview."""
    return AppInfoResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV.value,
        status="OPERATIONAL",
        timestamp=datetime.now(UTC).isoformat(),
    )
