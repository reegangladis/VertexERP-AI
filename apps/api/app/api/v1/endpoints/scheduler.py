import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.scheduled_job import ScheduledJobRepository
from app.schemas.scheduled_job import (
    ScheduledJobCreate,
    ScheduledJobResponse,
    ScheduledJobUpdate,
)
from app.services.scheduler_service import ScheduledJobService

router = APIRouter()


def get_scheduler_service(
    db: AsyncSession = Depends(get_db_session),
) -> ScheduledJobService:
    return ScheduledJobService(ScheduledJobRepository(db))


@router.post("", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_job(
    data: ScheduledJobCreate,
    service: ScheduledJobService = Depends(get_scheduler_service),
):
    return await service.create(data)


@router.get("", response_model=list[ScheduledJobResponse])
async def list_scheduled_jobs(
    organization_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    service: ScheduledJobService = Depends(get_scheduler_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(
    id: uuid.UUID,
    service: ScheduledJobService = Depends(get_scheduler_service),
):
    job = await service.get(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled job not found"
        )
    return job


@router.put("/{id}", response_model=ScheduledJobResponse)
async def update_scheduled_job(
    id: uuid.UUID,
    data: ScheduledJobUpdate,
    service: ScheduledJobService = Depends(get_scheduler_service),
):
    job = await service.update(id, data)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled job not found"
        )
    return job


@router.delete("/{id}", response_model=ScheduledJobResponse)
async def delete_scheduled_job(
    id: uuid.UUID,
    service: ScheduledJobService = Depends(get_scheduler_service),
):
    job = await service.delete(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled job not found"
        )
    return job
