import uuid
from datetime import datetime, UTC
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.organization import OrganizationRepository, SecuritySettingRepository
from app.repositories.role import RoleRepository
from app.repositories.session import SessionRepository, RefreshTokenRepository
from app.services.audit import AuditService, LoginHistoryService
from app.services.user import UserService
from app.services.organization import OrganizationService
from app.services.session import SessionService
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(
        self,
        user_service: UserService,
        org_service: OrganizationService,
        session_service: SessionService,
        refresh_token_repo: RefreshTokenRepository,
        role_repo: RoleRepository,
        audit_service: AuditService,
        login_history_service: LoginHistoryService,
        security_setting_repo: SecuritySettingRepository
    ):
        self.user_service = user_service
        self.org_service = org_service
        self.session_service = session_service
        self.refresh_token_repo = refresh_token_repo
        self.role_repo = role_repo
        self.audit_service = audit_service
        self.login_history_service = login_history_service
        self.security_setting_repo = security_setting_repo

    async def register(self, user_data: dict, org_name: str, org_slug: str, ip_address: str, user_agent: str) -> User:
        # 1. Verify user unique constraints
        existing_email = await self.user_service.get_by_email(user_data["email"])
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        existing_username = await self.user_service.get_by_username(user_data["username"])
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")

        # 2. Verify organization slug unique constraints
        existing_org = await self.org_service.get_by_slug(org_slug)
        if existing_org:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization Slug is already in use")

        # 3. Create Organization & defaults
        org = await self.org_service.create_organization(org_name, org_slug, user_data["email"])

        # 4. Create User
        user_data["organization_id"] = org.id
        user_data["email_verified"] = False
        user_data["phone_verified"] = False
        user_data["status"] = "active"
        
        user = await self.user_service.create_user(user_data)

        # 5. Assign default Organization Admin Role
        admin_role = await self.role_repo.get_by_name("Organization Admin")
        if admin_role:
            user.roles.append(admin_role)
            await self.user_service.repository.db.commit()

        # 6. Set organization created_by back to user ID
        await self.org_service.repository.update(org, {"created_by": user.id})

        # 7. Audit actions
        await self.audit_service.log_action(
            user.id,
            org.id,
            "user.register",
            ip_address,
            user_agent,
            {"organization_name": org_name, "organization_slug": org_slug}
        )

        return user

    async def login(self, email: str, password: str, ip_address: str, user_agent: str) -> dict:
        user = await self.user_service.get_by_email(email)
        
        if not user:
            # Audit failed attempt
            await self.login_history_service.log_login(
                None, email, ip_address, user_agent, "Other", "Other", "failed", "Invalid credentials"
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        # Fetch security settings for organization
        threshold = 5
        duration = 15
        if user.organization_id:
            sec_set = await self.security_setting_repo.get_by_org_id(user.organization_id)
            if sec_set:
                threshold = sec_set.account_lockout_threshold
                duration = sec_set.account_lockout_duration_minutes

        # Check lock
        if await self.user_service.is_account_locked(user):
            await self.login_history_service.log_login(
                user.id, email, ip_address, user_agent, "Other", "Other", "failed", "Account is locked"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is locked. Please try again after {user.locked_until.strftime('%H:%M UTC')}"
            )

        # Verify Password
        if not verify_password(password, user.password_hash):
            await self.user_service.increment_failed_attempts(user, threshold, duration)
            await self.login_history_service.log_login(
                user.id, email, ip_address, user_agent, "Other", "Other", "failed", "Invalid credentials"
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        # Reset failed attempts
        await self.user_service.reset_failed_attempts(user)

        # Update last login timestamp
        await self.user_service.repository.update(user, {"last_login": datetime.now(UTC)})

        # Create active Session
        session = await self.session_service.create_session(user.id, ip_address, user_agent)

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Store Refresh Token
        await self.refresh_token_repo.create({
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": datetime.now(UTC) + timedelta(days=7)
        })

        # Audit successful login
        from app.services.session import parse_user_agent
        browser, os = parse_user_agent(user_agent)
        await self.login_history_service.log_login(
            user.id, email, ip_address, user_agent, browser, os, "success"
        )
        await self.audit_service.log_action(
            user.id, user.organization_id, "user.login", ip_address, user_agent
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "session_id": str(session.id)
        }

    async def logout(self, refresh_token: str, user_id: uuid.UUID, ip_address: str, user_agent: str) -> None:
        # Revoke Refresh Token
        await self.refresh_token_repo.revoke_token(refresh_token)
        
        # Deactivate user sessions
        await self.session_service.revoke_all_user_sessions(user_id)

        # Log audit
        await self.audit_service.log_action(
            user_id, None, "user.logout", ip_address, user_agent
        )

    async def refresh_tokens(self, refresh_token: str, ip_address: str, user_agent: str) -> dict:
        db_token = await self.refresh_token_repo.get_by_token(refresh_token)
        
        if not db_token or db_token.is_revoked or db_token.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        # Decode token
        sub = decode_token(refresh_token, is_refresh=True)
        if not sub or str(db_token.user_id) != sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token signature")

        # Rotate token: revoke old token
        await self.refresh_token_repo.revoke_token(refresh_token)

        # Generate new tokens
        user_id = db_token.user_id
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        # Save new refresh token
        await self.refresh_token_repo.create({
            "user_id": user_id,
            "token": new_refresh_token,
            "expires_at": datetime.now(UTC) + timedelta(days=7)
        })

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
