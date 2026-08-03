import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.calendar import BusinessCalendar, Holiday, WorkingDay
from app.repositories.base import BaseRepository


class BusinessCalendarRepository(BaseRepository[BusinessCalendar]):
    def __init__(self, db: AsyncSession):
        super().__init__(BusinessCalendar, db)

    async def get_with_details(self, calendar_id: uuid.UUID) -> BusinessCalendar | None:
        stmt = (
            select(BusinessCalendar)
            .options(
                selectinload(BusinessCalendar.holidays),
                selectinload(BusinessCalendar.working_days),
            )
            .where(
                BusinessCalendar.id == calendar_id,
                BusinessCalendar.is_deleted == False,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[BusinessCalendar]:
        stmt = (
            select(BusinessCalendar)
            .options(
                selectinload(BusinessCalendar.holidays),
                selectinload(BusinessCalendar.working_days),
            )
            .where(
                BusinessCalendar.organization_id == org_id,
                BusinessCalendar.is_deleted == False,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class HolidayRepository(BaseRepository[Holiday]):
    def __init__(self, db: AsyncSession):
        super().__init__(Holiday, db)


class WorkingDayRepository(BaseRepository[WorkingDay]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkingDay, db)
