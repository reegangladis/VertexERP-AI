import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
)
from app.models.login_history import LoginHistory
from app.models.session import RefreshToken, Session
from app.models.user import PasswordHistory, User
from app.repositories.login_history import LoginHistoryRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.role import RoleRepository
from app.repositories.session import RefreshTokenRepository, SessionRepository
from app.repositories.token import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
)
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserWithRolesResponse


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        role_repo: RoleRepository,
        session_repo: SessionRepository,
        refresh_token_repo: RefreshTokenRepository,
        login_history_repo: LoginHistoryRepository,
        email_token_repo: EmailVerificationTokenRepository,
        password_token_repo: PasswordResetTokenRepository,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.role_repo = role_repo
        self.session_repo = session_repo
        self.refresh_token_repo = refresh_token_repo
        self.login_history_repo = login_history_repo
        self.email_token_repo = email_token_repo
        self.password_token_repo = password_token_repo

    async def register(self, req: RegisterRequest) -> User:
        pwd_errors = validate_password_strength(req.password)
        if pwd_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(pwd_errors)}",
            )

        existing = await self.user_repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )
        existing_user = await self.user_repo.get_by_username(req.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken",
            )

        # Get or create organization
        org = None
        if req.organization_slug:
            org = await self.org_repo.get_by_slug(req.organization_slug)
        if not org:
            orgs = await self.org_repo.get_all(limit=1)
            if orgs:
                org = orgs[0]
            else:
                org_name = req.organization_name or f"{req.first_name}'s Org"
                org_slug = req.organization_slug or f"org-{uuid.uuid4().hex[:6]}"
                org = await self.org_repo.create({"name": org_name, "slug": org_slug})

        user_data = {
            "first_name": req.first_name,
            "last_name": req.last_name,
            "username": req.username,
            "email": req.email,
            "password_hash": hash_password(req.password),
            "organization_id": org.id,
            "status": "active",
        }
        user = await self.user_repo.create(user_data)

        # Assign default Admin role if system has roles
        roles = await self.role_repo.get_by_org_id(org.id)
        if roles:
            await self.user_repo.assign_roles(user, [roles[0].id])

        # Record password history
        password_hist = PasswordHistory(user_id=user.id, password_hash=user.password_hash)
        self.user_repo.db.add(password_hist)
        await self.user_repo.db.commit()

        return await self.user_repo.get_with_roles(user.id) or user

    async def login(self, req: LoginRequest, ip_address: str = "127.0.0.1", user_agent: str = "Client") -> TokenResponse:
        user = await self.user_repo.get_by_username_or_email(req.username_or_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        # Check account lockout
        if user.locked_until:
            locked_until_tz = user.locked_until.replace(tzinfo=UTC) if user.locked_until.tzinfo is None else user.locked_until
            if locked_until_tz > datetime.now(UTC):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account locked due to excessive failed attempts. Try again later.",
                )

        if not verify_password(req.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
            await self.user_repo.db.commit()

            # Record failed login
            await self.login_history_repo.create(
                {
                    "user_id": user.id,
                    "ip_address": ip_address,
                    "device": user_agent,
                    "browser": user_agent,
                    "status": "failed",
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        # Reset failed login attempts on successful authentication
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(UTC)
        await self.user_repo.db.commit()

        # Generate Tokens
        access_token = create_access_token(user.id)
        raw_refresh_token = create_refresh_token(user.id)
        token_hash = hash_token(raw_refresh_token)

        refresh_exp = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repo.create(
            {
                "user_id": user.id,
                "token_hash": token_hash,
                "expires_at": refresh_exp,
            }
        )

        # Create Active Session
        session_exp = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        await self.session_repo.create(
            {
                "user_id": user.id,
                "device_name": user_agent,
                "browser": user_agent,
                "operating_system": "Web Client",
                "ip_address": ip_address,
                "refresh_token_hash": token_hash,
                "expires_at": session_exp,
                "revoked": False,
            }
        )

        # Record Login History
        await self.login_history_repo.create(
            {
                "user_id": user.id,
                "ip_address": ip_address,
                "device": user_agent,
                "browser": user_agent,
                "status": "success",
            }
        )

        full_user = await self.user_repo.get_with_roles(user.id) or user
        user_schema = UserWithRolesResponse.model_validate(full_user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_schema,
        )

    async def refresh_tokens(self, req: RefreshTokenRequest) -> TokenResponse:
        sub = decode_token(req.refresh_token, is_refresh=True)
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        token_hash = hash_token(req.refresh_token)
        stored_token = await self.refresh_token_repo.get_by_hash(token_hash)
        if not stored_token or stored_token.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Token rotation: revoke old refresh token
        await self.refresh_token_repo.revoke_token(token_hash)

        user_id = uuid.UUID(sub)
        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Issue new token pair
        new_access_token = create_access_token(user.id)
        new_raw_refresh_token = create_refresh_token(user.id)
        new_token_hash = hash_token(new_raw_refresh_token)

        refresh_exp = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repo.create(
            {
                "user_id": user.id,
                "token_hash": new_token_hash,
                "expires_at": refresh_exp,
            }
        )

        user_schema = UserWithRolesResponse.model_validate(user)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_schema,
        )

    async def logout(self, user_id: uuid.UUID, refresh_token: str | None = None) -> bool:
        if refresh_token:
            token_hash = hash_token(refresh_token)
            await self.refresh_token_repo.revoke_token(token_hash)
        await self.session_repo.revoke_all_sessions(user_id)
        return True

    async def change_password(self, user_id: uuid.UUID, req: ChangePasswordRequest) -> bool:
        user = await self.user_repo.get(user_id)
        if not user or not verify_password(req.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        pwd_errors = validate_password_strength(req.new_password)
        if pwd_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(pwd_errors)}",
            )

        # Check password history (prevent re-using previous passwords)
        history_items = await self.user_repo.db.execute(
            select(PasswordHistory).where(PasswordHistory.user_id == user_id).order_by(PasswordHistory.created_at.desc()).limit(3)
        )
        for h in history_items.scalars().all():
            if verify_password(req.new_password, h.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot reuse recently used password",
                )

        new_hash = hash_password(req.new_password)
        user.password_hash = new_hash
        await self.user_repo.db.commit()

        # Record password history
        password_hist = PasswordHistory(user_id=user.id, password_hash=new_hash)
        self.user_repo.db.add(password_hist)
        await self.user_repo.db.commit()
        return True

    async def forgot_password(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return "Password reset token created if account exists"

        raw_token = uuid.uuid4().hex
        exp = datetime.now(UTC) + timedelta(hours=1)
        await self.password_token_repo.create(
            {
                "user_id": user.id,
                "token": raw_token,
                "expires_at": exp,
                "used": False,
            }
        )
        return raw_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        token_obj = await self.password_token_repo.get_by_token(token)
        if not token_obj or token_obj.used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        exp_tz = token_obj.expires_at.replace(tzinfo=UTC) if token_obj.expires_at.tzinfo is None else token_obj.expires_at
        if exp_tz < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        pwd_errors = validate_password_strength(new_password)
        if pwd_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(pwd_errors)}",
            )

        user = await self.user_repo.get(token_obj.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        new_hash = hash_password(new_password)
        user.password_hash = new_hash
        token_obj.used = True
        await self.user_repo.db.commit()

        # Record password history
        password_hist = PasswordHistory(user_id=user.id, password_hash=new_hash)
        self.user_repo.db.add(password_hist)
        await self.user_repo.db.commit()
        return True

    async def verify_email(self, token: str) -> bool:
        token_obj = await self.email_token_repo.get_by_token(token)
        if not token_obj or token_obj.used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        exp_tz = token_obj.expires_at.replace(tzinfo=UTC) if token_obj.expires_at.tzinfo is None else token_obj.expires_at
        if exp_tz < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user = await self.user_repo.get(token_obj.user_id)
        if user:
            user.email_verified = True
            token_obj.used = True
            await self.user_repo.db.commit()
            return True
        return False
