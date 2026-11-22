"""Supplier / Vendor Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    contact_name: str | None = Field(None, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=32)
    website: str | None = Field(None, max_length=255)
    tax_id: str | None = Field(None, max_length=64)
    currency: str = Field("USD", max_length=3)
    payment_terms: str | None = Field("NET_30", max_length=64)
    lead_time_days: int = Field(default=7, ge=0)
    address: dict[str, Any] = Field(default_factory=dict)
    status: str = Field("ACTIVE", max_length=32)  # ACTIVE, INACTIVE, BLOCKED
    rating: Decimal = Field(default=Decimal("5.00"), ge=0, le=5)
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    contact_name: str | None = Field(None, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=32)
    website: str | None = Field(None, max_length=255)
    tax_id: str | None = Field(None, max_length=64)
    currency: str | None = None
    payment_terms: str | None = None
    lead_time_days: int | None = Field(None, ge=0)
    address: dict[str, Any] | None = None
    status: str | None = None
    rating: Decimal | None = Field(None, ge=0, le=5)
    notes: str | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    tax_id: str | None = None
    currency: str
    payment_terms: str | None = None
    lead_time_days: int
    address: dict[str, Any] = Field(default_factory=dict)
    status: str
    rating: Decimal
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierListResponse(BaseModel):
    items: list[SupplierResponse]
    total: int
    page: int
    page_size: int
