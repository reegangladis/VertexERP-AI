from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.core.config import settings
from app.database.connection import get_db
from app.database.redis import check_redis_health
from app.schemas.system import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def get_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
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
    response = HealthResponse(
        status=overall_status,
        version="1.1.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
        services={"database": db_status, "redis": redis_status},
    )

    if not is_healthy:
        # Return 503 Service Unavailable when core dependency is failing
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )

    return response
