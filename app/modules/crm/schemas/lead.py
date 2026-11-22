"""CRM Lead Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    company_name: str | None = Field(None, max_length=128)
    email: EmailStr
    phone: str | None = Field(None, max_length=32)
    title: str | None = Field(None, max_length=64)
    source: str = Field(
        "WEBSITE", max_length=32
    )  # WEBSITE, REFERRAL, COLD_CALL, CAMPAIGN, EVENT, OTHER
    status: str = Field("NEW", max_length=32)  # NEW, CONTACTED, QUALIFIED, UNQUALIFIED, CONVERTED
    rating: str = Field("WARM", max_length=16)  # HOT, WARM, COLD
    estimated_value: Decimal = Field(default=Decimal("0.00"), ge=0)
    owner_id: uuid.UUID | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=64)
    last_name: str | None = Field(None, min_length=1, max_length=64)
    company_name: str | None = Field(None, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=32)
    title: str | None = Field(None, max_length=64)
    source: str | None = None
    status: str | None = None
    rating: str | None = None
    estimated_value: Decimal | None = Field(None, ge=0)
    owner_id: uuid.UUID | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class LeadConvertRequest(BaseModel):
    """Request payload to atomically convert a lead into a customer, contact, and deal."""

    customer_name: str | None = None
    deal_title: str | None = None
    pipeline_id: uuid.UUID | None = None
    stage_id: uuid.UUID | None = None
    deal_value: Decimal | None = None
    create_deal: bool = True


class LeadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    owner_id: uuid.UUID | None = None
    first_name: str
    last_name: str
    company_name: str | None = None
    email: str
    phone: str | None = None
    title: str | None = None
    source: str
    status: str
    rating: str
    estimated_value: Decimal
    converted_customer_id: uuid.UUID | None = None
    converted_contact_id: uuid.UUID | None = None
    converted_deal_id: uuid.UUID | None = None
    converted_at: datetime | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
