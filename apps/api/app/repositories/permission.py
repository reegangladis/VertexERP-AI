from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: AsyncSession):
        super().__init__(Permission, db)

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(
            Permission.name == name, Permission.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_names(self, names: list[str]) -> list[Permission]:
        stmt = select(Permission).where(
            Permission.name.in_(names), Permission.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[Permission]:
        stmt = select(Permission).where(
            Permission.category == category, Permission.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
