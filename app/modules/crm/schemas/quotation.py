"""CRM Quotation and Line Items Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QuotationItemBase(BaseModel):
    item_type: str = Field("PRODUCT", max_length=32)  # PRODUCT, SERVICE, CUSTOM
    item_code: str | None = Field(None, max_length=64)
    description: str = Field(..., min_length=1, max_length=255)
    quantity: Decimal = Field(default=Decimal("1.0000"), gt=0)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_pct: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_pct: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    sort_order: int = Field(default=0, ge=0)


class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemResponse(BaseModel):
    id: uuid.UUID
    quotation_id: uuid.UUID
    item_type: str
    item_code: str | None = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_pct: Decimal
    line_total: Decimal
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuotationBase(BaseModel):
    customer_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    quotation_date: date = Field(default_factory=date.today)
    valid_until: date
    currency: str = Field("USD", max_length=3)
    status: str = Field(
        "DRAFT", max_length=32
    )  # DRAFT, SENT, ACCEPTED, REJECTED, EXPIRED, CONVERTED
    terms_and_conditions: str | None = None
    notes: str | None = None
    billing_address: dict[str, Any] = Field(default_factory=dict)
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class QuotationCreate(QuotationBase):
    items: list[QuotationItemCreate] = Field(..., min_length=1)


class QuotationUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    quotation_date: date | None = None
    valid_until: date | None = None
    currency: str | None = None
    status: str | None = None
    terms_and_conditions: str | None = None
    notes: str | None = None
    billing_address: dict[str, Any] | None = None
    shipping_address: dict[str, Any] | None = None
    custom_fields: dict[str, Any] | None = None
    items: list[QuotationItemCreate] | None = None
    is_active: bool | None = None


class QuotationConvertToOrderRequest(BaseModel):
    expected_delivery_date: date | None = None
    payment_terms: str | None = None
    shipping_method: str | None = None
    notes: str | None = None


class QuotationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    quotation_number: str
    quotation_date: date
    valid_until: date
    status: str
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    terms_and_conditions: str | None = None
    notes: str | None = None
    billing_address: dict[str, Any] = Field(default_factory=dict)
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    items: list[QuotationItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuotationListResponse(BaseModel):
    items: list[QuotationResponse]
    total: int
    page: int
    page_size: int
