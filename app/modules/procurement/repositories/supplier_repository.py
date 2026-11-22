"""Supplier Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier import Supplier


class SupplierRepository:
    """Repository for Supplier / Vendor master with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, supplier_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Supplier | None:
        stmt = select(Supplier).where(
            Supplier.id == supplier_id,
            Supplier.tenant_id == tenant_id,
            Supplier.organization_id == org_id,
            Supplier.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Supplier | None:
        stmt = select(Supplier).where(
            Supplier.code == code.upper(),
            Supplier.tenant_id == tenant_id,
            Supplier.organization_id == org_id,
            Supplier.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Supplier]:
        stmt = select(Supplier).where(
            Supplier.tenant_id == tenant_id,
            Supplier.organization_id == org_id,
            Supplier.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(Supplier.status == status)
        if search:
            stmt = stmt.where(
                (Supplier.name.ilike(f"%{search}%"))
                | (Supplier.code.ilike(f"%{search}%"))
                | (Supplier.email.ilike(f"%{search}%"))
            )
        stmt = stmt.order_by(Supplier.name).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        search: str | None = None,
    ) -> int:
        stmt = select(func.count(Supplier.id)).where(
            Supplier.tenant_id == tenant_id,
            Supplier.organization_id == org_id,
            Supplier.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(Supplier.status == status)
        if search:
            stmt = stmt.where(
                (Supplier.name.ilike(f"%{search}%"))
                | (Supplier.code.ilike(f"%{search}%"))
                | (Supplier.email.ilike(f"%{search}%"))
            )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, supplier: Supplier) -> Supplier:
        self.session.add(supplier)
        await self.session.flush()
        return supplier
