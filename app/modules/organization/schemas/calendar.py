"""Work Calendar and Working Day schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WorkingDayBase(BaseModel):
    """Base fields for working day."""

    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    is_working_day: bool = True
    start_time: str | None = Field(default="09:00", max_length=8)
    end_time: str | None = Field(default="17:00", max_length=8)


class WorkingDayCreate(WorkingDayBase):
    """Schema for creating working day."""

    pass


class WorkingDayResponse(WorkingDayBase):
    """Response schema for working day."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    calendar_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkCalendarBase(BaseModel):
    """Base fields for work calendar."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique calendar code")
    name: str = Field(..., min_length=1, max_length=128, description="Calendar name")
    description: str | None = Field(None, description="Calendar description")
    time_zone: str = Field(
        default="UTC", max_length=64, description="Timezone name e.g. America/New_York"
    )
    is_default: bool = False
    standard_hours_per_day: Decimal = Field(default=Decimal("8.00"), ge=0, le=24)
    is_active: bool = True


class WorkCalendarCreate(WorkCalendarBase):
    """Schema for creating work calendar with working days."""

    working_days: list[WorkingDayCreate] | None = None


class WorkCalendarUpdate(BaseModel):
    """Schema for updating work calendar."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    time_zone: str | None = Field(None, max_length=64)
    is_default: bool | None = None
    standard_hours_per_day: Decimal | None = Field(None, ge=0, le=24)
    is_active: bool | None = None


class WorkCalendarResponse(WorkCalendarBase):
    """Response schema for work calendar."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
    working_days: list[WorkingDayResponse] = []

    model_config = ConfigDict(from_attributes=True)
