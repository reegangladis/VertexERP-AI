"""Repository for UserSession management and active session tracking."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.user_credential import UserSession


class SessionRepository:
    """Data access repository for UserSession entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_jti(self, jti: str) -> UserSession | None:
        stmt = select(UserSession).where(UserSession.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_refresh_token_hash(self, token_hash: str) -> UserSession | None:
        stmt = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_user_sessions(self, user_id: uuid.UUID) -> Sequence[UserSession]:
        now = datetime.now(UTC)
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_revoked.is_(False),
                UserSession.expires_at > now,
            )
            .order_by(UserSession.last_active_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, user_session: UserSession) -> UserSession:
        self.session.add(user_session)
        await self.session.flush()
        return user_session

    async def revoke_session(self, session_id: uuid.UUID) -> None:
        stmt = update(UserSession).where(UserSession.id == session_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = update(UserSession).where(UserSession.user_id == user_id).values(is_revoked=True)
        await self.session.execute(stmt)
