"""Centralized Workflow & Approval Router.

Aggregates approval items from HR (Leave, Attendance Regularization), CRM (Quotations),
and Finance (Expense Claims) into a unified inbox for managers and administrators.
"""

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import get_current_user
from app.modules.crm.models import Quotation
from app.modules.hr.models.attendance import AttendanceRecord, AttendanceRegularization
from app.modules.hr.models.employee import Employee
from app.modules.hr.models.leave import LeaveBalance, LeaveRequest
from app.modules.identity.models.user import User

workflow_router = APIRouter(prefix="/workflows", tags=["Workflows & Approvals"])


class ApprovalActionRequest(BaseModel):
    action: Literal["APPROVE", "REJECT", "RETURN"]
    comments: str | None = Field(default=None, max_length=500)


class UnifiedApprovalItem(BaseModel):
    id: str
    entity_type: str  # LEAVE, REGULARIZATION, QUOTATION, EXPENSE
    entity_id: str
    requester_name: str
    requester_email: str | None = None
    title: str
    summary: str
    amount: float | None = None
    currency: str | None = "USD"
    status: str
    priority: str = "MEDIUM"
    created_at: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class WorkflowStats(BaseModel):
    pending_total: int
    pending_leaves: int
    pending_regularizations: int
    pending_quotations: int
    approved_this_month: int
    rejected_this_month: int


