"""Recurring Job Scheduler and Cron Evaluation Engine."""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models.job import BackgroundJob, JobPriority, JobSchedule, JobStatus

logger = logging.getLogger("vertexerp.jobs.scheduler")


class CronScheduler:
    """Evaluates recurring job schedules and enqueues scheduled instances."""

    @staticmethod
    def calculate_next_run(cron_expression: str, from_time: datetime | None = None) -> datetime:
        """
        Calculate the next execution timestamp based on cron expression or interval pattern.
        Supports standard cron approximations (e.g. '* * * * *', '*/5 * * * *', '0 * * * *', '0 0 * * *').
        """
        base = from_time or datetime.now(UTC)
        expr = cron_expression.strip()

        # Handle simple interval aliases
        if expr in ("@hourly", "0 * * * *"):
            return base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif expr in ("@daily", "0 0 * * *"):
            return base.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif expr.startswith("*/"):
            try:
                parts = expr.split()
                min_step = int(parts[0].replace("*/", ""))
                return base + timedelta(minutes=min_step)
            except Exception:
                return base + timedelta(minutes=5)
        elif expr == "* * * * *":
            return base + timedelta(minutes=1)
        else:
            # Default fallback: +1 hour
            return base + timedelta(hours=1)

    @classmethod
    async def evaluate_schedules(
        cls,
        session: AsyncSession,
        tenant_id: uuid.UUID | None = None,
    ) -> list[BackgroundJob]:
        """
        Scan active job schedules and trigger jobs for matured schedules.
        """
        now = datetime.now(UTC)
        stmt = select(JobSchedule).where(JobSchedule.is_enabled)
        if tenant_id:
            stmt = stmt.where(JobSchedule.tenant_id == tenant_id)

        res = await session.execute(stmt)
        schedules = res.scalars().all()

        enqueued_jobs: list[BackgroundJob] = []

        for sched in schedules:
            if sched.next_run_at is None or sched.next_run_at <= now:
                # Create and enqueue job instance
                job = BackgroundJob(
                    id=uuid.uuid4(),
                    tenant_id=sched.tenant_id,
                    organization_id=sched.organization_id,
                    job_type=sched.job_type,
                    job_name=f"{sched.name} - Automated Run",
                    status=JobStatus.PENDING.value,
                    priority=JobPriority.NORMAL.value,
                    payload_json=sched.payload_template or {},
                    created_by=sched.created_by,
                    scheduled_at=now,
                )
                session.add(job)
                enqueued_jobs.append(job)

                sched.last_run_at = now
                sched.next_run_at = cls.calculate_next_run(sched.cron_expression, now)
                logger.info(
                    "Scheduler triggered job '%s' (type=%s, next_run=%s)",
                    sched.name,
                    sched.job_type,
                    sched.next_run_at.isoformat(),
                )

        if enqueued_jobs:
            await session.flush()

        return enqueued_jobs


# Scheduler singleton
cron_scheduler = CronScheduler()
