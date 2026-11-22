"""Holiday schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HolidayBase(BaseModel):
    """Base fields for holiday."""

    name: str = Field(..., min_length=1, max_length=128, description="Holiday name")
    holiday_date: date = Field(..., description="Observed date (YYYY-MM-DD)")
    holiday_type: str = Field(
        default="NATIONAL",
        max_length=32,
        description="Type (NATIONAL, REGIONAL, COMPANY, OPTIONAL)",
    )
    calendar_id: uuid.UUID | None = Field(None, description="Linked Calendar ID")
    branch_id: uuid.UUID | None = Field(None, description="Linked Branch ID")
    is_recurring: bool = False
    description: str | None = None


class HolidayCreate(HolidayBase):
    """Schema for creating holiday."""

    pass


class HolidayUpdate(BaseModel):
    """Schema for updating holiday."""

    name: str | None = Field(None, min_length=1, max_length=128)
    holiday_date: date | None = None
    holiday_type: str | None = Field(None, max_length=32)
    calendar_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    is_recurring: bool | None = None
    description: str | None = None


class HolidayResponse(HolidayBase):
    """Response schema for holiday."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
