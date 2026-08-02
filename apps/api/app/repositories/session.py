import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_history import TrustedDevice
from app.models.session import RefreshToken, Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[Session]:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.is_active == True,
            Session.expires_at > datetime.now(UTC),
            Session.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_all_user_sessions(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Session)
            .where(Session.user_id == user_id, Session.is_active == True)
            .values(is_active=False, updated_at=datetime.now(UTC))
        )
        await self.db.execute(stmt)
        await self.db.commit()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token == token, RefreshToken.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_token(self, token: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(is_revoked=True, updated_at=datetime.now(UTC))
        )
        await self.db.execute(stmt)
        await self.db.commit()


class TrustedDeviceRepository(BaseRepository[TrustedDevice]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrustedDevice, db)

    async def get_by_fingerprint(
        self, user_id: uuid.UUID, fingerprint: str
    ) -> TrustedDevice | None:
        stmt = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_fingerprint == fingerprint,
            TrustedDevice.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
