"""Repository for Production Orders, Work Orders, Consumptions, Outputs, and Scrap."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.manufacturing.models.production_order import (
    MaterialConsumption,
    ProductionOrder,
    ProductionOutput,
    ProductionScrap,
    WorkOrder,
)


class ProductionOrderRepository:
    """Database repository for Production Order lifecycle and execution artifacts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_order(self, order: ProductionOrder) -> ProductionOrder:
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_order_by_id(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, for_update: bool = False
    ) -> ProductionOrder | None:
        stmt = (
            select(ProductionOrder)
            .where(
                ProductionOrder.id == order_id,
                ProductionOrder.tenant_id == tenant_id,
                ProductionOrder.organization_id == org_id,
            )
            .options(
                selectinload(ProductionOrder.work_orders),
                selectinload(ProductionOrder.consumptions),
                selectinload(ProductionOrder.outputs),
                selectinload(ProductionOrder.scraps),
            )
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_order_by_number(
        self, order_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductionOrder | None:
        stmt = select(ProductionOrder).where(
            ProductionOrder.order_number == order_number,
            ProductionOrder.tenant_id == tenant_id,
            ProductionOrder.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_orders(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[ProductionOrder], int]:
        query = select(ProductionOrder).where(
            ProductionOrder.tenant_id == tenant_id,
            ProductionOrder.organization_id == org_id,
        )
        if product_id:
            query = query.where(ProductionOrder.product_id == product_id)
        if status:
            query = query.where(ProductionOrder.status == status)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            query.options(
                selectinload(ProductionOrder.work_orders),
                selectinload(ProductionOrder.consumptions),
                selectinload(ProductionOrder.outputs),
                selectinload(ProductionOrder.scraps),
            )
            .order_by(ProductionOrder.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    # Work Order methods
    async def create_work_order(self, wo: WorkOrder) -> WorkOrder:
        self.session.add(wo)
        await self.session.flush()
        return wo

    async def get_work_order_by_id(
        self, wo_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, for_update: bool = False
    ) -> WorkOrder | None:
        stmt = select(WorkOrder).where(
            WorkOrder.id == wo_id,
            WorkOrder.tenant_id == tenant_id,
            WorkOrder.organization_id == org_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_work_orders(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        production_order_id: uuid.UUID | None = None,
        work_center_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[WorkOrder], int]:
        query = select(WorkOrder).where(
            WorkOrder.tenant_id == tenant_id,
            WorkOrder.organization_id == org_id,
        )
        if production_order_id:
            query = query.where(WorkOrder.production_order_id == production_order_id)
        if work_center_id:
            query = query.where(WorkOrder.work_center_id == work_center_id)
        if status:
            query = query.where(WorkOrder.status == status)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = query.order_by(WorkOrder.sequence).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    # Material Consumption methods
    async def create_consumption(self, cons: MaterialConsumption) -> MaterialConsumption:
        self.session.add(cons)
        await self.session.flush()
        return cons

    # Production Output methods
    async def create_output(self, out: ProductionOutput) -> ProductionOutput:
        self.session.add(out)
        await self.session.flush()
        return out

    # Production Scrap methods
    async def create_scrap(self, scrap: ProductionScrap) -> ProductionScrap:
        self.session.add(scrap)
        await self.session.flush()
        return scrap
