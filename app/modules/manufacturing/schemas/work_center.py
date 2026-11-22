"""Pydantic Schemas for Work Centers and Machines."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MachineBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=128)
    serial_number: str | None = None
    hourly_cost: Decimal = Decimal("30.0000")
    status: str = "OPERATIONAL"
    last_maintenance_date: date | None = None
    next_maintenance_date: date | None = None


class MachineCreate(MachineBase):
    work_center_id: uuid.UUID


class MachineUpdate(BaseModel):
    name: str | None = None
    serial_number: str | None = None
    hourly_cost: Decimal | None = None
    status: str | None = None
    last_maintenance_date: date | None = None
    next_maintenance_date: date | None = None


class MachineRead(MachineBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    work_center_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MachineListResponse(BaseModel):
    items: list[MachineRead]
    total: int
    page: int
    page_size: int



class WorkCenterBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=128)
    work_center_type: str = "MACHINING"
    capacity_per_day_hours: Decimal = Decimal("8.00")
    cost_per_hour: Decimal = Decimal("50.0000")
    overhead_cost_per_hour: Decimal = Decimal("20.0000")
    location_id: uuid.UUID | None = None
    status: str = "ACTIVE"
    is_active: bool = True


class WorkCenterCreate(WorkCenterBase):
    pass


class WorkCenterUpdate(BaseModel):
    name: str | None = None
    work_center_type: str | None = None
    capacity_per_day_hours: Decimal | None = None
    cost_per_hour: Decimal | None = None
    overhead_cost_per_hour: Decimal | None = None
    location_id: uuid.UUID | None = None
    status: str | None = None
    is_active: bool | None = None


class WorkCenterRead(WorkCenterBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    machines: list[MachineRead] = []

    model_config = ConfigDict(from_attributes=True)
