import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_with_permissions(self, role_id: uuid.UUID) -> Role | None:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id, Role.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.organization_id == org_id, Role.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
