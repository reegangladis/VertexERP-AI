"""Purchase Request Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRequestItemBase(BaseModel):
    product_id: uuid.UUID
    uom_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1, max_length=255)
    quantity: Decimal = Field(..., gt=0)
    estimated_unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    notes: str | None = None


class PurchaseRequestItemCreate(PurchaseRequestItemBase):
    pass


class PurchaseRequestItemResponse(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    product_id: uuid.UUID
    uom_id: uuid.UUID | None = None
    description: str
    quantity: Decimal
    estimated_unit_price: Decimal
    estimated_total: Decimal
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseRequestBase(BaseModel):
    department_id: uuid.UUID | None = None
    required_date: date
    priority: str = Field("MEDIUM", max_length=16)  # LOW, MEDIUM, HIGH, URGENT
    notes: str | None = None
    is_active: bool = True


class PurchaseRequestCreate(PurchaseRequestBase):
    items: list[PurchaseRequestItemCreate] = Field(..., min_length=1)


class PurchaseRequestUpdate(BaseModel):
    department_id: uuid.UUID | None = None
    required_date: date | None = None
    priority: str | None = None
    notes: str | None = None
    items: list[PurchaseRequestItemCreate] | None = None
    is_active: bool | None = None


class PurchaseRequestReject(BaseModel):
    reason: str | None = None


class PurchaseRequestResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    request_number: str
    requester_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    required_date: date
    status: str
    priority: str
    estimated_total: Decimal
    notes: str | None = None
    is_active: bool
    version: int
    items: list[PurchaseRequestItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseRequestListResponse(BaseModel):
    items: list[PurchaseRequestResponse]
    total: int
    page: int
    page_size: int
