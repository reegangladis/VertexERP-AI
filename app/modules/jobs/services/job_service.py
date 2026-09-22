"""Service layer for Background Job management and orchestration."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.jobs.engine.executor import JobExecutor
from app.modules.jobs.engine.job_queue import job_queue_manager
from app.modules.jobs.engine.scheduler import CronScheduler
from app.modules.jobs.models.job import (
    BackgroundJob,
    JobSchedule,
    JobStatus,
)
from app.modules.jobs.schemas.job import (
    JobCreateRequest,
    JobScheduleCreate,
    JobScheduleUpdate,
    QueueMetricsResponse,
)

logger = logging.getLogger("vertexerp.jobs.service")


class JobService:
    """Enterprise Job management service enforcing tenancy, idempotency, and non-blocking invariants."""

    async def create_and_enqueue_job(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        payload: JobCreateRequest,
        eager: bool = False,
    ) -> BackgroundJob:
        """
        Create and enqueue a background job.
        Implements strict idempotency deduplication and non-blocking asynchronous dispatch.
        """
        # 1. Idempotency check
        if payload.idempotency_key:
            stmt = (
                select(BackgroundJob)
                .where(
                    BackgroundJob.tenant_id == tenant_id,
                    BackgroundJob.idempotency_key == payload.idempotency_key,
                )
                .options(selectinload(BackgroundJob.execution_logs))
            )
            res = await session.execute(stmt)
            existing_job = res.scalar_one_or_none()
            if existing_job:
                logger.info(
                    "Idempotent hit for key '%s' (job_id=%s, status=%s)",
                    payload.idempotency_key,
                    existing_job.id,
                    existing_job.status,
                )
                return existing_job

        # 2. Instantiate BackgroundJob
        job = BackgroundJob(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            job_type=payload.job_type,
            job_name=payload.job_name,
            status=JobStatus.PENDING.value,
            priority=payload.priority,
            idempotency_key=payload.idempotency_key,
            correlation_id=payload.correlation_id or f"corr_{uuid.uuid4().hex[:12]}",
            payload_json=payload.payload or {},
            max_retries=payload.max_retries,
            backoff_base_seconds=payload.backoff_base_seconds,
            timeout_seconds=payload.timeout_seconds,
            scheduled_at=payload.scheduled_at,
            created_by=user_id,
        )
        session.add(job)
        await session.flush()

        # 3. Dispatch to Queue or run Eagerly
        if eager:
            await JobExecutor.execute_job(session, job.id)
            await session.refresh(job)
        else:
            await job_queue_manager.enqueue(
                job_id=job.id,
                priority=job.priority,
                scheduled_at=job.scheduled_at,
            )

        return job

    async def get_job(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> BackgroundJob | None:
        """Fetch job with execution logs enforcing tenant isolation."""
        stmt = (
            select(BackgroundJob)
            .where(BackgroundJob.id == job_id, BackgroundJob.tenant_id == tenant_id)
            .options(selectinload(BackgroundJob.execution_logs))
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_jobs(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        job_type: str | None = None,
        status: str | None = None,
        is_dead_letter: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[BackgroundJob], int]:
        """List jobs with filtering and pagination."""
        query = select(BackgroundJob).where(BackgroundJob.tenant_id == tenant_id)

        if job_type:
            query = query.where(BackgroundJob.job_type == job_type)
        if status:
            query = query.where(BackgroundJob.status == status)
        if is_dead_letter is not None:
            query = query.where(BackgroundJob.is_dead_letter == is_dead_letter)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await session.execute(count_stmt)
        total = total_res.scalar() or 0

        paged_stmt = query.order_by(BackgroundJob.created_at.desc()).offset(skip).limit(limit)
        res = await session.execute(paged_stmt)
        items = list(res.scalars().all())

        return items, total

    async def retry_job(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        force_reset: bool = True,
        eager: bool = False,
    ) -> BackgroundJob:
        """Retry a failed or dead-letter job."""
        job = await self.get_job(session, tenant_id, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found in this tenant.")

        if force_reset:
            job.retry_count = 0

        job.status = JobStatus.PENDING.value
        job.is_dead_letter = False
        job.dead_letter_reason = None
        job.error_message = None
        job.stack_trace = None
        job.completed_at = None
        await session.flush()

        if eager:
            await JobExecutor.execute_job(session, job.id)
            await session.refresh(job)
        else:
            await job_queue_manager.enqueue(job.id, priority=job.priority)

        return job

    async def cancel_job(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        reason: str | None = None,
    ) -> BackgroundJob:
        """Cancel a pending, queued, or running job."""
        job = await self.get_job(session, tenant_id, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found in this tenant.")

        if job.status == JobStatus.COMPLETED.value:
            raise ValueError(f"Cannot cancel job {job_id} as it is already completed.")

        job.status = JobStatus.CANCELLED.value
        job.completed_at = datetime.now(UTC)
        job.error_message = reason or "Cancelled by user"
        await session.flush()
        return job

    async def get_metrics(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> QueueMetricsResponse:
        """Compute real-time queue depths and status distributions."""
        status_stmt = (
            select(BackgroundJob.status, func.count(BackgroundJob.id))
            .where(BackgroundJob.tenant_id == tenant_id)
            .group_by(BackgroundJob.status)
        )
        status_res = await session.execute(status_stmt)
        status_counts = dict(status_res.all())

        type_stmt = (
            select(BackgroundJob.job_type, func.count(BackgroundJob.id))
            .where(BackgroundJob.tenant_id == tenant_id)
            .group_by(BackgroundJob.job_type)
        )
        type_res = await session.execute(type_stmt)
        type_counts = dict(type_res.all())

        dlq_stmt = select(func.count(BackgroundJob.id)).where(
            BackgroundJob.tenant_id == tenant_id, BackgroundJob.is_dead_letter
        )
        dlq_res = await session.execute(dlq_stmt)
        dlq_count = dlq_res.scalar() or 0

        total_jobs = sum(status_counts.values())

        return QueueMetricsResponse(
            total_jobs=total_jobs,
            pending_jobs=status_counts.get(JobStatus.PENDING.value, 0),
            queued_jobs=status_counts.get(JobStatus.QUEUED.value, 0),
            running_jobs=status_counts.get(JobStatus.RUNNING.value, 0),
            completed_jobs=status_counts.get(JobStatus.COMPLETED.value, 0),
            failed_jobs=status_counts.get(JobStatus.FAILED.value, 0),
            dead_letter_jobs=dlq_count,
            active_workers=2,
            queue_depth_by_type=type_counts,
        )

    # --------------------------------------------------------------------------
    # Schedule Management
    # --------------------------------------------------------------------------
    async def create_schedule(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        payload: JobScheduleCreate,
    ) -> JobSchedule:
        """Create a recurring periodic job schedule."""
        next_run = CronScheduler.calculate_next_run(payload.cron_expression)
        sched = JobSchedule(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            name=payload.name,
            description=payload.description,
            job_type=payload.job_type,
            cron_expression=payload.cron_expression,
            payload_template=payload.payload_template or {},
            is_enabled=payload.is_enabled,
            next_run_at=next_run,
            created_by=user_id,
        )
        session.add(sched)
        await session.flush()
        return sched

    async def list_schedules(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> list[JobSchedule]:
        """List all recurring schedules for a tenant."""
        stmt = (
            select(JobSchedule)
            .where(JobSchedule.tenant_id == tenant_id)
            .order_by(JobSchedule.created_at.desc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def get_schedule(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        schedule_id: uuid.UUID,
    ) -> JobSchedule | None:
        """Fetch a specific recurring schedule."""
        stmt = select(JobSchedule).where(
            JobSchedule.id == schedule_id,
            JobSchedule.tenant_id == tenant_id,
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_schedule(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        schedule_id: uuid.UUID,
        payload: JobScheduleUpdate,
    ) -> JobSchedule | None:
        """Update schedule configuration."""
        sched = await self.get_schedule(session, tenant_id, schedule_id)
        if not sched:
            return None

        if payload.name is not None:
            sched.name = payload.name
        if payload.description is not None:
            sched.description = payload.description
        if payload.cron_expression is not None:
            sched.cron_expression = payload.cron_expression
            sched.next_run_at = CronScheduler.calculate_next_run(payload.cron_expression)
        if payload.payload_template is not None:
            sched.payload_template = payload.payload_template
        if payload.is_enabled is not None:
            sched.is_enabled = payload.is_enabled

        await session.flush()
        return sched

    async def delete_schedule(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        schedule_id: uuid.UUID,
    ) -> bool:
        """Delete a recurring schedule."""
        sched = await self.get_schedule(session, tenant_id, schedule_id)
        if not sched:
            return False
        await session.delete(sched)
        await session.flush()
        return True

    async def trigger_schedule(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        schedule_id: uuid.UUID,
        eager: bool = False,
    ) -> BackgroundJob:
        """Manually trigger an execution run of a scheduled job."""
        sched = await self.get_schedule(session, tenant_id, schedule_id)
        if not sched:
            raise ValueError(f"Schedule {schedule_id} not found.")

        req = JobCreateRequest(
            job_type=sched.job_type,
            job_name=f"Manual Run: {sched.name}",
            payload=sched.payload_template or {},
        )
        return await self.create_and_enqueue_job(
            session=session,
            tenant_id=tenant_id,
            organization_id=sched.organization_id,
            user_id=sched.created_by,
            payload=req,
            eager=eager,
        )


# Global job service singleton
job_service = JobService()
