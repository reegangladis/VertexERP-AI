"""Location schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    """Base fields for location."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique location code")
    name: str = Field(..., min_length=1, max_length=128, description="Location site name")
    location_type: str = Field(
        default="OFFICE",
        max_length=32,
        description="Facility type (e.g., OFFICE, WAREHOUSE, PLANT, STORE, DATACENTER)",
    )
    branch_id: uuid.UUID | None = Field(None, description="Linked Branch ID")
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=64)
    state: str = Field(..., min_length=1, max_length=64)
    postal_code: str = Field(..., min_length=1, max_length=32)
    country: str = Field(default="USA", max_length=3)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    is_active: bool = True


class LocationCreate(LocationBase):
    """Schema for creating location."""

    pass


class LocationUpdate(BaseModel):
    """Schema for updating location."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    location_type: str | None = Field(None, max_length=32)
    branch_id: uuid.UUID | None = None
    address_line1: str | None = Field(None, min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, min_length=1, max_length=64)
    state: str | None = Field(None, min_length=1, max_length=64)
    postal_code: str | None = Field(None, min_length=1, max_length=32)
    country: str | None = Field(None, max_length=3)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    is_active: bool | None = None


class LocationResponse(LocationBase):
    """Response schema for location."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
