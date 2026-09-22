"""Immutable Compliance Audit Logging Subsystem for VertexERP AI V2."""

from __future__ import annotations

import uuid
from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.context import get_correlation_id, get_tenant_id, get_user_id

audit_structlog = structlog.get_logger("vertexerp.audit")


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    tenant_id: str | None
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    status: str
    correlation_id: str
    changes_summary: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class AuditLogger:
    """Thread-safe compliance and security audit event emitter."""

    def __init__(self, max_buffer: int = 500) -> None:
        self.max_buffer = max_buffer
        self._event_buffer: deque[AuditEvent] = deque(maxlen=max_buffer)

    def record(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        status: str = "SUCCESS",
        changes_summary: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> AuditEvent:
        """Emits an immutable structured audit log entry and appends to the compliance ring buffer."""
        event_id = f"aud_{uuid.uuid4().hex}"
        now_iso = datetime.now(UTC).isoformat()
        corr_id = get_correlation_id() or "unknown"
        t_id = tenant_id or (str(get_tenant_id()) if get_tenant_id() else None)
        u_id = user_id or (str(get_user_id()) if get_user_id() else None)

        event = AuditEvent(
            event_id=event_id,
            timestamp=now_iso,
            tenant_id=t_id,
            user_id=u_id,
            action=action.upper(),
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            status=status.upper(),
            correlation_id=corr_id,
            changes_summary=changes_summary,
            metadata=metadata,
        )

        self._event_buffer.append(event)

        # Emit to structured audit log
        audit_structlog.info(
            "Audit event captured",
            event_id=event.event_id,
            audit_action=event.action,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            audit_status=event.status,
            tenant_id=event.tenant_id,
            user_id=event.user_id,
            correlation_id=event.correlation_id,
            changes=changes_summary,
        )
        return event

    def get_events(
        self,
        tenant_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Retrieves recent audit events filtered optionally by tenant."""
        events = list(self._event_buffer)
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        return [asdict(e) for e in reversed(events[-limit:])]


# Global Audit Logger Singleton
audit_logger = AuditLogger()
