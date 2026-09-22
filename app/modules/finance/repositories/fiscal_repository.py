"""Fiscal Year and Fiscal Period Repository."""

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.fiscal import FiscalPeriod, FiscalYear


class FiscalRepository:
    """Repository for Fiscal Years & Periods with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_year_by_id(
        self, year_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> FiscalYear | None:
        stmt = (
            select(FiscalYear)
            .options(selectinload(FiscalYear.periods))
            .where(
                FiscalYear.id == year_id,
                FiscalYear.tenant_id == tenant_id,
                FiscalYear.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_period_by_id(
        self, period_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> FiscalPeriod | None:
        stmt = select(FiscalPeriod).where(
            FiscalPeriod.id == period_id,
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_period_for_date(
        self, target_date: date, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> FiscalPeriod | None:
        stmt = select(FiscalPeriod).where(
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.organization_id == org_id,
            FiscalPeriod.start_date <= target_date,
            FiscalPeriod.end_date >= target_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_years_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[FiscalYear]:
        stmt = (
            select(FiscalYear)
            .options(selectinload(FiscalYear.periods))
            .where(
                FiscalYear.tenant_id == tenant_id,
                FiscalYear.organization_id == org_id,
            )
            .order_by(FiscalYear.start_date.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_years_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(FiscalYear.id)).where(
            FiscalYear.tenant_id == tenant_id,
            FiscalYear.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def list_periods_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        fiscal_year_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[FiscalPeriod]:
        stmt = select(FiscalPeriod).where(
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.organization_id == org_id,
        )
        if fiscal_year_id:
            stmt = stmt.where(FiscalPeriod.fiscal_year_id == fiscal_year_id)
        stmt = stmt.order_by(FiscalPeriod.start_date.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_periods_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        fiscal_year_id: uuid.UUID | None = None,
    ) -> int:
        stmt = select(func.count(FiscalPeriod.id)).where(
            FiscalPeriod.tenant_id == tenant_id,
            FiscalPeriod.organization_id == org_id,
        )
        if fiscal_year_id:
            stmt = stmt.where(FiscalPeriod.fiscal_year_id == fiscal_year_id)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create_year(self, year: FiscalYear) -> FiscalYear:
        self.session.add(year)
        await self.session.flush()
        return year
