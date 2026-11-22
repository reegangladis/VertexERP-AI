"""JWT Token issuance, cryptographic verification, and Redis blacklist integration."""

import contextlib
import uuid
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings
from app.core.security import create_jwt_token, decode_jwt_token


class JwtService:
    """Service managing asymmetric RS256 / HMAC JWT tokens and Redis revocation lists."""

    @staticmethod
    def create_access_token(
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        roles: list[str],
        permissions: list[str] | None = None,
        session_id: uuid.UUID | None = None,
        jti: str | None = None,
    ) -> tuple[str, str, int]:
        """Issues a short-lived slim access token with identity, session, and role claims."""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_jti = jti or f"jti_{uuid.uuid4().hex}"
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "org_id": str(organization_id),
            "session_id": str(session_id) if session_id else str(uuid.uuid4()),
            "roles": roles,
            "jti": token_jti,
            "token_type": "access",
        }
        token = create_jwt_token(payload, expires_delta)
        expires_in = int(expires_delta.total_seconds())
        return token, token_jti, expires_in

    @staticmethod
    def create_mfa_challenge_token(
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> str:
        """Issues an ephemeral MFA challenge token valid for 5 minutes."""
        expires_delta = timedelta(minutes=5)
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "org_id": str(organization_id),
            "token_type": "mfa_challenge",
            "jti": f"mfa_{uuid.uuid4().hex}",
        }
        return create_jwt_token(payload, expires_delta)

    @staticmethod
    def verify_token(token: str) -> dict[str, Any]:
        """Decodes and cryptographically verifies token claims."""
        return decode_jwt_token(token)

    @staticmethod
    async def is_jti_blacklisted(redis: Redis | None, jti: str) -> bool:
        """Checks if a JWT ID has been revoked in the Redis blacklist."""
        if not redis:
            return False
        try:
            return bool(await redis.exists(f"token:blacklist:{jti}"))
        except Exception:
            return False

    @staticmethod
    async def blacklist_jti(redis: Redis | None, jti: str, ttl_seconds: int = 900) -> None:
        """Adds a revoked JWT ID to the Redis blacklist with a TTL."""
        if not redis:
            return
        with contextlib.suppress(Exception):
            await redis.set(f"token:blacklist:{jti}", "revoked", ex=ttl_seconds)
