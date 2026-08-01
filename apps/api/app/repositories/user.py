import uuid
from datetime import datetime, UTC
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import User, MfaSetting, PasswordHistory

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

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        stmt = select(User).where(
            or_(User.email == identifier, User.username == identifier),
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class MfaSettingRepository(BaseRepository[MfaSetting]):
    def __init__(self, db: AsyncSession):
        super().__init__(MfaSetting, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> MfaSetting | None:
        stmt = select(MfaSetting).where(MfaSetting.user_id == user_id, MfaSetting.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class PasswordHistoryRepository(BaseRepository[PasswordHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(PasswordHistory, db)

    async def get_history_by_user(self, user_id: uuid.UUID) -> list[PasswordHistory]:
        stmt = select(PasswordHistory).where(PasswordHistory.user_id == user_id, PasswordHistory.is_deleted == False).order_by(PasswordHistory.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
