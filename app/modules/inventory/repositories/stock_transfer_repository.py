"""Stock Transfer Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.models.stock_transfer import StockTransfer


class StockTransferRepository:
    """Repository for Stock Transfers with items eager-loading and isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, transfer_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> StockTransfer | None:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.items))
            .where(
                StockTransfer.id == transfer_id,
                StockTransfer.tenant_id == tenant_id,
                StockTransfer.organization_id == org_id,
                StockTransfer.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        from_warehouse_id: uuid.UUID | None = None,
        to_warehouse_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[StockTransfer]:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.items))
            .where(
                StockTransfer.tenant_id == tenant_id,
                StockTransfer.organization_id == org_id,
                StockTransfer.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(StockTransfer.status == status)
        if from_warehouse_id:
            stmt = stmt.where(StockTransfer.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            stmt = stmt.where(StockTransfer.to_warehouse_id == to_warehouse_id)
        stmt = stmt.order_by(StockTransfer.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(StockTransfer.id)).where(
            StockTransfer.tenant_id == tenant_id,
            StockTransfer.organization_id == org_id,
            StockTransfer.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(StockTransfer.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, transfer: StockTransfer) -> StockTransfer:
        self.session.add(transfer)
        await self.session.flush()
        return transfer
