"""Stock Transfer Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StockTransferItemBase(BaseModel):
    product_id: uuid.UUID
    from_location_id: uuid.UUID | None = None
    to_location_id: uuid.UUID | None = None
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(default=Decimal("0.0000"), ge=0)
    batch_number: str | None = Field(None, max_length=64)


class StockTransferItemCreate(StockTransferItemBase):
    pass


class StockTransferItemResponse(BaseModel):
    id: uuid.UUID
    transfer_id: uuid.UUID
    product_id: uuid.UUID
    from_location_id: uuid.UUID | None = None
    to_location_id: uuid.UUID | None = None
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    batch_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StockTransferBase(BaseModel):
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    transfer_date: date = Field(default_factory=date.today)
    expected_arrival_date: date | None = None
    notes: str | None = None
    is_active: bool = True


class StockTransferCreate(StockTransferBase):
    items: list[StockTransferItemCreate] = Field(..., min_length=1)


class StockTransferUpdate(BaseModel):
    from_warehouse_id: uuid.UUID | None = None
    to_warehouse_id: uuid.UUID | None = None
    transfer_date: date | None = None
    expected_arrival_date: date | None = None
    notes: str | None = None
    items: list[StockTransferItemCreate] | None = None
    is_active: bool | None = None


class StockTransferResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    transfer_number: str
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    status: str
    transfer_date: date
    expected_arrival_date: date | None = None
    shipped_at: datetime | None = None
    received_at: datetime | None = None
    created_by_id: uuid.UUID | None = None
    notes: str | None = None
    is_active: bool
    version: int
    items: list[StockTransferItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockTransferListResponse(BaseModel):
    items: list[StockTransferResponse]
    total: int
    page: int
    page_size: int
