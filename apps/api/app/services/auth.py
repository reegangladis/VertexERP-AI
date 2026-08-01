"""
AuthService — Enterprise Authentication Business Logic Layer.

Implements registration, login, logout, token refresh, password reset,
email verification, profile management, session management, and audit logging.
Follows Clean Architecture and the Service Layer pattern.
"""

import logging
import uuid
from datetime import datetime, timedelta, UTC

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.session import Session
from app.models.user import User
from app.repositories.audit import AuditLogRepository, LoginHistoryRepository
from app.repositories.organization import OrganizationRepository, SecuritySettingRepository
from app.repositories.role import RoleRepository
from app.repositories.session import RefreshTokenRepository, SessionRepository
from app.repositories.token import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
)
from app.services.audit import AuditService, LoginHistoryService
from app.services.organization import OrganizationService
from app.services.session import SessionService, parse_user_agent
from app.services.user import UserService

logger = logging.getLogger(__name__)


class AuthService:
    """Central authentication orchestration service."""

    def __init__(
        self,
        user_service: UserService,
        org_service: OrganizationService,
        session_service: SessionService,
        refresh_token_repo: RefreshTokenRepository,
        role_repo: RoleRepository,
        audit_service: AuditService,
        login_history_service: LoginHistoryService,
        security_setting_repo: SecuritySettingRepository,
        password_reset_token_repo: PasswordResetTokenRepository,
        email_verification_token_repo: EmailVerificationTokenRepository,
    ) -> None:
        self.user_service = user_service
        self.org_service = org_service
        self.session_service = session_service
        self.refresh_token_repo = refresh_token_repo
        self.role_repo = role_repo
        self.audit_service = audit_service
        self.login_history_service = login_history_service
        self.security_setting_repo = security_setting_repo
        self.password_reset_token_repo = password_reset_token_repo
        self.email_verification_token_repo = email_verification_token_repo

    # ──────────────────────────────────────────
    # Registration
    # ──────────────────────────────────────────

    async def register(
        self,
        user_data: dict,
        org_name: str,
        org_slug: str,
        ip_address: str,
        user_agent: str,
        industry: str | None = None,
        company_size: str | None = None,
        country: str | None = None,
        timezone: str | None = None,
    ) -> tuple[User, str]:
        """
        Register a new organization and its first admin user.
        Returns (user, verification_token_str) — the token is logged/returned for dev.
        """
        # 1. Check unique email
        existing_email = await self.user_service.get_by_email(user_data["email"])
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered",
            )

        # 2. Auto-derive username from email if not provided
        if not user_data.get("username"):
            base = user_data["email"].split("@")[0].replace(".", "").replace("+", "")
            user_data["username"] = base[:30]

        existing_username = await self.user_service.get_by_username(user_data["username"])
        if existing_username:
            user_data["username"] = f"{user_data['username']}_{uuid.uuid4().hex[:6]}"

        # 3. Check organization slug uniqueness
        existing_org = await self.org_service.get_by_slug(org_slug)
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization slug is already taken",
            )

        # 4. Create Organization
        org = await self.org_service.create_organization(
            org_name=org_name,
            slug=org_slug,
            email=user_data["email"],
            industry=industry,
            company_size=company_size,
            country=country,
        )

        # 5. Create User
        user_create = {
            **user_data,
            "organization_id": org.id,
            "email_verified": False,
            "phone_verified": False,
            "status": "active",
            "timezone": timezone or "UTC",
        }
        user = await self.user_service.create_user(user_create)

        # 6. Ensure default RBAC roles exist and assign Organization Admin role
        roles_map = await self.role_repo.ensure_default_roles(org.id)
        admin_role = roles_map.get("Organization Admin") or await self.role_repo.get_by_name("Organization Admin")
        if admin_role and admin_role not in user.roles:
            user.roles.append(admin_role)
            await self.user_service.repository.db.commit()

        # 7. Set org.created_by
        await self.org_service.repository.update(org, {"created_by": user.id})

        # 8. Generate email verification token
        verification_token_str = EmailVerificationToken.generate_token()
        await self.email_verification_token_repo.create(
            {
                "user_id": user.id,
                "token": verification_token_str,
                "expires_at": datetime.now(UTC) + timedelta(hours=24),
                "used": False,
            }
        )

        # 9. Audit
        await self.audit_service.log_action(
            user.id,
            org.id,
            "user.register",
            ip_address,
            user_agent,
            {"organization_name": org_name, "organization_slug": org_slug},
        )

        logger.info(
            f"[AUTH] New organization registered: {org_name} ({org_slug}) | "
            f"Admin: {user.email} | "
            f"Email verification token: {verification_token_str}"
        )

        return user, verification_token_str

    # ──────────────────────────────────────────
    # Login
    # ──────────────────────────────────────────

    async def login(
        self,
        identifier: str,
        password: str,
        ip_address: str,
        user_agent: str,
    ) -> dict:
        """Authenticate user credentials (email or username) and issue JWT access + refresh tokens."""
        user = await self.user_service.repository.get_by_email_or_username(identifier)

        if not user:
            await self.login_history_service.log_login(
                None, identifier, ip_address, user_agent, "Other", "Other", "failed",
                "User not found",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password",
            )

        # Fetch account lockout security settings
        threshold = 5
        duration = 15
        if user.organization_id:
            sec_set = await self.security_setting_repo.get_by_org_id(
                user.organization_id
            )
            if sec_set:
                threshold = sec_set.account_lockout_threshold
                duration = sec_set.account_lockout_duration_minutes

        # Check account lock
        if await self.user_service.is_account_locked(user):
            await self.login_history_service.log_login(
                user.id, email, ip_address, user_agent, "Other", "Other",
                "failed", "Account is locked",
            )
            locked_until = user.locked_until.strftime("%H:%M UTC") if user.locked_until else "soon"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is temporarily locked. Please try again after {locked_until}",
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            await self.user_service.increment_failed_attempts(user, threshold, duration)
            await self.login_history_service.log_login(
                user.id, email, ip_address, user_agent, "Other", "Other",
                "failed", "Invalid credentials",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Reset failed attempts
        await self.user_service.reset_failed_attempts(user)

        # Update last_login
        await self.user_service.repository.update(
            user, {"last_login": datetime.now(UTC)}
        )

        # Create session
        session = await self.session_service.create_session(
            user.id, ip_address, user_agent
        )

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Persist refresh token
        await self.refresh_token_repo.create(
            {
                "user_id": user.id,
                "token": refresh_token,
                "expires_at": datetime.now(UTC)
                + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            }
        )

        # Audit
        browser, os = parse_user_agent(user_agent)
        await self.login_history_service.log_login(
            user.id, email, ip_address, user_agent, browser, os, "success"
        )
        await self.audit_service.log_action(
            user.id, user.organization_id, "user.login", ip_address, user_agent
        )

        logger.info(f"[AUTH] Successful login: {email} from {ip_address}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "session_id": str(session.id),
        }

    # ──────────────────────────────────────────
    # Logout
    # ──────────────────────────────────────────

    async def logout(
        self,
        refresh_token: str,
        user_id: uuid.UUID,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Revoke the given refresh token and deactivate the user session."""
        await self.refresh_token_repo.revoke_token(refresh_token)
        await self.session_service.revoke_all_user_sessions(user_id)
        await self.audit_service.log_action(
            user_id, None, "user.logout", ip_address, user_agent
        )

    async def logout_all(
        self,
        user_id: uuid.UUID,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Revoke ALL refresh tokens and sessions for the user (terminate all devices)."""
        # Revoke all sessions
        await self.session_service.revoke_all_user_sessions(user_id)

        # Revoke all refresh tokens via raw SQL
        from sqlalchemy import update
        from app.models.session import RefreshToken
        from datetime import datetime, UTC
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        await self.refresh_token_repo.db.execute(stmt)
        await self.refresh_token_repo.db.commit()

        await self.audit_service.log_action(
            user_id, None, "user.logout_all", ip_address, user_agent
        )

    # ──────────────────────────────────────────
    # Token Refresh (Rotation)
    # ──────────────────────────────────────────

    async def refresh_tokens(
        self, refresh_token: str, ip_address: str, user_agent: str
    ) -> dict:
        """Rotate refresh token and issue new access + refresh token pair."""
        db_token = await self.refresh_token_repo.get_by_token(refresh_token)

        if not db_token or db_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        token_exp = db_token.expires_at
        if token_exp.tzinfo is None:
            token_exp = token_exp.replace(tzinfo=UTC)

        if token_exp < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        sub = decode_token(refresh_token, is_refresh=True)
        if not sub or str(db_token.user_id) != sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token signature mismatch",
            )

        # Rotate: revoke old token
        await self.refresh_token_repo.revoke_token(refresh_token)

        user_id = db_token.user_id
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        await self.refresh_token_repo.create(
            {
                "user_id": user_id,
                "token": new_refresh_token,
                "expires_at": datetime.now(UTC)
                + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            }
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    # ──────────────────────────────────────────
    # Forgot Password
    # ──────────────────────────────────────────

    async def forgot_password(self, email: str) -> str | None:
        """
        Initiate password recovery flow.
        Returns reset token string only in development mode.
        Always returns generic success message to the caller.
        """
        user = await self.user_service.get_by_email(email)
        if not user:
            # Security: do NOT reveal whether email exists
            logger.info(f"[AUTH] Forgot password: no user found for {email}")
            return None

        # Revoke previous reset tokens
        await self.password_reset_token_repo.revoke_all_for_user(user.id)

        # Generate new reset token
        token_str = PasswordResetToken.generate_token()
        await self.password_reset_token_repo.create(
            {
                "user_id": user.id,
                "token": token_str,
                "expires_at": datetime.now(UTC) + timedelta(hours=2),
                "used": False,
            }
        )

        reset_link = f"http://localhost:5173/auth/reset-password?token={token_str}"
        logger.info(
            f"[AUTH] Password reset token generated for {email}. "
            f"Reset link: {reset_link}"
        )

        # In development, return the token for immediate testing
        if settings.ENVIRONMENT in ("development", "testing"):
            return token_str
        return None

    # ──────────────────────────────────────────
    # Reset Password
    # ──────────────────────────────────────────

    async def reset_password(self, token: str, new_password: str) -> None:
        """Validate reset token and update user password."""
        db_token = await self.password_reset_token_repo.get_valid_token(token)
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )

        user = await self.user_service.repository.get(db_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found",
            )

        try:
            await self.user_service.update_password(user, new_password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        # Mark token as used
        await self.password_reset_token_repo.mark_used(token)

        logger.info(f"[AUTH] Password reset successful for user {user.email}")

    # ──────────────────────────────────────────
    # Email Verification
    # ──────────────────────────────────────────

    async def verify_email(self, token: str) -> None:
        """Validate verification token and activate user email."""
        db_token = await self.email_verification_token_repo.get_valid_token(token)
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired email verification token",
            )

        user = await self.user_service.repository.get(db_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found",
            )

        await self.user_service.repository.update(user, {"email_verified": True})
        await self.email_verification_token_repo.mark_used(token)

        logger.info(f"[AUTH] Email verified for user {user.email}")

    async def resend_verification_email(
        self, user_id: uuid.UUID
    ) -> str | None:
        """Resend email verification token (revoke old, issue new)."""
        user = await self.user_service.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.email_verified:
            raise HTTPException(status_code=400, detail="Email is already verified")

        await self.email_verification_token_repo.revoke_all_for_user(user_id)

        token_str = EmailVerificationToken.generate_token()
        await self.email_verification_token_repo.create(
            {
                "user_id": user_id,
                "token": token_str,
                "expires_at": datetime.now(UTC) + timedelta(hours=24),
                "used": False,
            }
        )

        verify_link = f"http://localhost:5173/auth/verify-email?token={token_str}"
        logger.info(
            f"[AUTH] Email verification resent for {user.email}. "
            f"Verify link: {verify_link}"
        )

        if settings.ENVIRONMENT in ("development", "testing"):
            return token_str
        return None

    # ──────────────────────────────────────────
    # Profile Update
    # ──────────────────────────────────────────

    async def update_profile(self, user: User, update_data: dict) -> User:
        """Update user profile fields (non-security fields only)."""
        allowed_fields = {
            "first_name", "last_name", "phone", "avatar", "timezone", "language"
        }
        filtered = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}
        if not filtered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update",
            )
        return await self.user_service.repository.update(user, filtered)

    # ──────────────────────────────────────────
    # Change Password
    # ──────────────────────────────────────────

    async def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str,
        confirm_password: str,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Authenticated password change with current password verification."""
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirmation do not match",
            )

        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        try:
            await self.user_service.update_password(user, new_password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        await self.audit_service.log_action(
            user.id, user.organization_id,
            "user.change_password", ip_address, user_agent,
        )

        logger.info(f"[AUTH] Password changed for user {user.email}")

    # ──────────────────────────────────────────
    # Session Management
    # ──────────────────────────────────────────

    async def get_sessions(self, user_id: uuid.UUID) -> list[Session]:
        """Return all active sessions for the authenticated user."""
        return await self.session_service.get_active_by_user(user_id)

    async def revoke_session(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Terminate a specific session; verifies the session belongs to the user."""
        session = await self.session_service.repository.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to this account",
            )
        await self.session_service.revoke_session(session_id)
        await self.audit_service.log_action(
            user_id, None, "user.session_revoke", ip_address, user_agent,
            {"session_id": str(session_id)},
        )

    # ──────────────────────────────────────────
    # History & Audit
    # ──────────────────────────────────────────

    async def get_login_history(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list:
        """Return paginated login history for a user."""
        return await self.login_history_service.repository.get_by_user(user_id)

    async def get_audit_logs(
        self, organization_id: uuid.UUID, limit: int = 100
    ) -> list:
        """Return paginated audit logs for the user's organization."""
        return await self.audit_service.repository.get_by_org(organization_id)
