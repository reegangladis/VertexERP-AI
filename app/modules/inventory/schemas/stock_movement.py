"""Stock Movement (Ledger) Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StockMovementCreate(BaseModel):
    movement_type: str = Field(..., max_length=32)
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    batch_number: str | None = Field(None, max_length=64)
    serial_number: str | None = Field(None, max_length=64)
    expiry_date: date | None = None
    quantity: Decimal
    unit_cost: Decimal = Field(default=Decimal("0.0000"), ge=0)
    reference_doc_type: str | None = None
    reference_doc_id: uuid.UUID | None = None
    reference_doc_line_id: uuid.UUID | None = None
    notes: str | None = None


class StockMovementResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    movement_number: str
    movement_type: str
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: date | None = None
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    reference_doc_type: str | None = None
    reference_doc_id: uuid.UUID | None = None
    reference_doc_line_id: uuid.UUID | None = None
    running_balance_qty: Decimal
    running_balance_cost: Decimal
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StockMovementListResponse(BaseModel):
    items: list[StockMovementResponse]
    total: int
    page: int
    page_size: int
