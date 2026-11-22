"""Stock Adjustment Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.models.stock_adjustment import StockAdjustment


class StockAdjustmentRepository:
    """Repository for Stock Adjustments with items eager-loading and isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, adjustment_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> StockAdjustment | None:
        stmt = (
            select(StockAdjustment)
            .options(selectinload(StockAdjustment.items))
            .where(
                StockAdjustment.id == adjustment_id,
                StockAdjustment.tenant_id == tenant_id,
                StockAdjustment.organization_id == org_id,
                StockAdjustment.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        warehouse_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[StockAdjustment]:
        stmt = (
            select(StockAdjustment)
            .options(selectinload(StockAdjustment.items))
            .where(
                StockAdjustment.tenant_id == tenant_id,
                StockAdjustment.organization_id == org_id,
                StockAdjustment.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(StockAdjustment.status == status)
        if warehouse_id:
            stmt = stmt.where(StockAdjustment.warehouse_id == warehouse_id)
        stmt = stmt.order_by(StockAdjustment.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(StockAdjustment.id)).where(
            StockAdjustment.tenant_id == tenant_id,
            StockAdjustment.organization_id == org_id,
            StockAdjustment.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(StockAdjustment.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, adjustment: StockAdjustment) -> StockAdjustment:
        self.session.add(adjustment)
        await self.session.flush()
        return adjustment
