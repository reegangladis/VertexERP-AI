from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.core.config import settings
from app.database.connection import get_db
from app.database.redis import check_redis_health
from app.schemas.response import APIResponse
from app.schemas.system import HealthResponse
from app.utils.response import standard_json_response

router = APIRouter()


@router.get("", response_model=APIResponse[HealthResponse])
async def get_health(
    db: AsyncSession = Depends(get_db),
) -> APIResponse[HealthResponse] | HealthResponse:
    """Detailed health check validating internal services (Postgres & Redis)."""
    # 1. Validate database connection
    db_status = "healthy"
    try:
        # Run a minimal select query to check db network roundtrip
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # 2. Validate Redis connectivity
    redis_ok = await check_redis_health()
    redis_status = "healthy" if redis_ok else "unhealthy"

    # Determine overall status
    is_healthy = db_status == "healthy" and redis_status == "healthy"
    overall_status = "healthy" if is_healthy else "unhealthy"

    # Return standard health payload
    health_data = HealthResponse(
        status=overall_status,
        version="1.2.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
        services={"database": db_status, "redis": redis_status},
    )

    if not is_healthy:
        # Return 503 Service Unavailable using standard response envelope
        return standard_json_response(
            status_code=503,
            success=False,
            message="One or more internal services are unhealthy",
            data=health_data.model_dump(),
        )

    return APIResponse(
        success=True,
        message="All services are healthy",
        data=health_data,
    )
