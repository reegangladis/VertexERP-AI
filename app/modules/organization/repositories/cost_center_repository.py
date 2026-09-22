"""Cost Center repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.cost_center import CostCenter


class CostCenterRepository:
    """Repository for CostCenter persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, cc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CostCenter | None:
        stmt = select(CostCenter).where(
            CostCenter.id == cc_id,
            CostCenter.tenant_id == tenant_id,
            CostCenter.organization_id == org_id,
            CostCenter.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CostCenter | None:
        stmt = select(CostCenter).where(
            CostCenter.code == code,
            CostCenter.tenant_id == tenant_id,
            CostCenter.organization_id == org_id,
            CostCenter.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[CostCenter]:
        stmt = select(CostCenter).where(
            CostCenter.tenant_id == tenant_id,
            CostCenter.organization_id == org_id,
            CostCenter.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(CostCenter.is_active.is_(is_active))
        stmt = stmt.order_by(CostCenter.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, cc: CostCenter) -> CostCenter:
        self.session.add(cc)
        await self.session.flush()
        return cc

    async def update(self, cc: CostCenter) -> CostCenter:
        cc.updated_at = datetime.now(UTC)
        cc.version += 1
        await self.session.flush()
        return cc

    async def soft_delete(self, cc: CostCenter) -> None:
        cc.is_deleted = True
        cc.deleted_at = datetime.now(UTC)
        cc.version += 1
        await self.session.flush()
