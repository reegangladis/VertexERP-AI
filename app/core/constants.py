"""System-wide constants and immutable domain enumerations."""

from enum import StrEnum


class Environment(StrEnum):
    """Execution environment tiers."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    FREE = "free"


class LogLevel(StrEnum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ServiceStatus(StrEnum):
    """Component health & operational status."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


# Standard Headers
HEADER_CORRELATION_ID = "X-Correlation-ID"
HEADER_TENANT_ID = "X-Tenant-ID"
HEADER_IDEMPOTENCY_KEY = "Idempotency-Key"

# Problem Details standard media type (IETF RFC 7807)
MEDIA_TYPE_PROBLEM_JSON = "application/problem+json"
