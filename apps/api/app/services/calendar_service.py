import uuid

from fastapi import HTTPException, status

from app.models.calendar import BusinessCalendar, Holiday, WorkingDay
from app.repositories.calendar import (
    BusinessCalendarRepository,
    HolidayRepository,
    WorkingDayRepository,
)
from app.schemas.calendar import (
    BusinessCalendarCreate,
    BusinessCalendarUpdate,
    HolidayCreate,
    WorkingDayCreate,
)
from app.services.base import BaseService


class CalendarService(
    BaseService[BusinessCalendar, BusinessCalendarRepository]
):
    def __init__(
        self,
        repository: BusinessCalendarRepository,
        holiday_repo: HolidayRepository,
        working_day_repo: WorkingDayRepository,
    ):
        super().__init__(repository)
        self.holiday_repo = holiday_repo
        self.working_day_repo = working_day_repo

    async def get_by_org(self, org_id: uuid.UUID) -> list[BusinessCalendar]:
        return await self.repository.get_by_org_id(org_id)

    async def get_calendar_details(self, calendar_id: uuid.UUID) -> BusinessCalendar:
        cal = await self.repository.get_with_details(calendar_id)
        if not cal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business calendar not found.",
            )
        return cal

    async def add_holiday(
        self, calendar_id: uuid.UUID, obj_in: HolidayCreate
    ) -> Holiday:
        await self.get_calendar_details(calendar_id)
        return await self.holiday_repo.create(
            {**obj_in.model_dump(), "calendar_id": calendar_id}
        )

    async def add_working_day(
        self, calendar_id: uuid.UUID, obj_in: WorkingDayCreate
    ) -> WorkingDay:
        await self.get_calendar_details(calendar_id)
        return await self.working_day_repo.create(
            {**obj_in.model_dump(), "calendar_id": calendar_id}
        )
