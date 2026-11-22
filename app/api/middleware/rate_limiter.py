"""Enterprise Sliding-Window Rate Limiting Middleware with Redis persistence and in-memory fallback."""

from __future__ import annotations

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger("vertexerp.middleware.ratelimit")

# In-memory sliding window cache as zero-dependency fallback
_in_memory_windows: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-Window Rate Limiting Middleware.
    Applies differentiated rate limits based on path category:
    - Auth routes (/api/v1/auth/*, /identity/auth/*): Configured per IP (default 10 in prod, 500 in dev/test)
    - AI Copilot routes (/api/v1/ai/*): Configured per User/IP (default 30 in prod, 300 in dev/test)
    - Standard API routes (/api/v1/*): Configured per IP (default 120 in prod, 1000 in dev/test)
    - Health checks (/health/*, /): Exempt from rate limits
    """

    def __init__(
        self,
        app,
        auth_limit: int | None = None,
        ai_limit: int | None = None,
        default_limit: int | None = None,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.auth_limit = (
            auth_limit if auth_limit is not None else settings.RATE_LIMIT_AUTH_PER_MINUTE
        )
        self.ai_limit = ai_limit if ai_limit is not None else settings.RATE_LIMIT_AI_PER_MINUTE
        self.default_limit = (
            default_limit if default_limit is not None else settings.RATE_LIMIT_DEFAULT_PER_MINUTE
        )
        self.window_seconds = window_seconds

    def _get_rate_limit_for_path(self, path: str) -> tuple[int, str]:
        """Returns the rate limit threshold and bucket category for a given path."""
        if (
            path.startswith("/health")
            or path == "/"
            or path.startswith("/docs")
            or path.startswith("/openapi")
        ):
            return 0, "exempt"
        if "/auth" in path:
            return self.auth_limit, "auth"
        if "/ai" in path:
            return self.ai_limit, "ai"
        return self.default_limit, "default"

    def _get_client_ip(self, request: Request) -> str:
        """Extracts client IP safely with reverse proxy support."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "127.0.0.1"

    async def _check_rate_limit_redis(
        self,
        redis,
        key: str,
        limit: int,
        window: int,
    ) -> tuple[bool, int, int]:
        """
        Sliding-window counter via Redis sorted set.
        Returns: (is_allowed, remaining, retry_after)
        """
        now = time.time()
        window_start = now - window
        pipe = redis.pipeline()
        # Remove timestamps older than window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count requests in window
        pipe.zcard(key)
        # Add current timestamp
        pipe.zadd(key, {str(now): now})
        # Set TTL on set
        pipe.expire(key, window + 1)
        results = await pipe.execute()

        current_count = results[1]
        if current_count >= limit:
            # Over limit - fetch earliest item to calculate retry_after
            earliest = await redis.zrange(key, 0, 0, withscores=True)
            retry_after = int(window)
            if earliest:
                earliest_time = earliest[0][1]
                retry_after = max(1, int(window - (now - earliest_time)))
            return False, 0, retry_after

        remaining = max(0, limit - (current_count + 1))
        return True, remaining, 0

    def _check_rate_limit_memory(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> tuple[bool, int, int]:
        """In-memory sliding window fallback."""
        now = time.time()
        window_start = now - window
        timestamps = _in_memory_windows[key]

        # Prune older entries
        _in_memory_windows[key] = [t for t in timestamps if t > window_start]
        current_count = len(_in_memory_windows[key])

        if current_count >= limit:
            earliest = _in_memory_windows[key][0]
            retry_after = max(1, int(window - (now - earliest)))
            return False, 0, retry_after

        _in_memory_windows[key].append(now)
        remaining = max(0, limit - (current_count + 1))
        return True, remaining, 0

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        limit, category = self._get_rate_limit_for_path(request.url.path)
        if limit == 0:  # Exempt route
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        rate_key = f"ratelimit:{category}:{client_ip}"

        redis = None
        try:
            from app.infrastructure.redis import client as redis_module

            if redis_module.redis_client is not None:
                redis = redis_module.redis_client
        except Exception:
            pass

        is_allowed = True
        remaining = limit
        retry_after = 0

        if redis is not None:
            try:
                is_allowed, remaining, retry_after = await self._check_rate_limit_redis(
                    redis, rate_key, limit, self.window_seconds
                )
            except Exception as exc:
                logger.warning(
                    "Redis rate limiter failed (%s), falling back to in-memory rate limiting", exc
                )
                is_allowed, remaining, retry_after = self._check_rate_limit_memory(
                    rate_key, limit, self.window_seconds
                )
        else:
            is_allowed, remaining, retry_after = self._check_rate_limit_memory(
                rate_key, limit, self.window_seconds
            )

        if not is_allowed:
            logger.warning(
                "Rate limit exceeded for client '%s' on path '%s' (category='%s')",
                client_ip,
                request.url.path,
                category,
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "type": "https://errors.vertexerp.io/rate-limit-exceeded",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": f"Rate limit exceeded for category '{category}'. Please retry after {retry_after} seconds.",
                    "retry_after_seconds": retry_after,
                },
            )
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + retry_after))
            return response

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
