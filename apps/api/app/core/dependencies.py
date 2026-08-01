import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.database.connection import get_db as _get_db
from app.database.redis import RedisService, get_redis_service


def get_settings() -> Settings:
    """Dependency provider returning the application settings."""
    return settings


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency provider for obtaining an asynchronous database session.

    Delegates to the database connection manager.
    """
    async for session in _get_db():
        yield session


async def get_redis() -> AsyncGenerator[RedisService]:
    """Dependency provider for obtaining the Redis cache service."""
    yield get_redis_service()


def get_logger(name: str):
    """Dependency generator that provides a configured logger instance for a given name."""

    def _logger_dependency() -> logging.Logger:
        return logging.getLogger(name)

    return _logger_dependency


# Authentication & Authorization dependencies
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import decode_token
from app.core.tenant import get_current_tenant_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str | None = Depends(oauth2_scheme)
) -> User:
    """Dependency to retrieve the currently authenticated user via JWT."""
    if not token:
        # Fallback for development/standalone environments when unauthenticated
        if settings.ENVIRONMENT in ("development", "testing", "standalone", "dev"):
            user_repo = UserRepository(db)
            try:
                users = await user_repo.get_all(limit=1)
                if users:
                    return users[0]
            except Exception:
                pass
            return User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                organization_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                email="system_admin@vertexerp.ai",
                first_name="System",
                last_name="Administrator",
                status="active",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id_str = decode_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
        
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )
        
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is suspended or locked",
        )

    # Validate Tenant Boundary
    active_tenant = get_current_tenant_id()
    if active_tenant and user.organization_id != active_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Tenant isolation mismatch",
        )
        
    return user


class PermissionChecker:
    """Dependency factory checking user permission credentials."""
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Super Admin override
        for role in current_user.roles:
            if role.name == "Super Admin":
                return current_user
            for perm in role.permissions:
                if perm.name == self.permission_name or perm.name == "admin.full":
                    return current_user
                    
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required permission: {self.permission_name}",
        )


class RoleChecker:
    """Dependency factory checking user role mappings."""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        for role in current_user.roles:
            if role.name in self.allowed_roles or role.name == "Super Admin":
                return current_user
                
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Required roles: {', '.join(self.allowed_roles)}",
        )
