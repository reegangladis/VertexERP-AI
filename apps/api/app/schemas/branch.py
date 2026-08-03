from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BranchBase(BaseModel):
    name: str
    code: str | None = None
    phone: str | None = None
    email: str | None = None
    manager_uuid: UUID | None = None
    status: str = "active"


class BranchCreate(BranchBase):
    organization_id: UUID
    location_id: UUID | None = None


class BranchUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    phone: str | None = None
    email: str | None = None
    manager_uuid: UUID | None = None
    status: str | None = None
    location_id: UUID | None = None


class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    location_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
