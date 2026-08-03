from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    timezone: str = "UTC"
    status: str = "active"
    subscription: str = "free"
    logo: str | None = None


class OrganizationCreate(OrganizationBase):
    created_by: UUID | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    timezone: str | None = None
    status: str | None = None
    subscription: str | None = None
    logo: str | None = None


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
