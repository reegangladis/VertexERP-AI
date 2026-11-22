"""Action Proposal & Confirmation Token Store for Safe AI Mutations."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.exceptions import BusinessRuleViolationException, PermissionDeniedException
from app.modules.ai.schemas.copilot import PendingActionProposal


class PendingAction:
    def __init__(
        self,
        action_id: str,
        action_type: str,
        tool_name: str,
        parameters: dict[str, Any],
        preview_summary: str,
        tenant_id: UUID,
        user_id: UUID,
        confirmation_token: str,
        expires_at: datetime,
    ):
        self.action_id = action_id
        self.action_type = action_type
        self.tool_name = tool_name
        self.parameters = parameters
        self.preview_summary = preview_summary
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.confirmation_token = confirmation_token
        self.expires_at = expires_at
        self.consumed = False


class ActionConfirmationManager:
    """Manages ephemeral action proposals requiring explicit human-in-the-loop confirmation."""

    def __init__(self, ttl_minutes: int = 15):
        self.ttl_minutes = ttl_minutes
        self._store: dict[str, PendingAction] = {}

    def create_proposal(
        self,
        tool_name: str,
        action_type: str,
        parameters: dict[str, Any],
        preview_summary: str,
        tenant_id: UUID,
        user_id: UUID,
    ) -> PendingActionProposal:
        """Create and store a pending action proposal with confirmation token."""
        action_id = f"act_{uuid.uuid4().hex[:12]}"
        confirmation_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(minutes=self.ttl_minutes)

        action = PendingAction(
            action_id=action_id,
            action_type=action_type,
            tool_name=tool_name,
            parameters=parameters,
            preview_summary=preview_summary,
            tenant_id=tenant_id,
            user_id=user_id,
            confirmation_token=confirmation_token,
            expires_at=expires_at,
        )
        self._store[action_id] = action

        return PendingActionProposal(
            action_id=action_id,
            action_type=action_type,
            tool_name=tool_name,
            parameters=parameters,
            preview_summary=preview_summary,
            expires_at=expires_at,
            confirmation_token=confirmation_token,
            requires_confirmation=True,
        )

    def verify_and_consume(
        self,
        action_id: str,
        confirmation_token: str,
        tenant_id: UUID,
        user_id: UUID,
    ) -> PendingAction:
        """Verify token, tenant isolation, and expiry, then mark proposal consumed.

        Raises BusinessRuleViolationException or PermissionDeniedException.
        """
        action = self._store.get(action_id)
        if not action:
            raise BusinessRuleViolationException(
                f"Action proposal '{action_id}' not found or already consumed."
            )

        if action.consumed:
            raise BusinessRuleViolationException(
                f"Action proposal '{action_id}' has already been executed."
            )

        if datetime.now(UTC) > action.expires_at:
            del self._store[action_id]
            raise BusinessRuleViolationException(
                f"Action proposal '{action_id}' has expired. Please ask the AI to re-draft."
            )

        if str(action.tenant_id) != str(tenant_id):
            raise PermissionDeniedException("Cross-tenant confirmation forbidden.")

        if str(action.user_id) != str(user_id):
            raise PermissionDeniedException("Action can only be confirmed by the initiating user.")

        if not secrets.compare_digest(action.confirmation_token, confirmation_token):
            raise PermissionDeniedException("Invalid confirmation token.")

        # Mark as consumed
        action.consumed = True
        return action


# Singleton manager
action_confirmation_manager = ActionConfirmationManager()
