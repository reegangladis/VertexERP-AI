"""Stock Balance Repository with Concurrency Protection."""

import uuid
from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.stock_balance import StockBalance


class StockBalanceRepository:
    """Repository for Stock Balances with atomic locking and multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dimension(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID,
        location_id: uuid.UUID | None = None,
        for_update: bool = False,
    ) -> StockBalance | None:
        stmt = select(StockBalance).where(
            StockBalance.tenant_id == tenant_id,
            StockBalance.organization_id == org_id,
            StockBalance.product_id == product_id,
            StockBalance.warehouse_id == warehouse_id,
            StockBalance.location_id == location_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID,
        location_id: uuid.UUID | None = None,
        for_update: bool = False,
    ) -> StockBalance:
        balance = await self.get_by_dimension(
            tenant_id=tenant_id,
            org_id=org_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            for_update=for_update,
        )
        if not balance:
            balance = StockBalance(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                location_id=location_id,
                quantity_on_hand=Decimal("0.0000"),
                quantity_reserved=Decimal("0.0000"),
                quantity_allocated=Decimal("0.0000"),
                quantity_available=Decimal("0.0000"),
                average_cost=Decimal("0.0000"),
                total_value=Decimal("0.00"),
            )
            self.session.add(balance)
            await self.session.flush()
        return balance

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        warehouse_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[StockBalance]:
        stmt = select(StockBalance).where(
            StockBalance.tenant_id == tenant_id,
            StockBalance.organization_id == org_id,
        )
        if product_id:
            stmt = stmt.where(StockBalance.product_id == product_id)
        if warehouse_id:
            stmt = stmt.where(StockBalance.warehouse_id == warehouse_id)
        stmt = (
            stmt.order_by(StockBalance.product_id, StockBalance.warehouse_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_valuation(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, warehouse_id: uuid.UUID | None = None
    ) -> dict[str, Decimal]:
        stmt = select(
            func.count(StockBalance.id),
            func.coalesce(func.sum(StockBalance.quantity_on_hand), 0),
            func.coalesce(func.sum(StockBalance.total_value), 0),
        ).where(
            StockBalance.tenant_id == tenant_id,
            StockBalance.organization_id == org_id,
        )
        if warehouse_id:
            stmt = stmt.where(StockBalance.warehouse_id == warehouse_id)
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "total_items": row[0] or 0,
            "total_quantity_on_hand": Decimal(str(row[1])),
            "total_valuation": Decimal(str(row[2])),
        }
