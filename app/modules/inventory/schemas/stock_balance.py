"""Stock Balance Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StockBalanceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_allocated: Decimal
    quantity_available: Decimal
    average_cost: Decimal
    total_value: Decimal
    last_movement_at: datetime | None = None
    version: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockBalanceListResponse(BaseModel):
    items: list[StockBalanceResponse]
    total: int
    page: int
    page_size: int


class StockValuationSummary(BaseModel):
    total_items: int
    total_quantity_on_hand: Decimal
    total_valuation: Decimal
