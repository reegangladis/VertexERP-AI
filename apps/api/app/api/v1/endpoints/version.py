from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.response import APIResponse
from app.schemas.system import VersionResponse

router = APIRouter()


@router.get("", response_model=APIResponse[VersionResponse])
async def get_version() -> APIResponse[VersionResponse]:
    """Returns application environment status and version information."""
    data = VersionResponse(
        status="active",
        version="1.2.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
    )
    return APIResponse(
        success=True,
        message="Application version retrieved successfully",
        data=data,
    )
