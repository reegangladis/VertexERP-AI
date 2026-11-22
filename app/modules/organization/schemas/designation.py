"""Designation schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DesignationBase(BaseModel):
    """Base fields for designation."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique designation code")
    name: str = Field(..., min_length=1, max_length=128, description="Designation title")
    description: str | None = Field(None, description="Designation responsibilities")
    level: int = Field(
        default=1, ge=1, le=100, description="Hierarchy level (1=Junior, 10=Executive)"
    )
    is_active: bool = True


class DesignationCreate(DesignationBase):
    """Schema for creating designation."""

    pass


class DesignationUpdate(BaseModel):
    """Schema for updating designation."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    level: int | None = Field(None, ge=1, le=100)
    is_active: bool | None = None


class DesignationResponse(DesignationBase):
    """Response schema for designation."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