@workflow_router.get("/inbox", response_model=list[UnifiedApprovalItem])
async def get_approval_inbox(
    category: str | None = Query(None, description="Filter by category: LEAVE, REGULARIZATION, QUOTATION"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UnifiedApprovalItem]:
    """Retrieve all pending items requiring management sign-off."""
    items: list[UnifiedApprovalItem] = []

    # 1. Fetch Pending Leaves
    if not category or category == "LEAVE":
        leave_stmt = (
            select(LeaveRequest, Employee, User)
            .join(Employee, LeaveRequest.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id, isouter=True)
            .where(
                LeaveRequest.tenant_id == current_user.tenant_id,
                LeaveRequest.status.in_(["SUBMITTED", "PENDING", "DRAFT"]),
            )
            .order_by(LeaveRequest.created_at.desc())
        )
        leave_result = await db.execute(leave_stmt)
        for req, emp, u in leave_result.all():
            full_name = f"{emp.first_name} {emp.last_name}" if emp else "Employee"
            items.append(
                UnifiedApprovalItem(
                    id=f"leave_{req.id}",
                    entity_type="LEAVE",
                    entity_id=str(req.id),
                    requester_name=full_name,
                    requester_email=u.email if u else None,
                    title=f"Leave Request: {req.total_days} Day(s)",
                    summary=f"{req.start_date} to {req.end_date} - {req.reason}",
                    status=req.status,
                    priority="HIGH" if float(req.total_days) >= 3 else "MEDIUM",
                    created_at=req.created_at.isoformat() if req.created_at else None,
                    details={
                        "start_date": str(req.start_date),
                        "end_date": str(req.end_date),
                        "total_days": float(req.total_days),
                        "reason": req.reason,
                    },
                )
            )

    # 2. Fetch Pending Attendance Regularizations
    if not category or category == "REGULARIZATION":
        reg_stmt = (
            select(AttendanceRegularization, Employee, User)
            .join(Employee, AttendanceRegularization.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id, isouter=True)
            .where(
                AttendanceRegularization.tenant_id == current_user.tenant_id,
                AttendanceRegularization.status == "PENDING",
            )
            .order_by(AttendanceRegularization.created_at.desc())
        )
        reg_result = await db.execute(reg_stmt)
        for reg, emp, u in reg_result.all():
            full_name = f"{emp.first_name} {emp.last_name}" if emp else "Employee"
            items.append(
                UnifiedApprovalItem(
                    id=f"reg_{reg.id}",
                    entity_type="REGULARIZATION",
                    entity_id=str(reg.id),
                    requester_name=full_name,
                    requester_email=u.email if u else None,
                    title="Attendance Regularization Request",
                    summary=f"Discrepancy Correction: {reg.reason}",
                    status=reg.status,
                    priority="MEDIUM",
                    created_at=reg.created_at.isoformat() if reg.created_at else None,
                    details={
                        "requested_check_in": reg.requested_check_in.isoformat() if reg.requested_check_in else None,
                        "requested_check_out": reg.requested_check_out.isoformat() if reg.requested_check_out else None,
                        "reason": reg.reason,
                    },
                )
            )

    # 3. Fetch Pending Quotations
    if not category or category == "QUOTATION":
        quote_stmt = (
            select(Quotation)
            .where(
                Quotation.tenant_id == current_user.tenant_id,
                Quotation.status.in_(["DRAFT", "SENT", "PENDING_APPROVAL"]),
            )
            .order_by(Quotation.created_at.desc())
        )
        quote_result = await db.execute(quote_stmt)
        for q in quote_result.scalars().all():
            items.append(
                UnifiedApprovalItem(
                    id=f"quote_{q.id}",
                    entity_type="QUOTATION",
                    entity_id=str(q.id),
                    requester_name="Sales Team",
                    title=f"Quote Approval: {q.quotation_number}",
                    summary=f"Commercial proposal value: ${float(q.grand_total):,.2f}",
                    amount=float(q.grand_total),
                    currency="USD",
                    status=q.status,
                    priority="HIGH" if float(q.grand_total) > 25000 else "MEDIUM",
                    created_at=q.created_at.isoformat() if q.created_at else None,
                    details={
                        "subtotal": float(q.subtotal),
                        "tax_amount": float(q.tax_amount),
                        "grand_total": float(q.grand_total),
                        "valid_until": str(q.valid_until) if q.valid_until else None,
                    },
                )
            )

    return items


@workflow_router.get("/stats", response_model=WorkflowStats)
async def get_workflow_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowStats:
    """Retrieve high-level approval queue KPI counts."""
    # Leaves
    leaves_res = await db.execute(
        select(LeaveRequest.status).where(
            LeaveRequest.tenant_id == current_user.tenant_id,
        )
    )
    all_leaves = leaves_res.scalars().all()
    pending_leaves = sum(1 for s in all_leaves if s in ("SUBMITTED", "PENDING", "DRAFT"))
    approved_leaves = sum(1 for s in all_leaves if s == "APPROVED")
    rejected_leaves = sum(1 for s in all_leaves if s == "REJECTED")

    # Regularizations
    regs_res = await db.execute(
        select(AttendanceRegularization.status).where(
            AttendanceRegularization.tenant_id == current_user.tenant_id,
        )
    )
    all_regs = regs_res.scalars().all()
    pending_regs = sum(1 for s in all_regs if s == "PENDING")
    approved_regs = sum(1 for s in all_regs if s == "APPROVED")
    rejected_regs = sum(1 for s in all_regs if s == "REJECTED")

    # Quotes
    quotes_res = await db.execute(
        select(Quotation.status).where(
            Quotation.tenant_id == current_user.tenant_id,
        )
    )
    all_quotes = quotes_res.scalars().all()
    pending_quotes = sum(1 for s in all_quotes if s in ("DRAFT", "PENDING_APPROVAL", "SENT"))
    approved_quotes = sum(1 for s in all_quotes if s in ("APPROVED", "CONVERTED"))
    rejected_quotes = sum(1 for s in all_quotes if s == "REJECTED")

    return WorkflowStats(
        pending_total=pending_leaves + pending_regs + pending_quotes,
        pending_leaves=pending_leaves,
        pending_regularizations=pending_regs,
        pending_quotations=pending_quotes,
        approved_this_month=approved_leaves + approved_regs + approved_quotes,
        rejected_this_month=rejected_leaves + rejected_regs + rejected_quotes,
    )


@workflow_router.post("/{entity_type}/{entity_id}/action")
async def process_approval_action(
    entity_type: str,
    entity_id: uuid.UUID,
    payload: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Execute approval, rejection, or return with audit tracking."""
    entity_upper = entity_type.upper()
    now = datetime.now(UTC)

    new_status = "APPROVED" if payload.action == "APPROVE" else "REJECTED" if payload.action == "REJECT" else "RETURNED"

    if entity_upper == "LEAVE":
        from decimal import Decimal
        leave_stmt = select(LeaveRequest).where(
            LeaveRequest.id == entity_id,
            LeaveRequest.tenant_id == current_user.tenant_id,
        )
        leave_res = await db.execute(leave_stmt)
        leave_req = leave_res.scalar_one_or_none()
        if not leave_req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")

        leave_req.status = new_status
        leave_req.approver_id = current_user.id
        leave_req.approved_at = now
        leave_req.remarks = payload.comments

        # Sync LeaveBalance atomically
        bal_stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == leave_req.employee_id,
            LeaveBalance.leave_type_id == leave_req.leave_type_id,
            LeaveBalance.fiscal_year == leave_req.start_date.year,
            LeaveBalance.tenant_id == current_user.tenant_id,
        )
        bal_res = await db.execute(bal_stmt)
        balance = bal_res.scalar_one_or_none()
        if balance:
            req_days = Decimal(str(leave_req.total_days))
            pending_days = Decimal(str(balance.pending_days or 0))
            used_days = Decimal(str(balance.used_days or 0))
            balance_days = Decimal(str(balance.balance_days or 0))
            if new_status == "APPROVED":
                balance.pending_days = max(Decimal("0.0"), pending_days - req_days)
                balance.used_days = used_days + req_days
                balance.balance_days = max(Decimal("0.0"), balance_days - req_days)
            elif new_status in ("REJECTED", "RETURNED"):
                balance.pending_days = max(Decimal("0.0"), pending_days - req_days)
            balance.updated_at = now

        await db.commit()

    elif entity_upper == "REGULARIZATION":
        stmt = (
            update(AttendanceRegularization)
            .where(
                AttendanceRegularization.id == entity_id,
                AttendanceRegularization.tenant_id == current_user.tenant_id,
            )
            .values(
                status=new_status,
                approver_id=current_user.id,
                approved_at=now,
                remarks=payload.comments,
            )
        )
        res = await db.execute(stmt)
        if res.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regularization request not found.")
        await db.commit()

    elif entity_upper == "QUOTATION":
        stmt = (
            update(Quotation)
            .where(
                Quotation.id == entity_id,
                Quotation.tenant_id == current_user.tenant_id,
            )
            .values(status=new_status)
        )
        res = await db.execute(stmt)
        if res.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found.")
        await db.commit()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported entity type '{entity_type}'. Must be LEAVE, REGULARIZATION, or QUOTATION.",
        )

    return {
        "success": True,
        "entity_type": entity_upper,
        "entity_id": str(entity_id),
        "new_status": new_status,
        "processed_by": str(current_user.id),
        "timestamp": now.isoformat(),
    }
