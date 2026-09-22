"""Pydantic Schemas for Quality Inspections."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QualityInspectionBase(BaseModel):
    production_order_id: uuid.UUID
    work_order_id: uuid.UUID | None = None
    product_id: uuid.UUID
    inspection_type: str = "FINAL_ASSEMBLY"
    inspected_quantity: Decimal = Field(..., gt=0)
    passed_quantity: Decimal = Decimal("0.0000")
    failed_quantity: Decimal = Decimal("0.0000")
    result: str = "PASSED"
    defect_reason: str | None = None
    notes: str | None = None


class QualityInspectionCreate(QualityInspectionBase):
    pass


class QualityInspectionUpdate(BaseModel):
    passed_quantity: Decimal | None = None
    failed_quantity: Decimal | None = None
    result: str | None = None
    defect_reason: str | None = None
    notes: str | None = None
    status: str | None = None


class QualityInspectionRead(QualityInspectionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    inspection_number: str
    inspector_id: uuid.UUID | None = None
    inspection_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
