"""Purchase Order Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderItemBase(BaseModel):
    product_id: uuid.UUID
    uom_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1, max_length=255)
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_pct: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_pct: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemResponse(BaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    product_id: uuid.UUID
    uom_id: uuid.UUID | None = None
    description: str
    quantity_ordered: Decimal
    quantity_received: Decimal
    quantity_billed: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_pct: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    supplier_id: uuid.UUID
    warehouse_id: uuid.UUID
    purchase_request_id: uuid.UUID | None = None
    order_date: date = Field(default_factory=date.today)
    expected_delivery_date: date | None = None
    payment_terms: str | None = Field("NET_30", max_length=64)
    currency: str = Field("USD", max_length=3)
    shipping_terms: str | None = None
    notes: str | None = None
    is_active: bool = True


class PurchaseOrderCreate(PurchaseOrderBase):
    items: list[PurchaseOrderItemCreate] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    supplier_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None
    purchase_request_id: uuid.UUID | None = None
    order_date: date | None = None
    expected_delivery_date: date | None = None
    payment_terms: str | None = None
    currency: str | None = None
    shipping_terms: str | None = None
    notes: str | None = None
    items: list[PurchaseOrderItemCreate] | None = None
    is_active: bool | None = None


class PurchaseOrderCancel(BaseModel):
    reason: str | None = None


class PurchaseOrderResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    po_number: str
    supplier_id: uuid.UUID
    warehouse_id: uuid.UUID
    purchase_request_id: uuid.UUID | None = None
    order_date: date
    expected_delivery_date: date | None = None
    payment_terms: str | None = None
    currency: str
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    shipping_terms: str | None = None
    notes: str | None = None
    approved_by_id: uuid.UUID | None = None
    approved_at: datetime | None = None
    is_active: bool
    version: int
    items: list[PurchaseOrderItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderListResponse(BaseModel):
    items: list[PurchaseOrderResponse]
    total: int
    page: int
    page_size: int
