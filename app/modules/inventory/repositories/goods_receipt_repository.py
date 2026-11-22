"""Goods Receipt Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.models.goods_receipt import GoodsReceipt


class GoodsReceiptRepository:
    """Repository for Goods Receipts with eager-loading and isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, receipt_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> GoodsReceipt | None:
        stmt = (
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .where(
                GoodsReceipt.id == receipt_id,
                GoodsReceipt.tenant_id == tenant_id,
                GoodsReceipt.organization_id == org_id,
                GoodsReceipt.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, receipt_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> GoodsReceipt | None:
        stmt = select(GoodsReceipt).where(
            GoodsReceipt.receipt_number == receipt_number,
            GoodsReceipt.tenant_id == tenant_id,
            GoodsReceipt.organization_id == org_id,
            GoodsReceipt.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        supplier_id: uuid.UUID | None = None,
        purchase_order_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[GoodsReceipt]:
        stmt = (
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .where(
                GoodsReceipt.tenant_id == tenant_id,
                GoodsReceipt.organization_id == org_id,
                GoodsReceipt.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(GoodsReceipt.status == status)
        if supplier_id:
            stmt = stmt.where(GoodsReceipt.supplier_id == supplier_id)
        if purchase_order_id:
            stmt = stmt.where(GoodsReceipt.purchase_order_id == purchase_order_id)
        stmt = stmt.order_by(GoodsReceipt.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(GoodsReceipt.id)).where(
            GoodsReceipt.tenant_id == tenant_id,
            GoodsReceipt.organization_id == org_id,
            GoodsReceipt.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(GoodsReceipt.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, receipt: GoodsReceipt) -> GoodsReceipt:
        self.session.add(receipt)
        await self.session.flush()
        return receipt
