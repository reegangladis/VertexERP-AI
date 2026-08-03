from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OfficeLocationBase(BaseModel):
    name: str
    floor: str | None = None
    building: str | None = None
    capacity: int | None = None


class OfficeLocationCreate(OfficeLocationBase):
    organization_id: UUID
    location_id: UUID | None = None
    branch_id: UUID | None = None


class OfficeLocationUpdate(BaseModel):
    name: str | None = None
    floor: str | None = None
    building: str | None = None
    capacity: int | None = None
    location_id: UUID | None = None
    branch_id: UUID | None = None


class OfficeLocationResponse(OfficeLocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    location_id: UUID | None = None
    branch_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
