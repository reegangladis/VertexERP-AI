"""Repository for Manufacturing Routings."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.manufacturing.models.routing import Routing, RoutingOperation


class RoutingRepository:
    """Database repository for Routing and RoutingOperation entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_routing(self, routing: Routing) -> Routing:
        self.session.add(routing)
        await self.session.flush()
        return routing

    async def get_routing_by_id(
        self, routing_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Routing | None:
        stmt = (
            select(Routing)
            .where(
                Routing.id == routing_id,
                Routing.tenant_id == tenant_id,
                Routing.organization_id == org_id,
            )
            .options(selectinload(Routing.operations))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_routing_by_product(
        self, product_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Routing | None:
        stmt = (
            select(Routing)
            .where(
                Routing.product_id == product_id,
                Routing.tenant_id == tenant_id,
                Routing.organization_id == org_id,
                Routing.is_active.is_(True),
            )
            .options(selectinload(Routing.operations))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_routings(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Routing], int]:
        query = select(Routing).where(
            Routing.tenant_id == tenant_id,
            Routing.organization_id == org_id,
        )
        if product_id:
            query = query.where(Routing.product_id == product_id)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            query.options(selectinload(Routing.operations))
            .order_by(Routing.code)
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    async def create_operation(self, operation: "RoutingOperation") -> "RoutingOperation":
        self.session.add(operation)
        await self.session.flush()
        return operation

