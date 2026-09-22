"""Authentication service implementing zero-trust identity, session rotation, and MFA."""

import hashlib
import re
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.session import set_superuser_context, set_tenant_context
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.permissions import PermissionCode, SystemRole
from app.core.security import hash_password, verify_password
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.role import Permission, Role, UserRole
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserCredential, UserSession
from app.modules.identity.repositories.role_repository import RoleRepository
from app.modules.identity.repositories.session_repository import SessionRepository
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.identity.services.jwt_service import JwtService
from app.modules.identity.services.mfa_service import MfaService
from app.modules.identity.services.rbac_service import RbacService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant
from app.modules.organization.services.organization_service import OrganizationService


def ensure_utc(dt: datetime | None) -> datetime | None:
    """Ensures datetime is timezone-aware in UTC for multi-database compatibility."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


class AuthService:
    """Core identity service managing registration, authentication, sessions, and credentials."""

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self.session = session
        self.redis = redis
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.role_repo = RoleRepository(session)
        self.org_service = OrganizationService(session)
        self.rbac_service = RbacService(session, redis=redis)

    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Enforces NIST-compliant password strength policy."""
        if len(password) < 12:
            raise ValidationException("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValidationException("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationException("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValidationException("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
            raise ValidationException("Password must contain at least one special character")

    @staticmethod
    def hash_token(token: str) -> str:
        """SHA-256 hash helper for indexing refresh tokens safely."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def _seed_system_permissions_and_roles(
        self, tenant_id: uuid.UUID
    ) -> tuple[Role, Role, Role, Role]:
        """Ensures all system permissions exist and provisions default roles for a tenant."""
        all_perms_in_db = {p.code: p for p in await self.role_repo.get_all_permissions()}
        seeded_permissions: list[Permission] = []

        for code_enum in PermissionCode:
            code_str = code_enum.value
            if code_str not in all_perms_in_db:
                domain, resource, action = code_str.split(":", 2)
                perm = Permission(
                    code=code_str,
                    domain=domain,
                    resource=resource,
                    action=action,
                    description=f"Permission to {action} {resource} in {domain}",
                )
                await self.role_repo.create_permission(perm)
                all_perms_in_db[code_str] = perm
            seeded_permissions.append(all_perms_in_db[code_str])

        tenant_admin_role = await self.role_repo.get_role_by_code(
            SystemRole.TENANT_ADMIN.value, tenant_id
        )
        if not tenant_admin_role:
            tenant_admin_role = Role(
                tenant_id=tenant_id,
                name="Tenant Administrator",
                code=SystemRole.TENANT_ADMIN.value,
                description="Full administrative access across all tenant resources",
                is_system_role=True,
            )
            await self.role_repo.create_role(tenant_admin_role)
            await self.role_repo.assign_permissions_to_role(
                tenant_id=tenant_id,
                role_id=tenant_admin_role.id,
                permission_ids=[p.id for p in seeded_permissions],
            )

        org_admin_role = await self.role_repo.get_role_by_code(
            SystemRole.ORG_ADMIN.value, tenant_id
        )
        if not org_admin_role:
            org_admin_role = Role(
                tenant_id=tenant_id,
                name="Organization Administrator",
                code=SystemRole.ORG_ADMIN.value,
                description="Administrative access within assigned organization",
                is_system_role=True,
            )
            await self.role_repo.create_role(org_admin_role)
            org_perms = [
                p.id
                for p in seeded_permissions
                if not p.code.startswith("audit:security_events")
                and p.code != PermissionCode.ORGANIZATION_DELETE.value
            ]
            await self.role_repo.assign_permissions_to_role(
                tenant_id=tenant_id,
                role_id=org_admin_role.id,
                permission_ids=org_perms,
            )

        auditor_role = await self.role_repo.get_role_by_code(SystemRole.AUDITOR.value, tenant_id)
        if not auditor_role:
            auditor_role = Role(
                tenant_id=tenant_id,
                name="Compliance Auditor",
                code=SystemRole.AUDITOR.value,
                description="Read-only access to audit trails and security logs",
                is_system_role=True,
            )
            await self.role_repo.create_role(auditor_role)
            audit_perms = [
                p.id
                for p in seeded_permissions
                if p.code.startswith("audit:") or p.code.endswith(":read")
            ]
            await self.role_repo.assign_permissions_to_role(
                tenant_id=tenant_id,
                role_id=auditor_role.id,
                permission_ids=audit_perms,
            )

        user_role = await self.role_repo.get_role_by_code(SystemRole.STANDARD_USER.value, tenant_id)
        if not user_role:
            user_role = Role(
                tenant_id=tenant_id,
                name="Standard User",
                code=SystemRole.STANDARD_USER.value,
                description="Basic access within assigned organization",
                is_system_role=True,
            )
            await self.role_repo.create_role(user_role)
            user_perms = [
                p.id
                for p in seeded_permissions
                if p.code
                in (
                    PermissionCode.ORGANIZATION_READ.value,
                    PermissionCode.IDENTITY_USERS_READ.value,
                )
            ]
            await self.role_repo.assign_permissions_to_role(
                tenant_id=tenant_id,
                role_id=user_role.id,
                permission_ids=user_perms,
            )

        return tenant_admin_role, org_admin_role, auditor_role, user_role

    async def register(
        self, req: RegisterRequest, ip_address: str = "127.0.0.1", user_agent: str = "Unknown"
    ) -> tuple[User, Tenant, Organization, TokenResponse]:
        """Provisions a new Tenant, Primary Org, Admin User, and returns initial credentials."""
        self.validate_password_strength(req.password)

        # Create Tenant and initial Organization
        tenant, org = await self.org_service.create_tenant_with_default_org(
            tenant_name=req.tenant_name,
            tenant_slug=req.tenant_slug,
            org_name=req.organization_name,
            legal_name=req.organization_name,
            tax_identifier=req.tax_identifier,
        )

        # Scope the remainder of the bootstrap transaction to the new tenant.
        await set_tenant_context(self.session, tenant.id)

        # Seed system roles & permissions for this tenant
        admin_role, _, _, _ = await self._seed_system_permissions_and_roles(tenant.id)

        # Create Admin User
        user = User(
            tenant_id=tenant.id,
            email=req.email.lower().strip(),
            full_name=req.full_name.strip(),
            is_active=True,
            is_verified=True,
            default_organization_id=org.id,
        )
        await self.user_repo.create(user)

        # Create Credentials with Argon2id
        password_hash = hash_password(req.password)
        creds = UserCredential(
            tenant_id=tenant.id,
            user_id=user.id,
            password_hash=password_hash,
            salt=secrets.token_hex(16),
        )
        await self.user_repo.create_credentials(creds)

        # Create TenantMembership
        await self.org_service.add_membership(
            tenant_id=tenant.id,
            user_id=user.id,
            org_id=org.id,
            is_default=True,
        )

        # Assign TenantAdmin role to user for this organization
        user_role_assignment = UserRole(
            tenant_id=tenant.id,
            user_id=user.id,
            role_id=admin_role.id,
            organization_id=org.id,
        )
        await self.role_repo.assign_user_role(user_role_assignment)

        # Create Session & Issue Tokens
        raw_refresh_token = secrets.token_urlsafe(48)
        refresh_token_hash = self.hash_token(raw_refresh_token)
        session_jti = f"sess_{uuid.uuid4().hex}"
        session_expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        user_session = UserSession(
            tenant_id=tenant.id,
            user_id=user.id,
            organization_id=org.id,
            jti=session_jti,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=session_expires_at,
            last_active_at=datetime.now(UTC),
        )
        await self.session_repo.create(user_session)

        # Resolve Roles and Permissions
        roles, permissions = await self.rbac_service.get_user_roles_and_permissions(user.id, org.id)

        access_token, token_jti, expires_in = JwtService.create_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            organization_id=org.id,
            roles=roles,
            permissions=permissions,
            session_id=user_session.id,
            jti=session_jti,
        )

        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=raw_refresh_token,
            user_id=user.id,
            tenant_id=tenant.id,
            organization_id=org.id,
            roles=roles,
            permissions=permissions,
        )

        await AuditService.log_security_event(
            session=self.session,
            event_type="AUTH_REGISTER_SUCCESS",
            description=f"User {user.email} registered tenant '{tenant.slug}' successfully",
            severity="INFO",
            tenant_id=tenant.id,
            user_id=user.id,
            client_ip=ip_address,
            user_agent=user_agent,
        )

        return user, tenant, org, token_response

    async def login(
        self, req: LoginRequest, ip_address: str = "127.0.0.1", user_agent: str = "Unknown"
    ) -> TokenResponse:
        """Authenticates user credentials, evaluates MFA challenges, and issues tokens."""
        email_clean = req.email.lower().strip()

        # Login is a controlled authentication bootstrap path: no tenant
        # context exists until credentials identify the tenant. Temporarily
        # bypass RLS for these lookup queries, then immediately scope the
        # transaction to the authenticated tenant.
        await set_superuser_context(self.session, True)

        # Find user
        tenant_id: uuid.UUID | None = None
        if req.tenant_slug:
            tenant = await self.org_service.org_repo.get_tenant_by_slug(req.tenant_slug)
            if not tenant:
                raise UnauthorizedException("Invalid email or password")
            tenant_id = tenant.id

        user = await self.user_repo.get_by_email(email_clean, tenant_id=tenant_id)
        if not user:
            await AuditService.log_security_event(
                session=self.session,
                event_type="AUTH_LOGIN_FAILED",
                description=f"Login attempt failed for nonexistent user {email_clean}",
                severity="WARNING",
                client_ip=ip_address,
                user_agent=user_agent,
            )
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active or user.is_deleted:
            raise UnauthorizedException("User account is inactive or disabled")

        await set_superuser_context(self.session, False)
        await set_tenant_context(self.session, user.tenant_id)

        # Check Credentials
        creds = await self.user_repo.get_credentials(user.id)
        if not creds:
            raise UnauthorizedException("Invalid email or password")

        now = datetime.now(UTC)
        locked_until_utc = ensure_utc(creds.locked_until)
        if locked_until_utc is not None and locked_until_utc > now:
            await AuditService.log_security_event(
                session=self.session,
                event_type="AUTH_LOGIN_LOCKED",
                description=f"Login attempt on locked account for user {user.email}",
                severity="WARNING",
                tenant_id=user.tenant_id,
                user_id=user.id,
                client_ip=ip_address,
                user_agent=user_agent,
            )
            raise UnauthorizedException(
                "Account is temporarily locked due to multiple failed login attempts. "
                "Please try again later."
            )

        # Verify Password with Argon2id
        if not verify_password(req.password, creds.password_hash):
            await self.user_repo.record_failed_login(user.id)
            await AuditService.log_security_event(
                session=self.session,
                event_type="AUTH_LOGIN_FAILED",
                description=f"Invalid password for user {user.email}",
                severity="WARNING",
                tenant_id=user.tenant_id,
                user_id=user.id,
                client_ip=ip_address,
                user_agent=user_agent,
            )
            raise UnauthorizedException("Invalid email or password")

        # Password valid: reset failed attempts
        await self.user_repo.reset_failed_login(user.id)

        # Check Active Organization Context
        active_org_id = user.default_organization_id
        if not active_org_id:
            memberships = await self.org_service.get_user_memberships(user.tenant_id, user.id)
            if not memberships:
                raise ForbiddenException("User has no active organization memberships")
            active_org_id = memberships[0].organization_id

        # Check MFA
        if user.mfa_enabled:
            mfa_setting = await self.user_repo.get_mfa_setting(user.id)
            if mfa_setting and mfa_setting.is_enabled:
                if not req.mfa_code:
                    challenge_token = JwtService.create_mfa_challenge_token(
                        user_id=user.id,
                        tenant_id=user.tenant_id,
                        organization_id=active_org_id,
                    )
                    return TokenResponse(
                        access_token="",
                        token_type="bearer",
                        expires_in=300,
                        user_id=user.id,
                        tenant_id=user.tenant_id,
                        organization_id=active_org_id,
                        roles=[],
                        permissions=[],
                        mfa_required=True,
                        mfa_challenge_token=challenge_token,
                    )

                # Verify TOTP code with replay attack protection or recovery code
                totp_valid = await MfaService.verify_code_with_replay_prevention(
                    mfa_setting.secret_encrypted, req.mfa_code, user_id=user.id, redis=self.redis
                )
                if not totp_valid:
                    recovery_valid, updated_codes = MfaService.verify_recovery_code(
                        mfa_setting.recovery_codes_hashed, req.mfa_code
                    )
                    if recovery_valid:
                        mfa_setting.recovery_codes_hashed = updated_codes
                        await self.user_repo.save_mfa_setting(mfa_setting)
                    else:
                        await AuditService.log_security_event(
                            session=self.session,
                            event_type="AUTH_MFA_FAILED",
                            description=f"Invalid MFA code for user {user.email}",
                            severity="WARNING",
                            tenant_id=user.tenant_id,
                            user_id=user.id,
                            client_ip=ip_address,
                            user_agent=user_agent,
                        )
                        raise UnauthorizedException("Invalid MFA authentication code")

        # Create Session & Issue Tokens
        raw_refresh_token = secrets.token_urlsafe(48)
        refresh_token_hash = self.hash_token(raw_refresh_token)
        session_jti = f"sess_{uuid.uuid4().hex}"
        session_expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        user_session = UserSession(
            tenant_id=user.tenant_id,
            user_id=user.id,
            organization_id=active_org_id,
            jti=session_jti,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=session_expires_at,
            last_active_at=datetime.now(UTC),
        )
        await self.session_repo.create(user_session)

        # Resolve Roles and Permissions
        roles, permissions = await self.rbac_service.get_user_roles_and_permissions(
            user.id, active_org_id
        )

        access_token, token_jti, expires_in = JwtService.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            organization_id=active_org_id,
            roles=roles,
            permissions=permissions,
            session_id=user_session.id,
            jti=session_jti,
        )

        await AuditService.log_security_event(
            session=self.session,
            event_type="AUTH_LOGIN_SUCCESS",
            description=f"User {user.email} logged in successfully",
            severity="INFO",
            tenant_id=user.tenant_id,
            user_id=user.id,
            client_ip=ip_address,
            user_agent=user_agent,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=raw_refresh_token,
            user_id=user.id,
            tenant_id=user.tenant_id,
            organization_id=active_org_id,
            roles=roles,
            permissions=permissions,
        )

    async def refresh_tokens(
        self, raw_refresh_token: str, ip_address: str = "127.0.0.1", user_agent: str = "Unknown"
    ) -> TokenResponse:
        """
        Validates refresh token, executes token rotation, and detects replay attack reuse.
        If a token is reused after rotation, ALL sessions for the user are immediately revoked.
        """
        token_hash = self.hash_token(raw_refresh_token)
        # Refresh tokens are the second authentication bootstrap path. The
        # tenant is discovered from the opaque token record, then RLS is
        # immediately narrowed to that tenant.
        await set_superuser_context(self.session, True)
        user_session = await self.session_repo.get_by_refresh_token_hash(token_hash)
        if user_session:
            await set_superuser_context(self.session, False)
            await set_tenant_context(self.session, user_session.tenant_id)

        now = datetime.now(UTC)
        expires_at_utc = ensure_utc(user_session.expires_at) if user_session else None
        if (
            not user_session
            or user_session.is_revoked
            or (expires_at_utc is not None and expires_at_utc <= now)
        ):
            # Replay Attack Detection via Redis Rotated Token History
            reused_user_id = None
            if self.redis:
                reused_user_id = await self.redis.get(f"token:rotated:{token_hash}")

            if reused_user_id:
                victim_uid = (
                    uuid.UUID(reused_user_id)
                    if isinstance(reused_user_id, str)
                    else uuid.UUID(reused_user_id.decode())
                )
                await self.revoke_all_sessions(victim_uid)
                await AuditService.log_security_event(
                    session=self.session,
                    event_type="SECURITY_REPLAY_ATTACK_DETECTED",
                    description=(
                        "Replay attack detected on rotated refresh token. "
                        f"All sessions revoked for user {victim_uid}."
                    ),
                    severity="CRITICAL",
                    user_id=victim_uid,
                    client_ip=ip_address,
                    user_agent=user_agent,
                )
            elif user_session and user_session.is_revoked:
                # Active reuse detected! Revoke all sessions for this user immediately
                await self.revoke_all_sessions(user_session.user_id)
                await AuditService.log_security_event(
                    session=self.session,
                    event_type="SECURITY_REPLAY_ATTACK_DETECTED",
                    description=(
                        "Replay attack detected on revoked refresh token. "
                        f"All sessions revoked for user {user_session.user_id}."
                    ),
                    severity="CRITICAL",
                    tenant_id=user_session.tenant_id,
                    user_id=user_session.user_id,
                    client_ip=ip_address,
                    user_agent=user_agent,
                )
            raise UnauthorizedException("Invalid or expired refresh token")

        # Record consumed token in rotated history
        if self.redis:
            await self.redis.set(
                f"token:rotated:{token_hash}", str(user_session.user_id), ex=30 * 86400
            )

        # Blacklist old session JTI in Redis
        await JwtService.blacklist_jti(self.redis, user_session.jti)
        await JwtService.blacklist_jti(self.redis, str(user_session.id))

        user = await self.user_repo.get_by_id(
            user_session.user_id, tenant_id=user_session.tenant_id
        )
        if not user or not user.is_active or user.is_deleted:
            await self.session_repo.revoke_session(user_session.id)
            raise UnauthorizedException("User account is inactive or disabled")

        # Rotate token
        new_raw_refresh_token = secrets.token_urlsafe(48)
        new_token_hash = self.hash_token(new_raw_refresh_token)
        new_session_jti = f"sess_{uuid.uuid4().hex}"

        user_session.jti = new_session_jti
        user_session.refresh_token_hash = new_token_hash
        user_session.ip_address = ip_address
        user_session.user_agent = user_agent
        user_session.last_active_at = now
        user_session.expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.session.flush()

        active_org_id = user_session.organization_id or user.default_organization_id
        if not active_org_id:
            raise UnauthorizedException("No active organization context found for session")

        # Resolve Roles and Permissions
        roles, permissions = await self.rbac_service.get_user_roles_and_permissions(
            user.id, active_org_id
        )

        access_token, token_jti, expires_in = JwtService.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            organization_id=active_org_id,
            roles=roles,
            permissions=permissions,
            session_id=user_session.id,
            jti=new_session_jti,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=new_raw_refresh_token,
            user_id=user.id,
            tenant_id=user.tenant_id,
            organization_id=active_org_id,
            roles=roles,
            permissions=permissions,
        )

    async def logout(
        self, user_id: uuid.UUID, session_id: uuid.UUID | None, jti: str | None = None
    ) -> None:
        """Revokes the current session and blacklists the JTI in Redis."""
        if session_id:
            await self.session_repo.revoke_session(session_id)
            await JwtService.blacklist_jti(self.redis, str(session_id))
        if jti:
            await JwtService.blacklist_jti(self.redis, jti)

        await AuditService.log_security_event(
            session=self.session,
            event_type="AUTH_LOGOUT",
            description=f"User {user_id} logged out successfully",
            severity="INFO",
            user_id=user_id,
        )

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        """Revokes all active sessions for a user across all devices."""
        active_sessions = await self.session_repo.list_active_user_sessions(user_id)
        for s in active_sessions:
            await JwtService.blacklist_jti(self.redis, s.jti)
            await JwtService.blacklist_jti(self.redis, str(s.id))
        await self.session_repo.revoke_all_for_user(user_id)

        await AuditService.log_security_event(
            session=self.session,
            event_type="AUTH_ALL_SESSIONS_REVOKED",
            description=f"All active sessions revoked for user {user_id}",
            severity="WARNING",
            user_id=user_id,
        )

    async def change_password(self, user_id: uuid.UUID, req: PasswordChangeRequest) -> None:
        """Changes user password, validates complexity, and revokes all active sessions."""
        self.validate_password_strength(req.new_password)
        creds = await self.user_repo.get_credentials(user_id)
        if not creds:
            raise NotFoundException("User credentials not found")

        if not verify_password(req.current_password, creds.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        creds.password_hash = hash_password(req.new_password)
        creds.password_changed_at = datetime.now(UTC)
        await self.session.flush()

        # Revoke all active sessions to force re-authentication
        await self.revoke_all_sessions(user_id)

        await AuditService.log_security_event(
            session=self.session,
            event_type="AUTH_PASSWORD_CHANGED",
            description=f"Password changed for user {user_id}",
            severity="INFO",
            user_id=user_id,
        )
