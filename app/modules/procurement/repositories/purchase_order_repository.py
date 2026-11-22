"""Purchase Order Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.procurement.models.purchase_order import PurchaseOrder


class PurchaseOrderRepository:
    """Repository for Purchase Orders with eager-loading and isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, po_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PurchaseOrder | None:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(
                PurchaseOrder.id == po_id,
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.organization_id == org_id,
                PurchaseOrder.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, po_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PurchaseOrder | None:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(
                PurchaseOrder.po_number == po_number,
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.organization_id == org_id,
                PurchaseOrder.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        supplier_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[PurchaseOrder]:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.organization_id == org_id,
                PurchaseOrder.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(PurchaseOrder.status == status)
        if supplier_id:
            stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
        stmt = stmt.order_by(PurchaseOrder.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.tenant_id == tenant_id,
            PurchaseOrder.organization_id == org_id,
            PurchaseOrder.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(PurchaseOrder.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, po: PurchaseOrder) -> PurchaseOrder:
        self.session.add(po)
        await self.session.flush()
        return po
