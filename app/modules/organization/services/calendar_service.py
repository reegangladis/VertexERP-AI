"""Work Calendar service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.calendar import WorkCalendar, WorkingDay
from app.modules.organization.repositories.calendar_repository import CalendarRepository
from app.modules.organization.schemas.calendar import (
    WorkCalendarCreate,
    WorkCalendarResponse,
    WorkCalendarUpdate,
    WorkingDayCreate,
    WorkingDayResponse,
)


class CalendarService:
    """Business service for Work Calendar and Working Day management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.cal_repo = CalendarRepository(session)

    async def create_calendar(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: WorkCalendarCreate
    ) -> WorkCalendarResponse:
        existing = await self.cal_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Calendar with code '{data.code}' already exists in this organization"
            )

        cal = WorkCalendar(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            description=data.description,
            time_zone=data.time_zone,
            is_default=data.is_default,
            standard_hours_per_day=data.standard_hours_per_day,
            is_active=data.is_active,
        )
        await self.cal_repo.create(cal)

        # Create working days (default Mon-Fri if not provided)
        working_days_list: list[WorkingDay] = []
        if data.working_days:
            for wd in data.working_days:
                working_days_list.append(
                    WorkingDay(
                        tenant_id=tenant_id,
                        calendar_id=cal.id,
                        day_of_week=wd.day_of_week,
                        is_working_day=wd.is_working_day,
                        start_time=wd.start_time,
                        end_time=wd.end_time,
                    )
                )
        else:
            for day in range(7):
                is_work = day < 5  # Mon-Fri
                working_days_list.append(
                    WorkingDay(
                        tenant_id=tenant_id,
                        calendar_id=cal.id,
                        day_of_week=day,
                        is_working_day=is_work,
                        start_time="09:00" if is_work else None,
                        end_time="17:00" if is_work else None,
                    )
                )
        saved_days = await self.cal_repo.save_working_days(tenant_id, cal.id, working_days_list)

        return WorkCalendarResponse(
            id=cal.id,
            tenant_id=cal.tenant_id,
            organization_id=cal.organization_id,
            code=cal.code,
            name=cal.name,
            description=cal.description,
            time_zone=cal.time_zone,
            is_default=cal.is_default,
            standard_hours_per_day=cal.standard_hours_per_day,
            is_active=cal.is_active,
            version=cal.version,
            created_at=cal.created_at,
            updated_at=cal.updated_at,
            working_days=[
                WorkingDayResponse(
                    id=wd.id,
                    tenant_id=wd.tenant_id,
                    calendar_id=wd.calendar_id,
                    day_of_week=wd.day_of_week,
                    is_working_day=wd.is_working_day,
                    start_time=wd.start_time,
                    end_time=wd.end_time,
                    created_at=wd.created_at,
                )
                for wd in saved_days
            ],
        )

    async def get_calendar(
        self, cal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> WorkCalendarResponse:
        cal = await self.cal_repo.get_by_id(cal_id, tenant_id, org_id)
        if not cal:
            raise NotFoundException(f"Work calendar '{cal_id}' not found")
        days = await self.cal_repo.get_working_days(tenant_id, cal.id)

        return WorkCalendarResponse(
            id=cal.id,
            tenant_id=cal.tenant_id,
            organization_id=cal.organization_id,
            code=cal.code,
            name=cal.name,
            description=cal.description,
            time_zone=cal.time_zone,
            is_default=cal.is_default,
            standard_hours_per_day=cal.standard_hours_per_day,
            is_active=cal.is_active,
            version=cal.version,
            created_at=cal.created_at,
            updated_at=cal.updated_at,
            working_days=[
                WorkingDayResponse(
                    id=wd.id,
                    tenant_id=wd.tenant_id,
                    calendar_id=wd.calendar_id,
                    day_of_week=wd.day_of_week,
                    is_working_day=wd.is_working_day,
                    start_time=wd.start_time,
                    end_time=wd.end_time,
                    created_at=wd.created_at,
                )
                for wd in days
            ],
        )

    async def list_calendars(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[WorkCalendar]:
        return await self.cal_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_calendar(
        self, cal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: WorkCalendarUpdate
    ) -> WorkCalendar:
        cal = await self.cal_repo.get_by_id(cal_id, tenant_id, org_id)
        if not cal:
            raise NotFoundException(f"Work calendar '{cal_id}' not found")

        if data.code is not None and data.code != cal.code:
            existing = await self.cal_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != cal.id:
                raise ConflictException(f"Calendar with code '{data.code}' already exists")
            cal.code = data.code

        if data.name is not None:
            cal.name = data.name
        if data.description is not None:
            cal.description = data.description
        if data.time_zone is not None:
            cal.time_zone = data.time_zone
        if data.is_default is not None:
            cal.is_default = data.is_default
        if data.standard_hours_per_day is not None:
            cal.standard_hours_per_day = data.standard_hours_per_day
        if data.is_active is not None:
            cal.is_active = data.is_active

        return await self.cal_repo.update(cal)

    async def update_working_days(
        self,
        cal_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        days_in: list[WorkingDayCreate],
    ) -> Sequence[WorkingDay]:
        await self.cal_repo.get_by_id(cal_id, tenant_id, org_id)
        working_days = [
            WorkingDay(
                tenant_id=tenant_id,
                calendar_id=cal_id,
                day_of_week=d.day_of_week,
                is_working_day=d.is_working_day,
                start_time=d.start_time,
                end_time=d.end_time,
            )
            for d in days_in
        ]
        return await self.cal_repo.save_working_days(tenant_id, cal_id, working_days)

    async def delete_calendar(
        self, cal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        cal = await self.cal_repo.get_by_id(cal_id, tenant_id, org_id)
        if not cal:
            raise NotFoundException(f"Work calendar '{cal_id}' not found")
        await self.cal_repo.soft_delete(cal)
