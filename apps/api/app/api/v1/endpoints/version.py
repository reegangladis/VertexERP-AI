from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.system import VersionResponse

router = APIRouter()


@router.get("", response_model=VersionResponse)
async def get_version() -> VersionResponse:
    """Returns application environment status and version information."""
    return VersionResponse(
        status="active",
        version="1.1.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
    )
