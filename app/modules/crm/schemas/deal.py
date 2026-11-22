"""CRM Deal (Opportunity) Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DealBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    pipeline_id: uuid.UUID
    stage_id: uuid.UUID
    customer_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    value: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field("USD", max_length=3)
    expected_close_date: date | None = None
    win_probability_pct: Decimal = Field(default=Decimal("10.00"), ge=0, le=100)
    status: str = Field("OPEN", max_length=32)  # OPEN, WON, LOST
    lost_reason: str | None = Field(None, max_length=255)
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=128)
    pipeline_id: uuid.UUID | None = None
    stage_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    value: Decimal | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=3)
    expected_close_date: date | None = None
    win_probability_pct: Decimal | None = Field(None, ge=0, le=100)
    status: str | None = None
    lost_reason: str | None = None
    notes: str | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class DealStageChangeRequest(BaseModel):
    stage_id: uuid.UUID
    notes: str | None = None
    lost_reason: str | None = None


class DealStageHistoryResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    deal_id: uuid.UUID
    from_stage_id: uuid.UUID | None = None
    to_stage_id: uuid.UUID
    changed_by_user_id: uuid.UUID | None = None
    duration_in_stage_seconds: int | None = None
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DealResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    pipeline_id: uuid.UUID
    stage_id: uuid.UUID
    customer_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    title: str
    value: Decimal
    currency: str
    expected_close_date: date | None = None
    win_probability_pct: Decimal
    status: str
    lost_reason: str | None = None
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DealListResponse(BaseModel):
    items: list[DealResponse]
    total: int
    page: int
    page_size: int
