import uuid
from contextvars import ContextVar

# Thread-local / Asyncio context variable to hold organization ID dynamically
_tenant_id_context: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)

def get_current_tenant_id() -> uuid.UUID | None:
    """Retrieves the active tenant ID from async context."""
    return _tenant_id_context.get()

def set_current_tenant_id(tenant_id: uuid.UUID | None) -> None:
    """Sets the active tenant ID inside async context."""
    _tenant_id_context.set(tenant_id)
