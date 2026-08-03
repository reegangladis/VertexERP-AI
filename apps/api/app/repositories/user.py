import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username, User.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> User | None:
        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier),
            User.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(User.id == user_id, User.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_roles(self, user: User, role_ids: list[uuid.UUID]) -> User:
        stmt = select(Role).where(Role.id.in_(role_ids), Role.is_deleted == False)
        result = await self.db.execute(stmt)
        roles = list(result.scalars().all())
        user.roles = roles
        await self.db.commit()
        await self.db.refresh(user)
        return user
