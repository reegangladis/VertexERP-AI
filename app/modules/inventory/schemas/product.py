"""Product / Item Master Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    barcode: str | None = Field(None, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    category_id: uuid.UUID | None = None
    uom_id: uuid.UUID
    valuation_method: str = Field(
        "AVERAGE_COST", max_length=32
    )  # FIFO, LIFO, AVERAGE_COST, STANDARD_COST
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    selling_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    reorder_point: Decimal = Field(default=Decimal("0.0000"), ge=0)
    reorder_quantity: Decimal = Field(default=Decimal("0.0000"), ge=0)
    safety_stock: Decimal = Field(default=Decimal("0.0000"), ge=0)
    min_order_qty: Decimal = Field(default=Decimal("1.0000"), gt=0)
    lead_time_days: int = Field(default=7, ge=0)
    is_stockable: bool = True
    is_purchasable: bool = True
    is_sellable: bool = True
    allow_negative_stock: bool = False
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=64)
    barcode: str | None = Field(None, max_length=64)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    category_id: uuid.UUID | None = None
    uom_id: uuid.UUID | None = None
    valuation_method: str | None = None
    cost_price: Decimal | None = Field(None, ge=0)
    selling_price: Decimal | None = Field(None, ge=0)
    reorder_point: Decimal | None = Field(None, ge=0)
    reorder_quantity: Decimal | None = Field(None, ge=0)
    safety_stock: Decimal | None = Field(None, ge=0)
    min_order_qty: Decimal | None = Field(None, gt=0)
    lead_time_days: int | None = Field(None, ge=0)
    is_stockable: bool | None = None
    is_purchasable: bool | None = None
    is_sellable: bool | None = None
    allow_negative_stock: bool | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    sku: str
    barcode: str | None = None
    name: str
    description: str | None = None
    category_id: uuid.UUID | None = None
    uom_id: uuid.UUID
    valuation_method: str
    cost_price: Decimal
    selling_price: Decimal
    reorder_point: Decimal
    reorder_quantity: Decimal
    safety_stock: Decimal
    min_order_qty: Decimal
    lead_time_days: int
    is_stockable: bool
    is_purchasable: bool
    is_sellable: bool
    allow_negative_stock: bool
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
