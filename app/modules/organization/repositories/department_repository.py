"""Department repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.department import Department


class DepartmentRepository:
    """Repository for Department persistence with strict tenant & org isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, dept_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Department | None:
        stmt = select(Department).where(
            Department.id == dept_id,
            Department.tenant_id == tenant_id,
            Department.organization_id == org_id,
            Department.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Department | None:
        stmt = select(Department).where(
            Department.code == code,
            Department.tenant_id == tenant_id,
            Department.organization_id == org_id,
            Department.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Department]:
        stmt = select(Department).where(
            Department.tenant_id == tenant_id,
            Department.organization_id == org_id,
            Department.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(Department.is_active.is_(is_active))
        stmt = stmt.order_by(Department.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, dept: Department) -> Department:
        self.session.add(dept)
        await self.session.flush()
        return dept

    async def update(self, dept: Department) -> Department:
        dept.updated_at = datetime.now(UTC)
        dept.version += 1
        await self.session.flush()
        return dept

    async def soft_delete(self, dept: Department) -> None:
        dept.is_deleted = True
        dept.deleted_at = datetime.now(UTC)
        dept.version += 1
        await self.session.flush()
