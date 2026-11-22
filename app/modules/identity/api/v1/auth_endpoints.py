"""Authentication API endpoints for registration, login, rotation, and sessions."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_user,
    get_current_user_claims,
    get_optional_redis,
)
from app.modules.identity.models.user import User
from app.modules.identity.repositories.session_repository import SessionRepository
from app.modules.identity.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
)
from app.modules.identity.services.auth_service import AuthService
from app.modules.identity.services.rbac_service import RbacService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, token_resp: TokenResponse) -> None:
    """Helper to set secure, HttpOnly cookies for access and refresh tokens."""
    if token_resp.access_token:
        response.set_cookie(
            key="access_token",
            value=token_resp.access_token,
            httponly=True,
            secure=settings.APP_ENV.value in ("staging", "production"),
            samesite="lax",
            max_age=token_resp.expires_in,
        )
    if token_resp.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token_resp.refresh_token,
            httponly=True,
            secure=settings.APP_ENV.value in ("staging", "production"),
            samesite="lax",
            max_age=30 * 24 * 3600,
        )


def _clear_auth_cookies(response: Response) -> None:
    """Helper to remove authentication cookies upon logout."""
    secure = settings.APP_ENV.value in ("staging", "production")
    response.delete_cookie(key="access_token", httponly=True, secure=secure, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, secure=secure, samesite="lax")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Tenant and Root Administrator",
)
async def register(
    req: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> TokenResponse:
    """Provisions a new Tenant, Primary Org, Admin User, and issues tokens."""
    auth_service = AuthService(db, redis)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    _, _, _, token_resp = await auth_service.register(
        req, ip_address=client_ip, user_agent=user_agent
    )
    _set_auth_cookies(response, token_resp)
    return token_resp


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate User and Issue Token Pair",
)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> TokenResponse:
    """Validates user credentials, processes MFA challenges, and creates an active session."""
    auth_service = AuthService(db, redis)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    token_resp = await auth_service.login(req, ip_address=client_ip, user_agent=user_agent)
    if not token_resp.mfa_required:
        _set_auth_cookies(response, token_resp)
    return token_resp


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate Refresh Token and Issue New Access Token",
)
async def refresh_tokens(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> TokenResponse:
    """Executes single-use refresh token rotation and checks for token reuse replay attacks."""
    raw_token = (
        body.refresh_token if body and body.refresh_token else None
    ) or request.cookies.get("refresh_token")
    if not raw_token:
        raise UnauthorizedException("Refresh token required")

    auth_service = AuthService(db, redis)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    token_resp = await auth_service.refresh_tokens(
        raw_token, ip_address=client_ip, user_agent=user_agent
    )
    _set_auth_cookies(response, token_resp)
    return token_resp


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate Current Session and Invalidate Tokens",
)
async def logout(
    response: Response,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> None:
    """Revokes the current session and adds JTI to the Redis blacklist."""
    auth_service = AuthService(db, redis)
    user_id = uuid.UUID(claims["sub"])
    session_id = uuid.UUID(claims["session_id"]) if claims.get("session_id") else None
    jti = claims.get("jti")

    await auth_service.logout(user_id=user_id, session_id=session_id, jti=jti)
    _clear_auth_cookies(response)


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Active User Sessions",
)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SessionResponse]:
    """Retrieves all active concurrent sessions for the authenticated user."""
    session_repo = SessionRepository(db)
    sessions = await session_repo.list_active_user_sessions(current_user.id)
    return [SessionResponse.model_validate(s) for s in sessions]


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke Specific Session",
)
async def revoke_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> None:
    """Revokes a specific session belonging to the authenticated user."""
    session_repo = SessionRepository(db)
    sessions = await session_repo.list_active_user_sessions(current_user.id)
    target = next((s for s in sessions if s.id == session_id), None)
    if target:
        auth_service = AuthService(db, redis)
        await auth_service.logout(user_id=current_user.id, session_id=target.id, jti=target.jti)


@router.post(
    "/sessions/revoke-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke All User Sessions Across All Devices",
)
async def revoke_all_sessions(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> None:
    """Revokes all active sessions across all devices and clears auth cookies."""
    auth_service = AuthService(db, redis)
    await auth_service.revoke_all_sessions(current_user.id)
    _clear_auth_cookies(response)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change User Password and Invalidate Existing Sessions",
)
async def change_password(
    req: PasswordChangeRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> None:
    """Updates user password and revokes all active sessions."""
    auth_service = AuthService(db, redis)
    await auth_service.change_password(current_user.id, req)
    _clear_auth_cookies(response)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User and Permissions",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> CurrentUserResponse:
    """Returns the authenticated user session profile, tenant context, and active permissions."""
    tenant_id = (
        uuid.UUID(claims["tenant_id"])
        if "tenant_id" in claims
        else current_user.tenant_id
    )
    org_id = (
        uuid.UUID(claims["org_id"])
        if "org_id" in claims
        else current_user.default_organization_id
    )

    roles = claims.get("roles", [])
    permissions = claims.get("permissions")

    if permissions is None and org_id is not None:
        rbac_service = RbacService(db, redis=redis)
        db_roles, db_perms = await rbac_service.get_user_roles_and_permissions(
            current_user.id, org_id, tenant_id=tenant_id
        )
        if not roles:
            roles = db_roles
        permissions = db_perms

    return CurrentUserResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tenant_id=tenant_id,
        organization_id=org_id,
        roles=roles,
        permissions=permissions or [],
        is_active=current_user.is_active,
    )
