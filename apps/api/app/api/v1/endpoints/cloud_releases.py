from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.cloud_release import ReleaseHistory
from app.repositories.cloud_release_repository import CloudReleaseRepository
from app.schemas.cloud_release import ReleaseCreate, ReleaseOut, RollbackRequest
from app.services.release_engineering_service import ReleaseEngineeringService

router = APIRouter()
rel_service = ReleaseEngineeringService()


@router.post("/create", response_model=ReleaseOut, status_code=status.HTTP_201_CREATED)
async def create_release(
    payload: ReleaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Creates a new Semantic Versioning release entry (e.g. v1.0.0)."""
    repo = CloudReleaseRepository(db)
    try:
        res = rel_service.create_release(
            payload.version,
            payload.release_name,
            payload.release_type,
            payload.git_commit_sha,
            payload.release_notes,
        )
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)
        ) from ex

    release = ReleaseHistory(
        version=res["version"],
        release_name=res["release_name"],
        release_type=res["release_type"],
        status=res["status"],
        git_commit_sha=res["git_commit_sha"],
        release_notes=res["release_notes"],
        artifacts=res["artifacts"],
        released_by=res["released_by"],
    )
    return await repo.create_release(release)


@router.get("/list", response_model=list[ReleaseOut])
async def list_releases(db: AsyncSession = Depends(get_db)):
    """List historical releases."""
    repo = CloudReleaseRepository(db)
    return await repo.list_releases()


@router.post("/rollback")
async def execute_release_rollback(payload: RollbackRequest):
    """Executes single-click release rollback to a target version."""
    try:
        return rel_service.execute_rollback(
            payload.target_version, payload.environment_name, payload.reason
        )
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)
        ) from ex
