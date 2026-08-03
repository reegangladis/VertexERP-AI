import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import RefreshToken, Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[Session]:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.revoked == False,
            Session.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = (
            update(Session)
            .where(
                Session.id == session_id,
                Session.user_id == user_id,
                Session.is_deleted == False,
            )
            .values(revoked=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def revoke_all_sessions(self, user_id: uuid.UUID, except_session_id: uuid.UUID | None = None) -> int:
        stmt = (
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.revoked == False,
                Session.is_deleted == False,
            )
        )
        if except_session_id:
            stmt = stmt.where(Session.id != except_session_id)
        stmt = stmt.values(revoked=True)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_token(self, token_hash: str) -> bool:
        token_obj = await self.get_by_hash(token_hash)
        if token_obj:
            token_obj.revoked = True
            await self.db.commit()
            return True
        return False
