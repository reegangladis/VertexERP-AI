"""Financial Customer and Vendor Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerPartyBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    tax_id: str | None = Field(None, max_length=64)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=64)
    credit_limit: Decimal = Field(Decimal("0.0000"), ge=0)
    ar_account_id: uuid.UUID | None = None
    payment_terms_days: int = Field(30, ge=0)
    is_active: bool = True


class CustomerPartyCreate(CustomerPartyBase):
    pass


class CustomerPartyResponse(CustomerPartyBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorPartyBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    tax_id: str | None = Field(None, max_length=64)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=64)
    ap_account_id: uuid.UUID | None = None
    payment_terms_days: int = Field(30, ge=0)
    is_active: bool = True


class VendorPartyCreate(VendorPartyBase):
    pass


class VendorPartyResponse(VendorPartyBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerPartyResponse]
    total: int
    page: int
    page_size: int


class VendorListResponse(BaseModel):
    items: list[VendorPartyResponse]
    total: int
    page: int
    page_size: int
