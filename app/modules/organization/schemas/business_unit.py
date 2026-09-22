"""Business Unit schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BusinessUnitBase(BaseModel):
    """Base fields for business unit."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique business unit code")
    name: str = Field(..., min_length=1, max_length=128, description="Business unit name")
    description: str | None = Field(None, description="Business unit description")
    head_user_id: uuid.UUID | None = Field(None, description="Head of Business Unit user ID")
    is_active: bool = True


class BusinessUnitCreate(BusinessUnitBase):
    """Schema for creating business unit."""

    pass


class BusinessUnitUpdate(BaseModel):
    """Schema for updating business unit."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    head_user_id: uuid.UUID | None = None
    is_active: bool | None = None


class BusinessUnitResponse(BusinessUnitBase):
    """Response schema for business unit."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
