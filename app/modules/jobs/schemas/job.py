"""Pydantic schemas for Background Jobs and Task Processing."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.jobs.models.job import JobPriority


class JobCreateRequest(BaseModel):
    """Payload to enqueue a new background job."""

    job_type: str = Field(
        ..., description="Job domain type (e.g. email, reports, document_ingestion)"
    )
    job_name: str = Field(..., description="Descriptive name of the job")
    priority: int = Field(
        default=JobPriority.NORMAL.value, ge=0, le=2, description="0=NORMAL, 1=HIGH, 2=CRITICAL"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Job parameters and arguments"
    )
    idempotency_key: str | None = Field(
        None, max_length=128, description="Optional unique key for deduplication"
    )
    correlation_id: str | None = Field(
        None, max_length=128, description="Distributed tracing correlation ID"
    )
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Max retry attempts on transient failure"
    )
    backoff_base_seconds: float = Field(
        default=2.0, ge=0.1, le=60.0, description="Base seconds for exponential backoff"
    )
    timeout_seconds: int = Field(
        default=60, ge=1, le=3600, description="Execution timeout in seconds"
    )
    scheduled_at: datetime | None = Field(
        None, description="Optional timestamp for delayed execution"
    )


class JobExecutionLogRead(BaseModel):
    """Execution attempt log record."""

    id: uuid.UUID
    job_id: uuid.UUID
    tenant_id: uuid.UUID
    attempt_number: int
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: float
    error_message: str | None = None
    stack_trace: str | None = None
    worker_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobRead(BaseModel):
    """Summary of background job status."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    job_type: str
    job_name: str
    status: str
    priority: int
    idempotency_key: str | None = None
    correlation_id: str | None = None
    retry_count: int
    max_retries: int
    backoff_base_seconds: float
    timeout_seconds: int
    is_dead_letter: bool
    dead_letter_reason: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobDetailRead(JobRead):
    """Full detail view of background job including payload, result, and execution logs."""

    payload_json: dict[str, Any] = Field(default_factory=dict)
    result_json: dict[str, Any] | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    execution_logs: list[JobExecutionLogRead] = Field(default_factory=list)


class JobRetryRequest(BaseModel):
    """Request payload to manually re-trigger a failed or dead-letter job."""

    force_reset: bool = Field(default=True, description="Reset retry_count to 0")


class JobCancelRequest(BaseModel):
    """Request payload to cancel a queued or running job."""

    reason: str | None = Field(None, description="Cancellation reason")


class JobScheduleCreate(BaseModel):
    """Create a recurring periodic job schedule."""

    name: str = Field(..., max_length=255)
    description: str | None = None
    job_type: str = Field(...)
    cron_expression: str = Field(
        ..., max_length=64, description="Standard 5-part cron or simple schedule"
    )
    payload_template: dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True


class JobScheduleUpdate(BaseModel):
    """Update an existing recurring schedule."""

    name: str | None = None
    description: str | None = None
    cron_expression: str | None = None
    payload_template: dict[str, Any] | None = None
    is_enabled: bool | None = None


class JobScheduleRead(BaseModel):
    """Recurring job schedule response schema."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    job_type: str
    cron_expression: str
    payload_template: dict[str, Any]
    is_enabled: bool
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueueMetricsResponse(BaseModel):
    """Real-time metrics for background workers and queue depth."""

    total_jobs: int
    pending_jobs: int
    queued_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    dead_letter_jobs: int
    active_workers: int
    queue_depth_by_type: dict[str, int]
