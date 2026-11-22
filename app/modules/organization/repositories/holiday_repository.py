"""Holiday repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.holiday import Holiday


class HolidayRepository:
    """Repository for Holiday persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, holiday_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Holiday | None:
        stmt = select(Holiday).where(
            Holiday.id == holiday_id,
            Holiday.tenant_id == tenant_id,
            Holiday.organization_id == org_id,
            Holiday.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        year: int | None = None,
        calendar_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> Sequence[Holiday]:
        stmt = select(Holiday).where(
            Holiday.tenant_id == tenant_id,
            Holiday.organization_id == org_id,
            Holiday.is_deleted.is_(False),
        )
        if year is not None:
            stmt = stmt.where(
                Holiday.holiday_date >= date(year, 1, 1),
                Holiday.holiday_date <= date(year, 12, 31),
            )
        if calendar_id is not None:
            stmt = stmt.where(Holiday.calendar_id == calendar_id)
        if branch_id is not None:
            stmt = stmt.where(Holiday.branch_id == branch_id)

        stmt = stmt.order_by(Holiday.holiday_date.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, holiday: Holiday) -> Holiday:
        self.session.add(holiday)
        await self.session.flush()
        return holiday

    async def update(self, holiday: Holiday) -> Holiday:
        holiday.updated_at = datetime.now(UTC)
        holiday.version += 1
        await self.session.flush()
        return holiday

    async def soft_delete(self, holiday: Holiday) -> None:
        holiday.is_deleted = True
        holiday.deleted_at = datetime.now(UTC)
        holiday.version += 1
        await self.session.flush()
