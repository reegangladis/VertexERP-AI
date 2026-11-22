"""Warehouse and Bin/Location Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    aisle: str | None = Field(None, max_length=32)
    rack: str | None = Field(None, max_length=32)
    shelf: str | None = Field(None, max_length=32)
    bin: str | None = Field(None, max_length=32)
    location_type: str = Field(
        "STORAGE", max_length=32
    )  # STORAGE, RECEIVING, SHIPPING, PICKING, QUARANTINE
    max_weight: Decimal | None = Field(None, ge=0)
    max_volume: Decimal | None = Field(None, ge=0)
    is_active: bool = True


class LocationCreate(LocationBase):
    warehouse_id: uuid.UUID | None = None


class LocationUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=64)
    name: str | None = Field(None, min_length=1, max_length=128)
    aisle: str | None = Field(None, max_length=32)
    rack: str | None = Field(None, max_length=32)
    shelf: str | None = Field(None, max_length=32)
    bin: str | None = Field(None, max_length=32)
    location_type: str | None = None
    max_weight: Decimal | None = Field(None, ge=0)
    max_volume: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


class LocationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    warehouse_id: uuid.UUID
    code: str
    name: str
    aisle: str | None = None
    rack: str | None = None
    shelf: str | None = None
    bin: str | None = None
    location_type: str
    max_weight: Decimal | None = None
    max_volume: Decimal | None = None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    branch_id: uuid.UUID | None = None
    warehouse_type: str = Field("STANDARD", max_length=32)  # STANDARD, TRANSIT, QUARANTINE, RETURN
    address: dict[str, Any] = Field(default_factory=dict)
    manager_id: uuid.UUID | None = None
    is_primary: bool = False
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    branch_id: uuid.UUID | None = None
    warehouse_type: str | None = None
    address: dict[str, Any] | None = None
    manager_id: uuid.UUID | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class WarehouseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    branch_id: uuid.UUID | None = None
    code: str
    name: str
    warehouse_type: str
    address: dict[str, Any] = Field(default_factory=dict)
    manager_id: uuid.UUID | None = None
    is_primary: bool
    is_active: bool
    version: int
    locations: list[LocationResponse] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseListResponse(BaseModel):
    items: list[WarehouseResponse]
    total: int
    page: int
    page_size: int
