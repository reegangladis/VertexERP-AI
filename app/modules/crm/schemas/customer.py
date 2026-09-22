"""CRM Customer (Account) Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    customer_type: str = Field("CORPORATE", max_length=32)  # INDIVIDUAL, CORPORATE
    industry: str | None = Field(None, max_length=64)
    website: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=32)
    email: EmailStr | None = None
    tax_id: str | None = Field(None, max_length=64)
    billing_address: dict[str, Any] = Field(default_factory=dict)
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)
    payment_terms: str | None = Field(None, max_length=64)
    status: str = Field("ACTIVE", max_length=32)  # ACTIVE, INACTIVE, PROSPECT, CHURNED
    owner_id: uuid.UUID | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    customer_type: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    tax_id: str | None = None
    billing_address: dict[str, Any] | None = None
    shipping_address: dict[str, Any] | None = None
    credit_limit: Decimal | None = Field(None, ge=0)
    payment_terms: str | None = None
    status: str | None = None
    owner_id: uuid.UUID | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    owner_id: uuid.UUID | None = None
    name: str
    customer_type: str
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    tax_id: str | None = None
    billing_address: dict[str, Any] = Field(default_factory=dict)
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    credit_limit: Decimal
    payment_terms: str | None = None
    status: str
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
