"""Repository for MRP Runs and Planned Orders."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.manufacturing.models.mrp import MRPPlannedOrder, MRPRun


class MRPRepository:
    """Database repository for MRP calculation runs and planned order releases."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(self, run: MRPRun) -> MRPRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run_by_id(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> MRPRun | None:
        stmt = (
            select(MRPRun)
            .where(
                MRPRun.id == run_id,
                MRPRun.tenant_id == tenant_id,
                MRPRun.organization_id == org_id,
            )
            .options(selectinload(MRPRun.planned_orders))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_runs(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[MRPRun], int]:
        query = select(MRPRun).where(
            MRPRun.tenant_id == tenant_id,
            MRPRun.organization_id == org_id,
        )
        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            query.options(selectinload(MRPRun.planned_orders))
            .order_by(MRPRun.run_date.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    async def get_planned_order_by_id(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> MRPPlannedOrder | None:
        stmt = select(MRPPlannedOrder).where(
            MRPPlannedOrder.id == order_id,
            MRPPlannedOrder.tenant_id == tenant_id,
            MRPPlannedOrder.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
