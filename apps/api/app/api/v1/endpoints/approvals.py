import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.workflow import (
    ApprovalActionPayload,
    ApprovalHistoryResponse,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
)
from app.services.approval_engine import ApprovalEngine

router = APIRouter()


def _get_org_id() -> uuid.UUID | None:
    return None


@router.post(
    "/", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED
)
async def create_approval_request(
    payload: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
):
    engine = ApprovalEngine(db)
    return await engine.create_approval_request(_get_org_id(), payload)


@router.get("/", response_model=list[ApprovalRequestResponse])
async def list_approvals(
    approver_id: str | None = Query(None),
    requester_id: str | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.workflow_repository import WorkflowRepository

    repo = WorkflowRepository(db)
    return await repo.list_approvals(
        _get_org_id(),
        approver_id=approver_id,
        requester_id=requester_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/pending/{approver_id}", response_model=list[ApprovalRequestResponse])
async def pending_for_approver(
    approver_id: str,
    db: AsyncSession = Depends(get_db),
):
    engine = ApprovalEngine(db)
    return await engine.list_pending_for_approver(_get_org_id(), approver_id)


@router.get("/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    engine = ApprovalEngine(db)
    approval = await engine.get_approval_with_history(_get_org_id(), approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval


@router.post("/{approval_id}/action", response_model=ApprovalRequestResponse)
async def process_approval_action(
    approval_id: uuid.UUID,
    payload: ApprovalActionPayload,
    db: AsyncSession = Depends(get_db),
):
    engine = ApprovalEngine(db)
    try:
        return await engine.process_action(_get_org_id(), approval_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{approval_id}/history", response_model=list[ApprovalHistoryResponse])
async def get_approval_history(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    engine = ApprovalEngine(db)
    return await engine.get_history(approval_id)


@router.post("/escalate-sla", response_model=list[ApprovalRequestResponse])
async def escalate_sla_breaches(
    db: AsyncSession = Depends(get_db),
):
    """System endpoint to auto-escalate SLA-breached approval requests."""
    engine = ApprovalEngine(db)
    return await engine.check_sla_escalations(_get_org_id())
