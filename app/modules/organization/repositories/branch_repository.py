"""Branch repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.branch import Branch


class BranchRepository:
    """Repository for Branch persistence with strict tenant & org isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, branch_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Branch | None:
        stmt = select(Branch).where(
            Branch.id == branch_id,
            Branch.tenant_id == tenant_id,
            Branch.organization_id == org_id,
            Branch.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Branch | None:
        stmt = select(Branch).where(
            Branch.code == code,
            Branch.tenant_id == tenant_id,
            Branch.organization_id == org_id,
            Branch.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Branch]:
        stmt = select(Branch).where(
            Branch.tenant_id == tenant_id,
            Branch.organization_id == org_id,
            Branch.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(Branch.is_active.is_(is_active))
        stmt = stmt.order_by(Branch.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, branch: Branch) -> Branch:
        self.session.add(branch)
        await self.session.flush()
        return branch

    async def update(self, branch: Branch) -> Branch:
        branch.updated_at = datetime.now(UTC)
        branch.version += 1
        await self.session.flush()
        return branch

    async def soft_delete(self, branch: Branch) -> None:
        branch.is_deleted = True
        branch.deleted_at = datetime.now(UTC)
        branch.version += 1
        await self.session.flush()
