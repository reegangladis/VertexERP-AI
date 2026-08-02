"""
Scheduler Service — manages cron, recurring, one-time, and delayed job execution.
Calculates next-run times from cron expressions and manages retry queues.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import ScheduledJob
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import ScheduledJobCreate, ScheduledJobUpdate


class SchedulerService:
    """Manages scheduled workflow trigger jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    # ─── CRUD ────────────────────────────────────────────────────────────────────
    async def create_job(
        self, org_id: uuid.UUID | None, data: ScheduledJobCreate
    ) -> ScheduledJob:
        next_run = data.next_run_at or self._compute_next_run(
            data.cron_expression, data.schedule_type
        )
        job = await self.repo.create_scheduled_job(
            org_id,
            {
                "workflow_id": data.workflow_id,
                "name": data.name,
                "schedule_type": data.schedule_type,
                "cron_expression": data.cron_expression,
                "next_run_at": next_run,
                "status": "active",
                "payload": data.payload or {},
                "max_retries": data.max_retries,
            },
        )
        await self.db.commit()
        return job

    async def update_job(
        self, org_id: uuid.UUID | None, job_id: uuid.UUID, data: ScheduledJobUpdate
    ) -> ScheduledJob | None:
        job = await self.repo.get_scheduled_job(org_id, job_id)
        if not job:
            return None
        updates = data.model_dump(exclude_unset=True)
        if "cron_expression" in updates and updates.get("cron_expression"):
            updates["next_run_at"] = self._compute_next_run(
                updates["cron_expression"], job.schedule_type
            )
        updated = await self.repo.update_scheduled_job(job, updates)
        await self.db.commit()
        return updated

    async def delete_job(self, org_id: uuid.UUID | None, job_id: uuid.UUID) -> bool:
        job = await self.repo.get_scheduled_job(org_id, job_id)
        if not job:
            return False
        await self.repo.delete_scheduled_job(job)
        await self.db.commit()
        return True

    async def list_jobs(
        self,
        org_id: uuid.UUID | None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ScheduledJob]:
        return await self.repo.list_scheduled_jobs(
            org_id, status=status, skip=skip, limit=limit
        )

    async def get_job(
        self, org_id: uuid.UUID | None, job_id: uuid.UUID
    ) -> ScheduledJob | None:
        return await self.repo.get_scheduled_job(org_id, job_id)

    # ─── Manual Trigger ──────────────────────────────────────────────────────────
    async def trigger_now(
        self, org_id: uuid.UUID | None, job_id: uuid.UUID
    ) -> dict[str, Any]:
        """Manually trigger a scheduled job immediately."""
        job = await self.repo.get_scheduled_job(org_id, job_id)
        if not job:
            return {"error": "Job not found"}
        now = datetime.now(UTC)
        next_run = self._compute_next_run(job.cron_expression, job.schedule_type, now)
        await self.repo.update_scheduled_job(
            job,
            {
                "last_run_at": now,
                "next_run_at": next_run,
            },
        )
        await self.db.commit()
        return {
            "job_id": str(job.id),
            "triggered_at": now.isoformat(),
            "next_run_at": next_run.isoformat() if next_run else None,
            "payload": job.payload,
        }

    # ─── Due Job Processing ──────────────────────────────────────────────────────
    async def process_due_jobs(self) -> list[dict[str, Any]]:
        """Poll and process all due jobs — called by a background task or scheduler tick."""
        now = datetime.now(UTC)
        due_jobs = await self.repo.get_due_scheduled_jobs(now)
        processed = []
        for job in due_jobs:
            result = await self._run_job(job, now)
            processed.append(result)
        if processed:
            await self.db.commit()
        return processed

    async def _run_job(self, job: ScheduledJob, now: datetime) -> dict[str, Any]:
        next_run = self._compute_next_run(job.cron_expression, job.schedule_type, now)
        new_status = "active"
        if job.schedule_type == "one_time":
            new_status = "completed"
        await self.repo.update_scheduled_job(
            job,
            {
                "last_run_at": now,
                "next_run_at": next_run,
                "status": new_status,
                "retry_count": 0,
            },
        )
        return {
            "job_id": str(job.id),
            "workflow_id": str(job.workflow_id),
            "executed_at": now.isoformat(),
            "next_run_at": next_run.isoformat() if next_run else None,
        }

    # ─── Cron / Schedule Calculator ──────────────────────────────────────────────
    def _compute_next_run(
        self,
        cron_expression: str | None,
        schedule_type: str,
        after: datetime | None = None,
    ) -> datetime | None:
        after = after or datetime.now(UTC)

        if schedule_type == "one_time":
            return None

        if schedule_type in ("cron", "recurring") and cron_expression:
            return self._parse_cron_next(cron_expression, after)

        if schedule_type == "delayed":
            return after + timedelta(minutes=5)

        return after + timedelta(hours=1)

    def _parse_cron_next(self, cron: str, after: datetime) -> datetime | None:
        """
        Simplified cron parser for standard 5-field cron expressions.
        Uses croniter if available, otherwise falls back to 1-hour default.
        Supported: '*/5 * * * *', '0 8 * * 1-5', '30 9 1 * *', etc.
        """
        try:
            from croniter import croniter  # type: ignore

            it = croniter(cron, after)
            return it.get_next(datetime)
        except ImportError:
            # Fallback: basic interval parsing for simple patterns like */N
            parts = cron.strip().split()
            if len(parts) == 5:
                minute_part = parts[0]
                if minute_part.startswith("*/"):
                    try:
                        interval_minutes = int(minute_part[2:])
                        return after + timedelta(minutes=interval_minutes)
                    except ValueError:
                        pass
            return after + timedelta(hours=1)

    def calculate_next_run(self, cron_expression: str) -> str | None:
        """Public utility to preview next run time for a given cron expression."""
        now = datetime.now(UTC)
        next_run = self._parse_cron_next(cron_expression, now)
        return next_run.isoformat() if next_run else None
