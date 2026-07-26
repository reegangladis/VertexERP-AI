import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.services.workflow_engine import WorkflowEngine
from app.schemas.workflow import (
    WorkflowExecutionResponse,
    WorkflowExecutionDetailResponse,
    WorkflowStepResponse,
    WorkflowLogResponse,
)

router = APIRouter()


def _get_org_id() -> Optional[uuid.UUID]:
    return None


@router.get("/", response_model=List[WorkflowExecutionResponse])
async def list_executions(
    workflow_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_executions(_get_org_id(), workflow_id=workflow_id, status=status, skip=skip, limit=limit)


@router.get("/{execution_id}", response_model=WorkflowExecutionDetailResponse)
async def get_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    execution = await repo.get_execution_with_steps(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/{execution_id}/steps", response_model=List[WorkflowStepResponse])
async def list_steps(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_steps(execution_id)


@router.get("/{execution_id}/logs", response_model=List[WorkflowLogResponse])
async def list_logs(
    execution_id: uuid.UUID,
    log_level: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_logs(execution_id, log_level=log_level, skip=skip, limit=limit)


@router.post("/{execution_id}/cancel", response_model=WorkflowExecutionResponse)
async def cancel_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    execution = await repo.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status not in ("running", "pending"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel execution with status: {execution.status}")
    engine = WorkflowEngine(db)
    cancelled = await engine.cancel_execution(execution, _get_org_id())
    await db.commit()
    return cancelled


@router.post("/{execution_id}/retry", response_model=WorkflowExecutionResponse)
async def retry_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    execution = await repo.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status not in ("failed", "cancelled"):
        raise HTTPException(status_code=400, detail="Only failed or cancelled executions can be retried")
    engine = WorkflowEngine(db)
    new_execution = await engine.trigger_workflow(
        org_id=_get_org_id(),
        workflow_id=execution.workflow_id,
        version_id=execution.version_id,
        trigger_type=execution.trigger_type,
        input_payload=execution.input_payload or {},
        executed_by="retry_system",
    )
    return new_execution
