import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_history import LoginHistory, TrustedDevice
from app.repositories.base import BaseRepository


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(LoginHistory, db)

    async def get_by_user_id(self, user_id: uuid.UUID, limit: int = 50) -> list[LoginHistory]:
        stmt = (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id, LoginHistory.is_deleted == False)
            .order_by(LoginHistory.login_time.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class TrustedDeviceRepository(BaseRepository[TrustedDevice]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrustedDevice, db)

    async def get_by_hash(self, user_id: uuid.UUID, device_hash: str) -> TrustedDevice | None:
        stmt = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_hash == device_hash,
            TrustedDevice.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
