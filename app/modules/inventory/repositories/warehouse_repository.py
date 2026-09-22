"""Warehouse and Location Repositories."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.models.warehouse import Location, Warehouse


class WarehouseRepository:
    """Repository for Warehouses with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, warehouse_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Warehouse | None:
        stmt = (
            select(Warehouse)
            .options(selectinload(Warehouse.locations))
            .where(
                Warehouse.id == warehouse_id,
                Warehouse.tenant_id == tenant_id,
                Warehouse.organization_id == org_id,
                Warehouse.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Warehouse | None:
        stmt = select(Warehouse).where(
            Warehouse.code == code.upper(),
            Warehouse.tenant_id == tenant_id,
            Warehouse.organization_id == org_id,
            Warehouse.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[Warehouse]:
        stmt = (
            select(Warehouse)
            .options(selectinload(Warehouse.locations))
            .where(
                Warehouse.tenant_id == tenant_id,
                Warehouse.organization_id == org_id,
                Warehouse.is_deleted.is_(False),
            )
            .order_by(Warehouse.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(Warehouse.id)).where(
            Warehouse.tenant_id == tenant_id,
            Warehouse.organization_id == org_id,
            Warehouse.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, warehouse: Warehouse) -> Warehouse:
        self.session.add(warehouse)
        await self.session.flush()
        return warehouse


class LocationRepository:
    """Repository for Warehouse Bins/Locations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, location_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Location | None:
        stmt = select(Location).where(
            Location.id == location_id,
            Location.tenant_id == tenant_id,
            Location.organization_id == org_id,
            Location.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_warehouse(
        self, warehouse_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[Location]:
        stmt = (
            select(Location)
            .where(
                Location.warehouse_id == warehouse_id,
                Location.tenant_id == tenant_id,
                Location.organization_id == org_id,
                Location.is_deleted.is_(False),
            )
            .order_by(Location.code)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, location: Location) -> Location:
        self.session.add(location)
        await self.session.flush()
        return location
