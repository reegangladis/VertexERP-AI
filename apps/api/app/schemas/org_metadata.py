from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationMetadataBase(BaseModel):
    industry: str | None = None
    company_size: str | None = None
    employee_count: int | None = None
    headquarters: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    website: str | None = None


class OrganizationMetadataUpdate(BaseModel):
    industry: str | None = None
    company_size: str | None = None
    employee_count: int | None = None
    headquarters: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    website: str | None = None


class OrganizationMetadataResponse(OrganizationMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
