"""FastAPI endpoints for Background Jobs and Asynchronous Processing."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)
from app.modules.jobs.schemas.job import (
    JobCancelRequest,
    JobCreateRequest,
    JobDetailRead,
    JobExecutionLogRead,
    JobRead,
    JobRetryRequest,
    JobScheduleCreate,
    JobScheduleRead,
    JobScheduleUpdate,
    QueueMetricsResponse,
)
from app.modules.jobs.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Background Processing & Jobs"])


# ------------------------------------------------------------------------------
# Job Enqueue & Query Endpoints
# ------------------------------------------------------------------------------
@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_WRITE.value))],
)
async def enqueue_job(
    payload: JobCreateRequest,
    eager: bool = Query(False, description="Execute synchronously for testing"),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Enqueue a background job for asynchronous worker processing.
    Returns HTTP 202 Accepted immediately without blocking the request.
    """
    job = await job_service.create_and_enqueue_job(
        session=db,
        tenant_id=tenant_id,
        organization_id=organization_id,
        user_id=user_id,
        payload=payload,
        eager=eager,
    )
    return JobRead.model_validate(job)


@router.get(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_READ.value))],
)
async def list_jobs(
    job_type: str | None = None,
    status: str | None = None,
    is_dead_letter: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """List tenant background jobs with status filtering and pagination."""
    jobs, total = await job_service.list_jobs(
        session=db,
        tenant_id=tenant_id,
        job_type=job_type,
        status=status,
        is_dead_letter=is_dead_letter,
        skip=skip,
        limit=limit,
    )
    items = [JobRead.model_validate(j) for j in jobs]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/metrics",
    response_model=QueueMetricsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_READ.value))],
)
async def get_queue_metrics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Retrieve real-time queue depths, status breakdowns, and worker telemetry."""
    return await job_service.get_metrics(session=db, tenant_id=tenant_id)


# ------------------------------------------------------------------------------
# Recurring Schedules Endpoints (Declared before /{job_id} to prevent path collision)
# ------------------------------------------------------------------------------
@router.post(
    "/schedules",
    response_model=JobScheduleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_SCHEDULES_MANAGE.value))],
)
async def create_schedule(
    payload: JobScheduleCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Create a recurring cron task schedule."""
    sched = await job_service.create_schedule(
        session=db,
        tenant_id=tenant_id,
        organization_id=organization_id,
        user_id=user_id,
        payload=payload,
    )
    return JobScheduleRead.model_validate(sched)


@router.get(
    "/schedules",
    response_model=list[JobScheduleRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_READ.value))],
)
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """List recurring schedules."""
    schedules = await job_service.list_schedules(session=db, tenant_id=tenant_id)
    return [JobScheduleRead.model_validate(s) for s in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=JobScheduleRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_READ.value))],
)
async def get_schedule(
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Get schedule details."""
    sched = await job_service.get_schedule(session=db, tenant_id=tenant_id, schedule_id=schedule_id)
    if not sched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")
    return JobScheduleRead.model_validate(sched)


@router.put(
    "/schedules/{schedule_id}",
    response_model=JobScheduleRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_SCHEDULES_MANAGE.value))],
)
async def update_schedule(
    schedule_id: uuid.UUID,
    payload: JobScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Update a recurring schedule."""
    sched = await job_service.update_schedule(
        session=db,
        tenant_id=tenant_id,
        schedule_id=schedule_id,
        payload=payload,
    )
    if not sched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")
    return JobScheduleRead.model_validate(sched)


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_SCHEDULES_MANAGE.value))],
)
async def delete_schedule(
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Delete a recurring schedule."""
    deleted = await job_service.delete_schedule(
        session=db, tenant_id=tenant_id, schedule_id=schedule_id
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")
    return {"message": "Schedule deleted successfully."}


@router.post(
    "/schedules/{schedule_id}/trigger",
    response_model=JobRead,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_SCHEDULES_MANAGE.value))],
)
async def trigger_schedule(
    schedule_id: uuid.UUID,
    eager: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Trigger an immediate execution run of a scheduled job."""
    try:
        job = await job_service.trigger_schedule(
            session=db,
            tenant_id=tenant_id,
            schedule_id=schedule_id,
            eager=eager,
        )
        return JobRead.model_validate(job)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ------------------------------------------------------------------------------
# Job Detail & Mutation Endpoints (Parameterized /{job_id})
# ------------------------------------------------------------------------------
@router.get(
    "/{job_id}",
    response_model=JobDetailRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_READ.value))],
)
async def get_job_details(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Fetch complete job details including payload, result, and execution attempt logs."""
    job = await job_service.get_job(session=db, tenant_id=tenant_id, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found in this tenant.",
        )

    exec_logs = [JobExecutionLogRead.model_validate(l) for l in job.execution_logs]

    return JobDetailRead(
        id=job.id,
        tenant_id=job.tenant_id,
        organization_id=job.organization_id,
        job_type=job.job_type,
        job_name=job.job_name,
        status=job.status,
        priority=job.priority,
        idempotency_key=job.idempotency_key,
        correlation_id=job.correlation_id,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        backoff_base_seconds=job.backoff_base_seconds,
        timeout_seconds=job.timeout_seconds,
        is_dead_letter=job.is_dead_letter,
        dead_letter_reason=job.dead_letter_reason,
        scheduled_at=job.scheduled_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
        payload_json=job.payload_json or {},
        result_json=job.result_json,
        error_message=job.error_message,
        stack_trace=job.stack_trace,
        execution_logs=exec_logs,
    )


@router.post(
    "/{job_id}/retry",
    response_model=JobRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_RETRY.value))],
)
async def retry_job(
    job_id: uuid.UUID,
    payload: JobRetryRequest | None = None,
    eager: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Manually re-trigger a failed or dead-letter job."""
    force_reset = payload.force_reset if payload else True
    try:
        job = await job_service.retry_job(
            session=db,
            tenant_id=tenant_id,
            job_id=job_id,
            force_reset=force_reset,
            eager=eager,
        )
        return JobRead.model_validate(job)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/{job_id}/cancel",
    response_model=JobRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.JOBS_CANCEL.value))],
)
async def cancel_job(
    job_id: uuid.UUID,
    payload: JobCancelRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Cancel a pending, queued, or running job."""
    reason = payload.reason if payload else "Cancelled by user"
    try:
        job = await job_service.cancel_job(
            session=db,
            tenant_id=tenant_id,
            job_id=job_id,
            reason=reason,
        )
        return JobRead.model_validate(job)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
