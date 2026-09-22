"""Pydantic Schemas for Manufacturing Routings."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RoutingOperationBase(BaseModel):
    sequence: int = Field(..., ge=1)
    operation_name: str = Field(..., max_length=128)
    work_center_id: uuid.UUID
    preferred_machine_id: uuid.UUID | None = None
    setup_time_hours: Decimal = Decimal("0.50")
    run_time_per_unit_hours: Decimal = Decimal("0.1000")
    description: str | None = None


class RoutingOperationCreate(RoutingOperationBase):
    routing_id: uuid.UUID | None = None


class RoutingOperationRead(RoutingOperationBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    routing_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoutingBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=128)
    product_id: uuid.UUID
    description: str | None = None
    version: str = "1.0"
    is_active: bool = True


class RoutingCreate(RoutingBase):
    operations: list[RoutingOperationCreate] = []


class RoutingUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    version: str | None = None
    is_active: bool | None = None


class RoutingRead(RoutingBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    operations: list[RoutingOperationRead] = []

    model_config = ConfigDict(from_attributes=True)
