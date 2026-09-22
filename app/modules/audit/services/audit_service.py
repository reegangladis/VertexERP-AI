"""Audit service for logging immutable security events and data mutations."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_correlation_id
from app.core.logging import logger
from app.modules.audit.models.audit_entry import AuditLogEntry, SecurityEventLog


class AuditService:
    """Service for capturing tamper-evident security telemetry and mutation logs."""

    @staticmethod
    async def log_security_event(
        session: AsyncSession,
        event_type: str,
        description: str,
        severity: str = "INFO",
        tenant_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> SecurityEventLog:
        """Records a security event in the database and structured logger."""
        corr_id = get_correlation_id()
        event_log = SecurityEventLog(
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            client_ip=client_ip,
            user_agent=user_agent,
            details=details or {},
            correlation_id=corr_id,
        )
        session.add(event_log)
        logger.info(
            "Security Event Recorded",
            event_type=event_type,
            severity=severity,
            tenant_id=str(tenant_id) if tenant_id else None,
            user_id=str(user_id) if user_id else None,
            description=description,
        )
        return event_log

    @staticmethod
    async def log_mutation(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID,
        actor_id: uuid.UUID | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLogEntry:
        """Records an entity state change into the audit vault."""
        corr_id = get_correlation_id()
        entry = AuditLogEntry(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values or {},
            new_values=new_values or {},
            client_ip=client_ip,
            user_agent=user_agent,
            correlation_id=corr_id,
        )
        session.add(entry)
        return entry
