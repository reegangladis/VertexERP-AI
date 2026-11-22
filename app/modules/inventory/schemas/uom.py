"""Unit of Measure (UoM) Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UomBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=16)
    name: str = Field(..., min_length=1, max_length=64)
    category: str = Field("COUNT", max_length=32)  # COUNT, WEIGHT, VOLUME, LENGTH, TIME, AREA
    is_base_unit: bool = True
    conversion_factor: Decimal = Field(default=Decimal("1.000000"), gt=0)
    base_unit_id: uuid.UUID | None = None
    is_active: bool = True


class UomCreate(UomBase):
    pass


class UomUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=16)
    name: str | None = Field(None, min_length=1, max_length=64)
    category: str | None = None
    is_base_unit: bool | None = None
    conversion_factor: Decimal | None = Field(None, gt=0)
    base_unit_id: uuid.UUID | None = None
    is_active: bool | None = None


class UomResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    category: str
    is_base_unit: bool
    conversion_factor: Decimal
    base_unit_id: uuid.UUID | None = None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UomListResponse(BaseModel):
    items: list[UomResponse]
    total: int
    page: int
    page_size: int
