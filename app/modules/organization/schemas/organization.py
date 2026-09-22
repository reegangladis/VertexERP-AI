"""Pydantic schemas for Organization and Membership domains."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    legal_name: str = Field(..., min_length=2, max_length=255)
    tax_identifier: str = Field(..., min_length=2, max_length=64)
    base_currency: str = Field(default="USD", min_length=3, max_length=3)
    fiscal_year_start_month: int = Field(default=1, ge=1, le=12)
    website: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=128)
    legal_name: str | None = Field(None, min_length=2, max_length=255)
    website: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    legal_name: str
    tax_identifier: str
    base_currency: str
    fiscal_year_start_month: int
    website: str | None
    logo_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TenantMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    is_default: bool
    created_at: datetime


class SwitchOrganizationRequest(BaseModel):
    target_organization_id: uuid.UUID


class AddMemberRequest(BaseModel):
    user_id: uuid.UUID
    role_ids: list[uuid.UUID] = Field(default_factory=list)
    is_default: bool = False
