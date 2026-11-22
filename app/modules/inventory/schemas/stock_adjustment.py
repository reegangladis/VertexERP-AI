"""Stock Adjustment Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StockAdjustmentItemBase(BaseModel):
    product_id: uuid.UUID
    location_id: uuid.UUID | None = None
    system_quantity: Decimal = Field(default=Decimal("0.0000"), ge=0)
    counted_quantity: Decimal = Field(default=Decimal("0.0000"), ge=0)
    unit_cost: Decimal = Field(default=Decimal("0.0000"), ge=0)
    adjustment_type: str = Field("INCREASE", max_length=16)  # INCREASE, DECREASE
    batch_number: str | None = Field(None, max_length=64)


class StockAdjustmentItemCreate(StockAdjustmentItemBase):
    pass


class StockAdjustmentItemResponse(BaseModel):
    id: uuid.UUID
    adjustment_id: uuid.UUID
    product_id: uuid.UUID
    location_id: uuid.UUID | None = None
    system_quantity: Decimal
    counted_quantity: Decimal
    difference_quantity: Decimal
    unit_cost: Decimal
    total_adjustment_value: Decimal
    adjustment_type: str
    batch_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentBase(BaseModel):
    warehouse_id: uuid.UUID
    reason: str = Field("INVENTORY_COUNT_DISCREPANCY", max_length=64)
    adjustment_date: date = Field(default_factory=date.today)
    notes: str | None = None
    is_active: bool = True


class StockAdjustmentCreate(StockAdjustmentBase):
    items: list[StockAdjustmentItemCreate] = Field(..., min_length=1)


class StockAdjustmentUpdate(BaseModel):
    warehouse_id: uuid.UUID | None = None
    reason: str | None = None
    adjustment_date: date | None = None
    notes: str | None = None
    items: list[StockAdjustmentItemCreate] | None = None
    is_active: bool | None = None


class StockAdjustmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    adjustment_number: str
    warehouse_id: uuid.UUID
    reason: str
    status: str
    adjustment_date: date
    requested_by_id: uuid.UUID | None = None
    approved_by_id: uuid.UUID | None = None
    posted_at: datetime | None = None
    notes: str | None = None
    is_active: bool
    version: int
    items: list[StockAdjustmentItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentListResponse(BaseModel):
    items: list[StockAdjustmentResponse]
    total: int
    page: int
    page_size: int
