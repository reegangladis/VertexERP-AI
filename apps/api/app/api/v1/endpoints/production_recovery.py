import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.production_repository import ProductionRepository
from app.services.backup_recovery_service import BackupRecoveryService
from app.models.production import RestoreJob
from app.schemas.production import RestoreJobCreate, RestoreJobOut

router = APIRouter()
backup_service = BackupRecoveryService()


@router.post("/restore", response_model=RestoreJobOut, status_code=status.HTTP_201_CREATED)
async def trigger_restore_job(
    payload: RestoreJobCreate,
    db: AsyncSession = Depends(get_db),
):
    """Simulates or triggers a Disaster Recovery restoration job with RPO/RTO telemetry."""
    repo = ProductionRepository(db)
    res = backup_service.simulate_disaster_recovery_restore(str(payload.backup_job_id), payload.target_environment)

    job = RestoreJob(
        backup_job_id=payload.backup_job_id,
        target_environment=payload.target_environment,
        status=res["status"],
        rpo_achieved_minutes=res["rpo_achieved_minutes"],
        rto_achieved_minutes=res["rto_achieved_minutes"],
        verification_details=res["verification_details"],
        executed_by="admin_dr_operator",
    )
    return await repo.create_restore_job(job)


@router.get("/list", response_model=List[RestoreJobOut])
async def list_restore_jobs(db: AsyncSession = Depends(get_db)):
    """List historical restore jobs and DR drills."""
    repo = ProductionRepository(db)
    return await repo.list_restore_jobs()


@router.get("/sla")
async def get_disaster_recovery_sla():
    """Returns DR RPO/RTO SLA metrics."""
    return backup_service.get_disaster_recovery_sla()
