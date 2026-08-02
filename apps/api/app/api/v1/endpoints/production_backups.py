from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.production import BackupJob
from app.repositories.production_repository import ProductionRepository
from app.schemas.production import BackupJobCreate, BackupJobOut
from app.services.backup_recovery_service import BackupRecoveryService

router = APIRouter()
backup_service = BackupRecoveryService()


@router.post(
    "/trigger", response_model=BackupJobOut, status_code=status.HTTP_201_CREATED
)
async def trigger_backup_job(
    payload: BackupJobCreate,
    db: AsyncSession = Depends(get_db),
):
    """Triggers an automated database & storage snapshot backup."""
    repo = ProductionRepository(db)
    res = backup_service.trigger_backup(payload.job_name, payload.backup_type)

    job = BackupJob(
        job_name=res["job_name"],
        backup_type=res["backup_type"],
        status=res["status"],
        size_bytes=res["size_bytes"],
        storage_location=res["storage_location"],
        checksum_sha256=res["checksum_sha256"],
        duration_seconds=res["duration_seconds"],
    )
    return await repo.create_backup_job(job)


@router.get("/list", response_model=list[BackupJobOut])
async def list_backup_jobs(db: AsyncSession = Depends(get_db)):
    """List historical backup jobs."""
    repo = ProductionRepository(db)
    return await repo.list_backup_jobs()


@router.post("/verify")
async def verify_backup_checksum(backup_id: str = Query(...)):
    """Verifies SHA-256 integrity checksum for a backup snapshot."""
    return backup_service.verify_backup_integrity(backup_id)
