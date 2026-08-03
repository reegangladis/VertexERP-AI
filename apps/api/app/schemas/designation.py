from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DesignationBase(BaseModel):
    name: str
    title: str | None = None
    code: str | None = None
    job_level: str | None = None
    grade: str | None = None
    reporting_level: int | None = None
    description: str | None = None
    status: str = "active"


class DesignationCreate(DesignationBase):
    organization_id: UUID


class DesignationUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    code: str | None = None
    job_level: str | None = None
    grade: str | None = None
    reporting_level: int | None = None
    description: str | None = None
    status: str | None = None


class DesignationResponse(DesignationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
