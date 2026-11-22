"""Domain exception hierarchy supporting IETF RFC 7807 Problem Details."""

from typing import Any


class AppException(Exception):
    """Base application exception from which all domain errors inherit."""

    status_code: int = 500
    error_type: str = "https://api.vertexerp.io/errors/internal-error"
    title: str = "Internal Server Error"

    def __init__(
        self,
        detail: str,
        invalid_params: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.invalid_params = invalid_params or []
        self.headers = headers or {}


class BadRequestException(AppException):
    """Raised when a request is invalid or violates domain business requirements."""

    status_code = 400
    error_type = "https://api.vertexerp.io/errors/bad-request"
    title = "Bad Request"


class NotFoundException(AppException):
    """Raised when a requested resource does not exist or is invisible due to RLS."""

    status_code = 404
    error_type = "https://api.vertexerp.io/errors/not-found"
    title = "Resource Not Found"


class ConflictException(AppException):
    """Raised on unique constraint violations or optimistic concurrency version conflicts."""

    status_code = 409
    error_type = "https://api.vertexerp.io/errors/conflict"
    title = "Conflict"


class ValidationException(AppException):
    """Raised on business invariant or domain schema validation failures."""

    status_code = 422
    error_type = "https://api.vertexerp.io/errors/validation-error"
    title = "Unprocessable Entity"


class UnauthorizedException(AppException):
    """Raised when authentication credentials are missing, invalid, or expired."""

    status_code = 401
    error_type = "https://api.vertexerp.io/errors/unauthorized"
    title = "Unauthorized"


class ForbiddenException(AppException):
    """Raised when authenticated identity lacks required RBAC/ABAC permissions."""

    status_code = 403
    error_type = "https://api.vertexerp.io/errors/forbidden"
    title = "Forbidden"


class DatabaseConnectionException(AppException):
    """Raised when database connection pool or PostgreSQL query execution fails."""

    status_code = 503
    error_type = "https://api.vertexerp.io/errors/database-unavailable"
    title = "Database Unavailable"


class RedisConnectionException(AppException):
    """Raised when in-memory Redis cluster is unreachable."""

    status_code = 503
    error_type = "https://api.vertexerp.io/errors/cache-unavailable"
    title = "Cache Unavailable"


# Aliases for domain semantics
PermissionDeniedException = ForbiddenException
BusinessRuleViolationException = BadRequestException
