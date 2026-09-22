"""Designation repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.designation import Designation


class DesignationRepository:
    """Repository for Designation persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, desig_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Designation | None:
        stmt = select(Designation).where(
            Designation.id == desig_id,
            Designation.tenant_id == tenant_id,
            Designation.organization_id == org_id,
            Designation.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Designation | None:
        stmt = select(Designation).where(
            Designation.code == code,
            Designation.tenant_id == tenant_id,
            Designation.organization_id == org_id,
            Designation.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Designation]:
        stmt = select(Designation).where(
            Designation.tenant_id == tenant_id,
            Designation.organization_id == org_id,
            Designation.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(Designation.is_active.is_(is_active))
        stmt = stmt.order_by(Designation.level.asc(), Designation.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, desig: Designation) -> Designation:
        self.session.add(desig)
        await self.session.flush()
        return desig

    async def update(self, desig: Designation) -> Designation:
        desig.updated_at = datetime.now(UTC)
        desig.version += 1
        await self.session.flush()
        return desig

    async def soft_delete(self, desig: Designation) -> None:
        desig.is_deleted = True
        desig.deleted_at = datetime.now(UTC)
        desig.version += 1
        await self.session.flush()
