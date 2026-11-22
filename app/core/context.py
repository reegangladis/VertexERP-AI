"""Execution context and thread-safe async ContextVars propagation."""

import uuid
from contextvars import ContextVar

# Context variable holders
_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_tenant_id_ctx: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)
_user_id_ctx: ContextVar[uuid.UUID | None] = ContextVar("user_id", default=None)


def get_correlation_id() -> str | None:
    """Retrieve active correlation ID from current execution context."""
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set active correlation ID in current execution context."""
    _correlation_id_ctx.set(correlation_id)


def get_tenant_id() -> uuid.UUID | None:
    """Retrieve active tenant ID from current execution context."""
    return _tenant_id_ctx.get()


def set_tenant_id(tenant_id: uuid.UUID | None) -> None:
    """Set active tenant ID in current execution context."""
    _tenant_id_ctx.set(tenant_id)


def get_user_id() -> uuid.UUID | None:
    """Retrieve active user ID from current execution context."""
    return _user_id_ctx.get()


def set_user_id(user_id: uuid.UUID | None) -> None:
    """Set active user ID in current execution context."""
    _user_id_ctx.set(user_id)
