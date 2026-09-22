"""Holiday service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.organization.models.holiday import Holiday
from app.modules.organization.repositories.holiday_repository import HolidayRepository
from app.modules.organization.schemas.holiday import HolidayCreate, HolidayUpdate


class HolidayService:
    """Business service for Holiday management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.holiday_repo = HolidayRepository(session)

    async def create_holiday(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: HolidayCreate
    ) -> Holiday:
        holiday = Holiday(
            tenant_id=tenant_id,
            organization_id=org_id,
            calendar_id=data.calendar_id,
            branch_id=data.branch_id,
            name=data.name,
            holiday_date=data.holiday_date,
            holiday_type=data.holiday_type,
            is_recurring=data.is_recurring,
            description=data.description,
        )
        return await self.holiday_repo.create(holiday)

    async def get_holiday(
        self, holiday_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Holiday:
        holiday = await self.holiday_repo.get_by_id(holiday_id, tenant_id, org_id)
        if not holiday:
            raise NotFoundException(f"Holiday '{holiday_id}' not found")
        return holiday

    async def list_holidays(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        year: int | None = None,
        calendar_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> Sequence[Holiday]:
        return await self.holiday_repo.list_by_org(tenant_id, org_id, year, calendar_id, branch_id)

    async def update_holiday(
        self, holiday_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: HolidayUpdate
    ) -> Holiday:
        holiday = await self.get_holiday(holiday_id, tenant_id, org_id)

        if data.name is not None:
            holiday.name = data.name
        if data.holiday_date is not None:
            holiday.holiday_date = data.holiday_date
        if data.holiday_type is not None:
            holiday.holiday_type = data.holiday_type
        if data.calendar_id is not None:
            holiday.calendar_id = data.calendar_id
        if data.branch_id is not None:
            holiday.branch_id = data.branch_id
        if data.is_recurring is not None:
            holiday.is_recurring = data.is_recurring
        if data.description is not None:
            holiday.description = data.description

        return await self.holiday_repo.update(holiday)

    async def delete_holiday(
        self, holiday_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        holiday = await self.get_holiday(holiday_id, tenant_id, org_id)
        await self.holiday_repo.soft_delete(holiday)
