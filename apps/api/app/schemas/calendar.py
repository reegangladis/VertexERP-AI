from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HolidayBase(BaseModel):
    date: date
    name: str
    type: str = "public"


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    calendar_id: UUID
    created_at: datetime
    updated_at: datetime


class WorkingDayBase(BaseModel):
    weekday: int
    start_time: str = "09:00"
    end_time: str = "17:00"
    is_working: bool = True


class WorkingDayCreate(WorkingDayBase):
    pass


class WorkingDayResponse(WorkingDayBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    calendar_id: UUID
    created_at: datetime
    updated_at: datetime


class BusinessCalendarBase(BaseModel):
    name: str
    timezone: str = "UTC"
    country: str | None = None


class BusinessCalendarCreate(BusinessCalendarBase):
    organization_id: UUID


class BusinessCalendarUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None
    country: str | None = None


class BusinessCalendarResponse(BusinessCalendarBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    holidays: list[HolidayResponse] = []
    working_days: list[WorkingDayResponse] = []
    created_at: datetime
    updated_at: datetime
