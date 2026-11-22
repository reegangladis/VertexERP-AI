"""Pydantic Schemas for Material Requirements Planning (MRP)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MRPPlannedOrderRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    mrp_run_id: uuid.UUID
    product_id: uuid.UUID
    order_type: str
    gross_requirement: Decimal
    on_hand_stock: Decimal
    scheduled_receipts: Decimal
    net_requirement: Decimal
    planned_quantity: Decimal
    order_date: date
    required_date: date
    status: str
    converted_doc_type: str | None = None
    converted_doc_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MRPRunTrigger(BaseModel):
    planning_horizon_days: int = Field(30, ge=1, le=365)


class MRPRunRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    run_number: str
    planning_horizon_days: int
    status: str
    run_date: datetime
    total_items_planned: int
    total_purchase_requests_generated: int
    total_production_orders_generated: int
    execution_log: str | None = None
    created_at: datetime
    planned_orders: list[MRPPlannedOrderRead] = []

    model_config = ConfigDict(from_attributes=True)
