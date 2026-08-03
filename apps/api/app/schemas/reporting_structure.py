from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportingStructureBase(BaseModel):
    employee_uuid: UUID
    manager_uuid: UUID
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class ReportingStructureCreate(ReportingStructureBase):
    organization_id: UUID


class ReportingStructureUpdate(BaseModel):
    employee_uuid: UUID | None = None
    manager_uuid: UUID | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class ReportingStructureResponse(ReportingStructureBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    effective_from: datetime
    created_at: datetime
    updated_at: datetime
