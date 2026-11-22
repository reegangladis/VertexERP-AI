"""Business Unit repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.business_unit import BusinessUnit


class BusinessUnitRepository:
    """Repository for BusinessUnit persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, bu_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BusinessUnit | None:
        stmt = select(BusinessUnit).where(
            BusinessUnit.id == bu_id,
            BusinessUnit.tenant_id == tenant_id,
            BusinessUnit.organization_id == org_id,
            BusinessUnit.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BusinessUnit | None:
        stmt = select(BusinessUnit).where(
            BusinessUnit.code == code,
            BusinessUnit.tenant_id == tenant_id,
            BusinessUnit.organization_id == org_id,
            BusinessUnit.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[BusinessUnit]:
        stmt = select(BusinessUnit).where(
            BusinessUnit.tenant_id == tenant_id,
            BusinessUnit.organization_id == org_id,
            BusinessUnit.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(BusinessUnit.is_active.is_(is_active))
        stmt = stmt.order_by(BusinessUnit.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, bu: BusinessUnit) -> BusinessUnit:
        self.session.add(bu)
        await self.session.flush()
        return bu

    async def update(self, bu: BusinessUnit) -> BusinessUnit:
        bu.updated_at = datetime.now(UTC)
        bu.version += 1
        await self.session.flush()
        return bu

    async def soft_delete(self, bu: BusinessUnit) -> None:
        bu.is_deleted = True
        bu.deleted_at = datetime.now(UTC)
        bu.version += 1
        await self.session.flush()
