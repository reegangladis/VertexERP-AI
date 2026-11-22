"""Job Executor handling timeout enforcement, retries, backoff, DLQ, and execution logging."""

import asyncio
import logging
import secrets
import traceback
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import set_correlation_id, set_tenant_id, set_user_id
from app.core.metrics import metrics_registry
from app.infrastructure.database.session import set_superuser_context, set_tenant_context
from app.modules.jobs.models.job import BackgroundJob, JobExecutionLog, JobStatus
from app.modules.jobs.workers.registry import worker_registry

logger = logging.getLogger("vertexerp.jobs.executor")


class JobExecutor:
    """Orchestrates single-job execution lifecycle with zero-trust safety and resilience."""

    @staticmethod
    def calculate_backoff_delay(retry_count: int, base_seconds: float = 2.0) -> float:
        """
        Calculate exponential backoff with randomized jitter.
        Formula: base * 2^(retry-1) + uniform(0, 0.5)
        """
        exponent = max(0, retry_count - 1)
        exponential_part = base_seconds * (2**exponent)
        jitter = secrets.SystemRandom().uniform(0.0, 0.5)
        return min(3600.0, exponential_part + jitter)

    @classmethod
    async def execute_job(
        cls,
        session: AsyncSession,
        job_id: uuid.UUID,
        worker_id: str | None = None,
    ) -> BackgroundJob:
        """
        Execute a single background job under strict timeout, logging, and retry rules.
        """
        worker_id_str = worker_id or f"worker_{uuid.uuid4().hex[:8]}"

        # Load job under superuser context to discover its tenant
        await set_superuser_context(session, True)
        stmt = select(BackgroundJob).where(BackgroundJob.id == job_id)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise ValueError(f"Job {job_id} not found.")

        # Immediately narrow context to job's tenant
        await set_superuser_context(session, False)
        await set_tenant_context(session, job.tenant_id)

        # If already terminal or cancelled, skip
        if job.status in (
            JobStatus.COMPLETED.value,
            JobStatus.CANCELLED.value,
            JobStatus.DEAD_LETTER.value,
        ):
            logger.warning("Job %s is already in terminal state %s, skipping.", job_id, job.status)
            return job

        # Bind context variables for distributed tracing
        correlation_id = job.correlation_id or f"job_corr_{uuid.uuid4().hex[:12]}"
        set_correlation_id(correlation_id)
        set_tenant_id(job.tenant_id)
        set_user_id(job.created_by)

        current_attempt = job.retry_count + 1
        start_time = datetime.now(UTC)

        # Transition job to RUNNING
        job.status = JobStatus.RUNNING.value
        job.started_at = start_time
        job.error_message = None
        job.stack_trace = None

        # Create execution log entry
        exec_log = JobExecutionLog(
            id=uuid.uuid4(),
            job_id=job.id,
            tenant_id=job.tenant_id,
            attempt_number=current_attempt,
            status="RUNNING",
            started_at=start_time,
            worker_id=worker_id_str,
        )
        session.add(exec_log)
        await session.flush()

        logger.info(
            "Starting execution of job=%s (type=%s, attempt=%d/%d, timeout=%ds, corr_id=%s)",
            job.id,
            job.job_type,
            current_attempt,
            job.max_retries,
            job.timeout_seconds,
            correlation_id,
        )

        try:
            # Resolve worker
            worker = worker_registry.get_worker(job.job_type)

            # Execute with timeout enforcement
            result_data = await asyncio.wait_for(
                worker.process(job=job, payload=job.payload_json or {}, session=session),
                timeout=float(job.timeout_seconds),
            )

            # Success path
            end_time = datetime.now(UTC)
            duration_sec = (end_time - start_time).total_seconds()
            duration_ms = duration_sec * 1000.0

            job.status = JobStatus.COMPLETED.value
            job.result_json = result_data
            job.completed_at = end_time
            job.is_dead_letter = False

            exec_log.status = "COMPLETED"
            exec_log.completed_at = end_time
            exec_log.duration_ms = duration_ms

            # Record telemetry
            metrics_registry.worker_jobs_processed_total.inc(
                labels={"job_type": job.job_type, "status": "completed"}
            )
            metrics_registry.worker_job_duration_seconds.observe(
                duration_sec, labels={"job_type": job.job_type}
            )

            logger.info("Successfully completed job=%s in %.2fms", job.id, duration_ms)

        except TimeoutError:
            end_time = datetime.now(UTC)
            duration_sec = (end_time - start_time).total_seconds()
            duration_ms = duration_sec * 1000.0
            error_msg = f"Job execution timed out after {job.timeout_seconds} seconds"
            stack_text = (
                "asyncio.TimeoutError: Job execution exceeded maximum allotted time window."
            )

            metrics_registry.worker_jobs_processed_total.inc(
                labels={"job_type": job.job_type, "status": "timeout"}
            )
            metrics_registry.worker_job_duration_seconds.observe(
                duration_sec, labels={"job_type": job.job_type}
            )

            logger.warning("Job=%s TIMED OUT on attempt %d: %s", job.id, current_attempt, error_msg)
            cls._handle_failure(
                job=job,
                exec_log=exec_log,
                error_msg=error_msg,
                stack_text=stack_text,
                duration_ms=duration_ms,
                end_time=end_time,
            )

        except Exception as exc:
            end_time = datetime.now(UTC)
            duration_sec = (end_time - start_time).total_seconds()
            duration_ms = duration_sec * 1000.0
            error_msg = str(exc) or exc.__class__.__name__
            stack_text = traceback.format_exc()

            metrics_registry.worker_jobs_processed_total.inc(
                labels={"job_type": job.job_type, "status": "failed"}
            )
            metrics_registry.worker_job_duration_seconds.observe(
                duration_sec, labels={"job_type": job.job_type}
            )

            logger.error("Job=%s FAILED on attempt %d: %s", job.id, current_attempt, error_msg)
            cls._handle_failure(
                job=job,
                exec_log=exec_log,
                error_msg=error_msg,
                stack_text=stack_text,
                duration_ms=duration_ms,
                end_time=end_time,
            )

        await session.flush()
        return job

    @classmethod
    def _handle_failure(
        cls,
        job: BackgroundJob,
        exec_log: JobExecutionLog,
        error_msg: str,
        stack_text: str,
        duration_ms: float,
        end_time: datetime,
    ) -> None:
        """Handle failure transitions, retries, exponential backoff, and DLQ assignment."""
        exec_log.status = "FAILED"
        exec_log.completed_at = end_time
        exec_log.duration_ms = duration_ms
        exec_log.error_message = error_msg
        exec_log.stack_trace = stack_text

        job.retry_count += 1
        job.error_message = error_msg
        job.stack_trace = stack_text

        if job.retry_count < job.max_retries:
            # Schedule retry with exponential backoff
            delay = cls.calculate_backoff_delay(job.retry_count, job.backoff_base_seconds)
            job.status = JobStatus.QUEUED.value
            job.scheduled_at = end_time + timedelta(seconds=delay)
            job.started_at = None
            metrics_registry.worker_job_retries_total.inc(labels={"job_type": job.job_type})
            logger.info(
                "Job=%s scheduled for RETRY #%d in %.2fs (at %s)",
                job.id,
                job.retry_count,
                delay,
                job.scheduled_at.isoformat(),
            )
        else:
            # Exhausted retries -> Dead Letter Queue (DLQ)
            job.status = JobStatus.DEAD_LETTER.value
            job.is_dead_letter = True
            job.dead_letter_reason = f"Exhausted maximum retry limit of {job.max_retries}"
            job.completed_at = end_time
            metrics_registry.worker_dead_letter_total.inc(labels={"job_type": job.job_type})
            logger.error(
                "Job=%s EXHAUSTED all %d retries. Moved to DEAD_LETTER queue.",
                job.id,
                job.max_retries,
            )
