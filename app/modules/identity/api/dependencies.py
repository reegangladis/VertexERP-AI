"""FastAPI dependencies for zero-trust authentication, tenant isolation, and RBAC authorization."""

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import set_tenant_id, set_user_id
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.permissions import PermissionCode, SystemRole
from app.infrastructure.database.session import get_db, set_tenant_context
from app.infrastructure.redis.client import get_redis_client
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserSession
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.services.jwt_service import JwtService
from app.modules.identity.services.rbac_service import RbacService


async def get_optional_redis(request: Request) -> Redis | None:
    """Helper to retrieve redis client or None if cache is disabled/mocked."""
    try:
        return await get_redis_client()
    except Exception:
        return None


async def get_current_user_claims(
    request: Request,
    redis: Redis | None = Depends(get_optional_redis),
) -> dict[str, Any]:
    """
    Extracts, decodes, and cryptographically verifies JWT access token.
    Validates token against Redis revocation list in < 1ms.
    """
    token: str | None = None
    auth_header = request.headers.get("Authorization")

    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedException("Authentication token required")

    try:
        claims = JwtService.verify_token(token)
    except Exception as exc:
        raise UnauthorizedException(f"Invalid authentication token: {exc}") from exc

    if claims.get("token_type") != "access":
        raise UnauthorizedException("Invalid token type: expected access token")

    jti = claims.get("jti")
    if jti and await JwtService.is_jti_blacklisted(redis, jti):
        raise UnauthorizedException("Token has been revoked")

    session_id = claims.get("session_id")
    if session_id and await JwtService.is_jti_blacklisted(redis, str(session_id)):
        raise UnauthorizedException("Session has been revoked")

    tenant_id_str = claims.get("tenant_id")
    if tenant_id_str:
        try:
            set_tenant_id(uuid.UUID(tenant_id_str))
        except ValueError:
            pass

    user_id_str = claims.get("sub")
    if user_id_str:
        try:
            set_user_id(uuid.UUID(user_id_str))
        except ValueError:
            pass

    return claims


async def get_current_user(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolves authenticated active User entity enforcing tenant and active session boundary."""
    user_id_str = claims.get("sub")
    tenant_id_str = claims.get("tenant_id")
    session_id_str = claims.get("session_id")

    if not user_id_str or not tenant_id_str:
        raise UnauthorizedException("Malformed authentication token claims")

    try:
        user_id = uuid.UUID(user_id_str)
        tenant_id = uuid.UUID(tenant_id_str)
    except ValueError as exc:
        raise UnauthorizedException("Invalid identifier in token claims") from exc

    set_tenant_id(tenant_id)
    set_user_id(user_id)
    await set_tenant_context(db, tenant_id)

    # Database defense-in-depth: Verify session is not revoked
    if session_id_str:
        try:
            session_id = uuid.UUID(session_id_str)
            session_stmt = select(UserSession).where(UserSession.id == session_id)
            session_res = await db.execute(session_stmt)
            active_session = session_res.scalar_one_or_none()
            if active_session and active_session.is_revoked:
                raise UnauthorizedException("Session has been revoked")
        except ValueError:
            pass

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id, tenant_id=tenant_id)

    if not user or not user.is_active or user.is_deleted:
        raise UnauthorizedException("User account is inactive, disabled, or does not exist")

    return user


async def get_current_user_id(
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> uuid.UUID:
    """Returns the authenticated user ID from token claims."""
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Missing user context in token")
    return uuid.UUID(user_id_str)


async def get_current_tenant_id(
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> uuid.UUID:
    """Returns the authenticated tenant ID from token claims."""
    tenant_id_str = claims.get("tenant_id")
    if not tenant_id_str:
        raise UnauthorizedException("Missing tenant context in token")
    try:
        tenant_id = uuid.UUID(tenant_id_str)
    except ValueError as exc:
        raise UnauthorizedException("Invalid tenant identifier in token claims") from exc
    set_tenant_id(tenant_id)
    return tenant_id


async def get_current_organization_id(
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> uuid.UUID:
    """Returns the active organization ID from token claims."""
    org_id_str = claims.get("org_id")
    if not org_id_str:
        raise UnauthorizedException("Missing organization context in token")
    return uuid.UUID(org_id_str)


def require_permission(permission_code: str) -> Callable[..., Any]:
    """
    Factory creating a dependency that enforces the caller holds the required permission.
    Resolves fine-grained permissions server-side from authoritative RBAC storage/cache.
    For TenantAdmin/SystemAdmin, preserves full administrative authorization semantics.
    Fails closed with HTTP 403 Forbidden.
    """

    async def _permission_checker(
        claims: dict[str, Any] = Depends(get_current_user_claims),
        db: AsyncSession = Depends(get_db),
        redis: Redis | None = Depends(get_optional_redis),
    ) -> dict[str, Any]:
        roles: list[str] = claims.get("roles", [])
        admin_roles = {SystemRole.TENANT_ADMIN.value, "SystemAdmin", "Administrator"}
        is_admin = any(r in admin_roles for r in roles)

        if "permissions" not in claims:
            if is_admin:
                claims["permissions"] = [p.value for p in PermissionCode]
                permissions = claims["permissions"]
            else:
                user_id_str = claims.get("sub")
                org_id_str = claims.get("org_id")
                tenant_id_str = claims.get("tenant_id")

                if not user_id_str or not org_id_str:
                    raise ForbiddenException(f"Missing required permission: '{permission_code}'")

                try:
                    user_id = uuid.UUID(user_id_str)
                    org_id = uuid.UUID(org_id_str)
                    tenant_id = uuid.UUID(tenant_id_str) if tenant_id_str else None
                except ValueError:
                    raise ForbiddenException(f"Missing required permission: '{permission_code}'")

                rbac_service = RbacService(db, redis=redis)
                resolved_roles, permissions = await rbac_service.get_user_roles_and_permissions(
                    user_id=user_id, organization_id=org_id, tenant_id=tenant_id, roles=roles
                )
                claims["permissions"] = permissions
                if not claims.get("roles"):
                    claims["roles"] = resolved_roles
        else:
            permissions = claims["permissions"]

        if permission_code not in permissions and not is_admin:
            raise ForbiddenException(f"Missing required permission: '{permission_code}'")
        return claims

    return _permission_checker
