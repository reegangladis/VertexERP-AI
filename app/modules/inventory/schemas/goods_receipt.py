"""Goods Receipt (GRN) Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GoodsReceiptItemBase(BaseModel):
    product_id: uuid.UUID
    po_item_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    quantity_received: Decimal = Field(..., gt=0)
    quantity_accepted: Decimal = Field(..., ge=0)
    quantity_rejected: Decimal = Field(default=Decimal("0.0000"), ge=0)
    rejection_reason: str | None = Field(None, max_length=255)
    unit_cost: Decimal = Field(default=Decimal("0.0000"), ge=0)
    batch_number: str | None = Field(None, max_length=64)
    serial_number: str | None = Field(None, max_length=64)
    expiry_date: date | None = None


class GoodsReceiptItemCreate(GoodsReceiptItemBase):
    pass


class GoodsReceiptItemResponse(BaseModel):
    id: uuid.UUID
    goods_receipt_id: uuid.UUID
    po_item_id: uuid.UUID | None = None
    product_id: uuid.UUID
    location_id: uuid.UUID | None = None
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    rejection_reason: str | None = None
    unit_cost: Decimal
    total_cost: Decimal
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: date | None = None

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptBase(BaseModel):
    supplier_id: uuid.UUID
    warehouse_id: uuid.UUID
    purchase_order_id: uuid.UUID | None = None
    receipt_date: date = Field(default_factory=date.today)
    vendor_delivery_note: str | None = Field(None, max_length=128)
    notes: str | None = None
    is_active: bool = True


class GoodsReceiptCreate(GoodsReceiptBase):
    items: list[GoodsReceiptItemCreate] = Field(..., min_length=1)


class GoodsReceiptUpdate(BaseModel):
    supplier_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None
    purchase_order_id: uuid.UUID | None = None
    receipt_date: date | None = None
    vendor_delivery_note: str | None = None
    notes: str | None = None
    items: list[GoodsReceiptItemCreate] | None = None
    is_active: bool | None = None


class GoodsReceiptResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    receipt_number: str
    purchase_order_id: uuid.UUID | None = None
    supplier_id: uuid.UUID
    warehouse_id: uuid.UUID
    receipt_date: date
    vendor_delivery_note: str | None = None
    status: str
    notes: str | None = None
    received_by_id: uuid.UUID | None = None
    posted_by_id: uuid.UUID | None = None
    posted_at: datetime | None = None
    is_active: bool
    version: int
    items: list[GoodsReceiptItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptListResponse(BaseModel):
    items: list[GoodsReceiptResponse]
    total: int
    page: int
    page_size: int
