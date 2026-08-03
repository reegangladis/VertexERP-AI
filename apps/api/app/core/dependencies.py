import logging
import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.core.security import decode_token
from app.database.connection import get_db as _get_db
from app.database.redis import RedisService, get_redis_service
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


def get_settings() -> Settings:
    """Dependency provider returning the application settings."""
    return settings


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency provider for obtaining an asynchronous database session."""
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


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    """Dependency to retrieve the currently authenticated user via JWT."""
    if not token:
        # Development / Testing fallback
        if settings.ENVIRONMENT in ("development", "testing", "standalone", "dev"):
            user_repo = UserRepository(db)
            users = await user_repo.get_all(limit=1)
            if users:
                return await user_repo.get_with_roles(users[0].id) or users[0]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = decode_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from None

    user_repo = UserRepository(db)
    user = await user_repo.get_with_roles(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )

    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is suspended",
        )

    return user


class PermissionChecker:
    """Dependency factory checking user permission credentials."""

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # In dev/testing, if no roles assigned yet, default to admin access
        if not current_user.roles and settings.ENVIRONMENT in ("development", "testing", "standalone", "dev"):
            return current_user

        for role in current_user.roles:
            if role.name in ("Super Admin", "Admin", "Organization Admin"):
                return current_user
            for perm in role.permissions:
                if perm.code == self.permission_code or perm.code in ("admin.full", "*"):
                    return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required permission: {self.permission_code}",
        )


class RoleChecker:
    """Dependency factory checking user role mappings."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.roles and settings.ENVIRONMENT in ("development", "testing", "standalone", "dev"):
            return current_user

        for role in current_user.roles:
            if role.name in self.allowed_roles or role.name in ("Super Admin", "Admin", "Organization Admin"):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Allowed roles: {', '.join(self.allowed_roles)}",
        )
