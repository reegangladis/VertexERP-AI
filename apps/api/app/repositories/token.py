import uuid
from datetime import datetime, UTC
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.password_reset_token import PasswordResetToken
from app.models.email_verification_token import EmailVerificationToken


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    """Repository for managing password reset tokens."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(PasswordResetToken, db)

    async def get_valid_token(self, token: str) -> PasswordResetToken | None:
        """Retrieve a valid, non-expired, and unused password reset token."""
        stmt = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,  # noqa: E712
                PasswordResetToken.expires_at > datetime.now(UTC),
                PasswordResetToken.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, token: str) -> None:
        """Mark a password reset token as consumed."""
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke all existing reset tokens for a user before issuing a new one."""
        stmt = (
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used == False,  # noqa: E712
            )
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()


class EmailVerificationTokenRepository(BaseRepository[EmailVerificationToken]):
    """Repository for managing email verification tokens."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(EmailVerificationToken, db)

    async def get_valid_token(self, token: str) -> EmailVerificationToken | None:
        """Retrieve a valid, non-expired, and unused email verification token."""
        stmt = (
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.token == token,
                EmailVerificationToken.used == False,  # noqa: E712
                EmailVerificationToken.expires_at > datetime.now(UTC),
                EmailVerificationToken.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, token: str) -> None:
        """Mark an email verification token as consumed."""
        stmt = (
            update(EmailVerificationToken)
            .where(EmailVerificationToken.token == token)
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke all pending verification tokens for a user."""
        stmt = (
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used == False,  # noqa: E712
            )
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()
