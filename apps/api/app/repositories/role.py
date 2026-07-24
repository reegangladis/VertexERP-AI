import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.role import Role
from app.models.permission import Permission

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name, Role.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_roles_by_org(self, organization_id: uuid.UUID | None) -> list[Role]:
        # Fetch organization specific roles + default global roles
        stmt = select(Role).where(
            (Role.organization_id == organization_id) | (Role.organization_id == None),
            Role.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
