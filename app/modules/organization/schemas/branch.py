"""Branch schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BranchBase(BaseModel):
    """Base fields for branch."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique branch code")
    name: str = Field(..., min_length=1, max_length=128, description="Branch display name")
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=64)
    state: str = Field(..., min_length=1, max_length=64)
    postal_code: str = Field(..., min_length=1, max_length=32)
    country: str = Field(default="USA", max_length=3)
    phone: str | None = Field(None, max_length=32)
    email: str | None = Field(None, max_length=255)
    is_headquarters: bool = False
    is_active: bool = True


class BranchCreate(BranchBase):
    """Schema for creating branch."""

    pass


class BranchUpdate(BaseModel):
    """Schema for updating branch."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    address_line1: str | None = Field(None, min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, min_length=1, max_length=64)
    state: str | None = Field(None, min_length=1, max_length=64)
    postal_code: str | None = Field(None, min_length=1, max_length=32)
    country: str | None = Field(None, max_length=3)
    phone: str | None = Field(None, max_length=32)
    email: str | None = Field(None, max_length=255)
    is_headquarters: bool | None = None
    is_active: bool | None = None


class BranchResponse(BranchBase):
    """Response schema for branch."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
