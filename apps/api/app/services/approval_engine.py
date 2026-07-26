"""
Approval Engine — handles single-level and multi-level approval workflows.
Supports: delegation, escalation, approval history, SLA due-date tracking.
"""
import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workflow_repository import WorkflowRepository
from app.models.workflow import ApprovalRequest, ApprovalHistory
from app.schemas.workflow import (
    ApprovalRequestCreate,
    ApprovalActionPayload,
    ApprovalRequestResponse,
    ApprovalHistoryResponse,
)


class ApprovalEngine:
    """Orchestrates multi-level approval workflows with delegation and escalation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    # ─── Create Request ──────────────────────────────────────────────────────────
    async def create_approval_request(
        self,
        org_id: Optional[uuid.UUID],
        data: ApprovalRequestCreate,
    ) -> ApprovalRequest:
        obj = await self.repo.create_approval(org_id, {
            "workflow_execution_id": data.workflow_execution_id,
            "step_key": data.step_key,
            "title": data.title,
            "description": data.description,
            "requester_id": data.requester_id,
            "approver_id": data.approver_id,
            "approver_role": data.approver_role,
            "level": data.level,
            "max_levels": data.max_levels,
            "status": "pending",
            "due_date": data.due_date,
            "escalation_user_id": data.escalation_user_id,
        })
        await self._record_history(org_id, obj.id, "created", data.requester_id, "Approval request created.")
        await self.db.commit()
        return obj

    # ─── Process Decision ────────────────────────────────────────────────────────
    async def process_action(
        self,
        org_id: Optional[uuid.UUID],
        approval_id: uuid.UUID,
        payload: ApprovalActionPayload,
    ) -> ApprovalRequest:
        approval = await self.repo.get_approval(org_id, approval_id)
        if not approval:
            raise ValueError("Approval request not found.")
        if approval.status not in ("pending", "delegated"):
            raise ValueError(f"Cannot process action on approval with status: {approval.status}")

        action = payload.action.lower()

        if action == "approve":
            new_status = await self._handle_approve(org_id, approval)
        elif action == "reject":
            new_status = "rejected"
        elif action == "delegate":
            if not payload.delegate_to_user_id:
                raise ValueError("delegate_to_user_id is required for delegation.")
            await self.repo.update_approval(approval, {"approver_id": payload.delegate_to_user_id})
            new_status = "delegated"
        elif action == "escalate":
            escalate_to = payload.escalate_to_user_id or approval.escalation_user_id
            if not escalate_to:
                raise ValueError("No escalation user defined.")
            await self.repo.update_approval(approval, {"approver_id": escalate_to, "level": approval.level + 1})
            new_status = "escalated"
        else:
            raise ValueError(f"Unknown approval action: {action}")

        updated = await self.repo.update_approval(approval, {"status": new_status})
        await self._record_history(
            org_id, approval_id, action, payload.actor_id,
            payload.comments or f"Action '{action}' performed.",
        )
        await self.db.commit()
        return updated

    async def _handle_approve(self, org_id: Optional[uuid.UUID], approval: ApprovalRequest) -> str:
        """Handle multi-level approval progression."""
        if approval.level < approval.max_levels:
            # Advance to next level
            await self.repo.update_approval(approval, {
                "level": approval.level + 1,
                "status": "pending",
            })
            return "pending"  # Still pending at next level
        return "approved"

    # ─── Escalation Check ────────────────────────────────────────────────────────
    async def check_sla_escalations(self, org_id: Optional[uuid.UUID]) -> List[ApprovalRequest]:
        """Find overdue pending approvals and escalate them automatically."""
        approvals = await self.repo.list_approvals(org_id, status="pending")
        escalated = []
        now = datetime.now(UTC)
        for approval in approvals:
            if approval.due_date and approval.due_date < now and approval.escalation_user_id:
                await self.repo.update_approval(approval, {
                    "status": "escalated",
                    "approver_id": approval.escalation_user_id,
                })
                await self._record_history(
                    org_id, approval.id, "auto_escalated",
                    "system", "Auto-escalated due to SLA breach."
                )
                escalated.append(approval)
        if escalated:
            await self.db.commit()
        return escalated

    # ─── Queries ─────────────────────────────────────────────────────────────────
    async def list_pending_for_approver(
        self,
        org_id: Optional[uuid.UUID],
        approver_id: str,
    ) -> List[ApprovalRequest]:
        return await self.repo.list_approvals(org_id, approver_id=approver_id, status="pending")

    async def get_approval_with_history(
        self, org_id: Optional[uuid.UUID], approval_id: uuid.UUID
    ) -> Optional[ApprovalRequest]:
        return await self.repo.get_approval(org_id, approval_id)

    async def get_history(self, approval_id: uuid.UUID) -> List[ApprovalHistory]:
        return await self.repo.list_approval_history(approval_id)

    # ─── Internal Helpers ────────────────────────────────────────────────────────
    async def _record_history(
        self,
        org_id: Optional[uuid.UUID],
        approval_id: uuid.UUID,
        action: str,
        actor_id: str,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalHistory:
        return await self.repo.create_approval_history(org_id, {
            "approval_request_id": approval_id,
            "action": action,
            "actor_id": actor_id,
            "comments": comments,
            "metadata_json": metadata or {},
        })
