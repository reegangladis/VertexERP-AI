"""Pydantic Schemas for Production Orders and Execution."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WorkOrderBase(BaseModel):
    sequence: int
    operation_name: str
    work_center_id: uuid.UUID
    machine_id: uuid.UUID | None = None
    planned_duration_hours: Decimal = Decimal("1.00")
    actual_duration_hours: Decimal = Decimal("0.00")
    technician_id: uuid.UUID | None = None
    status: str = "PENDING"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    hourly_rate: Decimal = Decimal("50.0000")
    total_labor_cost: Decimal = Decimal("0.0000")
    notes: str | None = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(PENDING|IN_PROGRESS|PAUSED|COMPLETED|CANCELLED)$")
    technician_id: uuid.UUID | None = None
    actual_duration_hours: Decimal | None = None
    notes: str | None = None


class WorkOrderRead(WorkOrderBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    production_order_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaterialConsumptionCreate(BaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    work_order_id: uuid.UUID | None = None
    consumed_quantity: Decimal = Field(..., gt=0)
    batch_number: str | None = None


class MaterialConsumptionRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    production_order_id: uuid.UUID
    work_order_id: uuid.UUID | None = None
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    planned_quantity: Decimal
    consumed_quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    stock_movement_id: uuid.UUID | None = None
    batch_number: str | None = None
    consumed_at: datetime
    consumed_by_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionOutputCreate(BaseModel):
    target_warehouse_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    produced_quantity: Decimal = Field(..., gt=0)
    batch_number: str | None = None
    serial_number: str | None = None


class ProductionOutputRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    production_order_id: uuid.UUID
    product_id: uuid.UUID
    target_warehouse_id: uuid.UUID
    location_id: uuid.UUID | None = None
    produced_quantity: Decimal
    unit_manufacturing_cost: Decimal
    total_manufacturing_cost: Decimal
    stock_movement_id: uuid.UUID | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    output_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionScrapCreate(BaseModel):
    product_id: uuid.UUID
    scrap_quantity: Decimal = Field(..., gt=0)
    scrap_reason: str = "DEFECTIVE_RAW_MATERIAL"
    work_order_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None


class ProductionScrapRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    production_order_id: uuid.UUID
    work_order_id: uuid.UUID | None = None
    product_id: uuid.UUID
    scrap_quantity: Decimal
    scrap_reason: str
    unit_cost: Decimal
    total_scrap_cost: Decimal
    stock_movement_id: uuid.UUID | None = None
    recorded_at: datetime
    recorded_by_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionOrderBase(BaseModel):
    product_id: uuid.UUID
    bom_id: uuid.UUID | None = None
    bom_version_id: uuid.UUID | None = None
    routing_id: uuid.UUID | None = None
    source_sales_order_id: uuid.UUID | None = None
    planned_quantity: Decimal = Field(..., gt=0)
    target_warehouse_id: uuid.UUID
    planned_start_date: date
    planned_due_date: date
    priority: str = "MEDIUM"
    notes: str | None = None


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseModel):
    planned_quantity: Decimal | None = None
    target_warehouse_id: uuid.UUID | None = None
    planned_start_date: date | None = None
    planned_due_date: date | None = None
    priority: str | None = None
    notes: str | None = None


class ProductionOrderRead(ProductionOrderBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    order_number: str
    produced_quantity: Decimal
    rejected_quantity: Decimal
    scrap_quantity: Decimal
    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None
    status: str
    unit_cost: Decimal
    total_cost: Decimal
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    work_orders: list[WorkOrderRead] = []
    consumptions: list[MaterialConsumptionRead] = []
    outputs: list[ProductionOutputRead] = []
    scraps: list[ProductionScrapRead] = []

    model_config = ConfigDict(from_attributes=True)
