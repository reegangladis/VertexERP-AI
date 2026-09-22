"""Repository for User and UserCredential persistence."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.mfa_setting import MfaSetting
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserCredential


class UserRepository:
    """Data access repository for Users, Credentials, and MFA settings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, user_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> User | None:
        stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
        if tenant_id:
            stmt = stmt.where(User.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, tenant_id: uuid.UUID | None = None) -> User | None:
        stmt = select(User).where(User.email == email, User.is_deleted.is_(False))
        if tenant_id:
            stmt = stmt.where(User.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[User]:
        stmt = (
            select(User)
            .where(User.tenant_id == tenant_id, User.is_deleted.is_(False))
            .order_by(User.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_credentials(self, user_id: uuid.UUID) -> UserCredential | None:
        stmt = select(UserCredential).where(UserCredential.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_credentials(self, creds: UserCredential) -> UserCredential:
        self.session.add(creds)
        await self.session.flush()
        return creds

    async def record_failed_login(
        self, user_id: uuid.UUID, max_attempts: int = 5, lockout_minutes: int = 15
    ) -> UserCredential:
        creds = await self.get_credentials(user_id)
        if creds:
            creds.failed_login_attempts += 1
            if creds.failed_login_attempts >= max_attempts:
                from datetime import timedelta

                creds.locked_until = datetime.now(UTC) + timedelta(minutes=lockout_minutes)
            await self.session.flush()
            return creds
        raise ValueError("Credentials not found")

    async def reset_failed_login(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(UserCredential)
            .where(UserCredential.user_id == user_id)
            .values(failed_login_attempts=0, locked_until=None)
        )
        await self.session.execute(stmt)

    async def get_mfa_setting(self, user_id: uuid.UUID) -> MfaSetting | None:
        stmt = select(MfaSetting).where(MfaSetting.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_mfa_setting(self, mfa: MfaSetting) -> MfaSetting:
        self.session.add(mfa)
        await self.session.flush()
        return mfa
