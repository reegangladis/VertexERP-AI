"""Stock Movement (Ledger) Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.stock_movement import StockMovement


class StockMovementRepository:
    """Repository for Immutable Stock Ledger with point-in-time auditing."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, movement_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> StockMovement | None:
        stmt = select(StockMovement).where(
            StockMovement.id == movement_id,
            StockMovement.tenant_id == tenant_id,
            StockMovement.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_product(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[StockMovement]:
        stmt = select(StockMovement).where(
            StockMovement.tenant_id == tenant_id,
            StockMovement.organization_id == org_id,
            StockMovement.product_id == product_id,
        )
        if warehouse_id:
            stmt = stmt.where(StockMovement.warehouse_id == warehouse_id)
        stmt = stmt.order_by(StockMovement.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        movement_type: str | None = None,
        warehouse_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[StockMovement]:
        stmt = select(StockMovement).where(
            StockMovement.tenant_id == tenant_id,
            StockMovement.organization_id == org_id,
        )
        if movement_type:
            stmt = stmt.where(StockMovement.movement_type == movement_type)
        if warehouse_id:
            stmt = stmt.where(StockMovement.warehouse_id == warehouse_id)
        stmt = stmt.order_by(StockMovement.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        movement_type: str | None = None,
        warehouse_id: uuid.UUID | None = None,
    ) -> int:
        stmt = select(func.count(StockMovement.id)).where(
            StockMovement.tenant_id == tenant_id,
            StockMovement.organization_id == org_id,
        )
        if movement_type:
            stmt = stmt.where(StockMovement.movement_type == movement_type)
        if warehouse_id:
            stmt = stmt.where(StockMovement.warehouse_id == warehouse_id)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, movement: StockMovement) -> StockMovement:
        self.session.add(movement)
        await self.session.flush()
        return movement
