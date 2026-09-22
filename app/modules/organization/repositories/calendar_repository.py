"""Work Calendar repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.calendar import WorkCalendar, WorkingDay


class CalendarRepository:
    """Repository for WorkCalendar and WorkingDay persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, cal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> WorkCalendar | None:
        stmt = select(WorkCalendar).where(
            WorkCalendar.id == cal_id,
            WorkCalendar.tenant_id == tenant_id,
            WorkCalendar.organization_id == org_id,
            WorkCalendar.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> WorkCalendar | None:
        stmt = select(WorkCalendar).where(
            WorkCalendar.code == code,
            WorkCalendar.tenant_id == tenant_id,
            WorkCalendar.organization_id == org_id,
            WorkCalendar.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[WorkCalendar]:
        stmt = select(WorkCalendar).where(
            WorkCalendar.tenant_id == tenant_id,
            WorkCalendar.organization_id == org_id,
            WorkCalendar.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(WorkCalendar.is_active.is_(is_active))
        stmt = stmt.order_by(WorkCalendar.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, cal: WorkCalendar) -> WorkCalendar:
        self.session.add(cal)
        await self.session.flush()
        return cal

    async def update(self, cal: WorkCalendar) -> WorkCalendar:
        cal.updated_at = datetime.now(UTC)
        cal.version += 1
        await self.session.flush()
        return cal

    async def soft_delete(self, cal: WorkCalendar) -> None:
        cal.is_deleted = True
        cal.deleted_at = datetime.now(UTC)
        cal.version += 1
        await self.session.flush()

    # Working Days
    async def get_working_days(
        self, tenant_id: uuid.UUID, calendar_id: uuid.UUID
    ) -> Sequence[WorkingDay]:
        stmt = (
            select(WorkingDay)
            .where(
                WorkingDay.tenant_id == tenant_id,
                WorkingDay.calendar_id == calendar_id,
            )
            .order_by(WorkingDay.day_of_week.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_working_days(
        self, tenant_id: uuid.UUID, calendar_id: uuid.UUID, days: list[WorkingDay]
    ) -> Sequence[WorkingDay]:
        # remove old
        existing = await self.get_working_days(tenant_id, calendar_id)
        for d in existing:
            await self.session.delete(d)
        await self.session.flush()

        for d in days:
            self.session.add(d)
        await self.session.flush()
        return days
