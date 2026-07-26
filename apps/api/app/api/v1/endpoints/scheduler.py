import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.scheduler_service import SchedulerService
from app.schemas.workflow import (
    ScheduledJobCreate,
    ScheduledJobUpdate,
    ScheduledJobResponse,
)

router = APIRouter()


def _get_org_id() -> Optional[uuid.UUID]:
    return None


@router.post("/", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_job(
    payload: ScheduledJobCreate,
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    return await service.create_job(_get_org_id(), payload)


@router.get("/", response_model=List[ScheduledJobResponse])
async def list_scheduled_jobs(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    return await service.list_jobs(_get_org_id(), status=status, skip=skip, limit=limit)


@router.get("/preview-next-run")
async def preview_next_run(
    cron_expression: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = SchedulerService(db)
    next_run = service.calculate_next_run(cron_expression)
    return {"cron_expression": cron_expression, "next_run_at": next_run}


@router.get("/{job_id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    job = await service.get_job(_get_org_id(), job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return job


@router.patch("/{job_id}", response_model=ScheduledJobResponse)
async def update_scheduled_job(
    job_id: uuid.UUID,
    payload: ScheduledJobUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    job = await service.update_job(_get_org_id(), job_id, payload)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    deleted = await service.delete_job(_get_org_id(), job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scheduled job not found")


@router.post("/{job_id}/trigger", response_model=Dict[str, Any])
async def trigger_job_now(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    result = await service.trigger_now(_get_org_id(), job_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/process-due-jobs", response_model=List[Dict[str, Any]])
async def process_due_jobs(
    db: AsyncSession = Depends(get_db),
):
    """Internal system endpoint to fire all due scheduled jobs."""
    service = SchedulerService(db)
    return await service.process_due_jobs()
