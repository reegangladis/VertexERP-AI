"""Fiscal Years and Fiscal Periods Pydantic Schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FiscalPeriodBase(BaseModel):
    period_number: int = Field(..., ge=1, le=16)
    period_name: str = Field(..., min_length=1, max_length=64)
    start_date: date
    end_date: date
    is_locked: bool = False
    is_closed: bool = False


class FiscalPeriodCreate(FiscalPeriodBase):
    pass


class FiscalPeriodResponse(FiscalPeriodBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    fiscal_year_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FiscalYearBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    start_date: date
    end_date: date
    is_closed: bool = False


class FiscalYearCreate(FiscalYearBase):
    periods: list[FiscalPeriodCreate] = Field(default_factory=list)


class FiscalYearResponse(FiscalYearBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    periods: list[FiscalPeriodResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FiscalYearListResponse(BaseModel):
    items: list[FiscalYearResponse]
    total: int
    page: int
    page_size: int


class FiscalPeriodListResponse(BaseModel):
    items: list[FiscalPeriodResponse]
    total: int
    page: int
    page_size: int

