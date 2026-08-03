from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScheduledJobBase(BaseModel):
    name: str
    job_type: str
    cron_expression: str
    status: str = "active"
    config: dict | None = None


class ScheduledJobCreate(ScheduledJobBase):
    organization_id: UUID | None = None


class ScheduledJobUpdate(BaseModel):
    name: str | None = None
    job_type: str | None = None
    cron_expression: str | None = None
    status: str | None = None
    config: dict | None = None


class ScheduledJobResponse(ScheduledJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID | None = None
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
