import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    ExecutionTriggerRequest,
    WorkflowCreate,
    WorkflowExecutionResponse,
    WorkflowResponse,
    WorkflowUpdate,
    WorkflowVersionCreate,
    WorkflowVersionResponse,
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter()


def _get_org_id() -> uuid.UUID | None:
    """Placeholder tenant resolver — replaced by real auth middleware in production."""
    return None


# ─── Workflow CRUD ───────────────────────────────────────────────────────────────
@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    graph = (
        payload.graph_definition.model_dump()
        if payload.graph_definition
        else {"nodes": [], "edges": [], "layout": {}}
    )
    workflow = await repo.create_workflow(
        org_id,
        {
            "name": payload.name,
            "description": payload.description,
            "category": payload.category,
            "trigger_type": payload.trigger_type,
            "tags": payload.tags,
            "metadata_json": payload.metadata_json,
            "status": "draft",
        },
    )
    # Auto-create initial version
    version_data = {
        "workflow_id": workflow.id,
        "version_number": "1.0.0",
        "graph_definition": graph,
        "is_published": False,
        "changelog": "Initial version",
    }
    version = await repo.create_version(org_id, version_data)
    await db.commit()
    return workflow


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(
    status: str | None = Query(None),
    category: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_workflows(
        _get_org_id(), status=status, category=category, skip=skip, limit=limit
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    workflow = await repo.get_workflow(_get_org_id(), workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: uuid.UUID,
    payload: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    workflow = await repo.get_workflow(_get_org_id(), workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    updated = await repo.update_workflow(
        workflow, payload.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    workflow = await repo.get_workflow(_get_org_id(), workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await repo.delete_workflow(workflow)
    await db.commit()


# ─── Versioning ───────────────────────────────────────────────────────────────────
@router.get("/{workflow_id}/versions", response_model=list[WorkflowVersionResponse])
async def list_versions(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_versions(workflow_id)


@router.post(
    "/{workflow_id}/versions",
    response_model=WorkflowVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_version(
    workflow_id: uuid.UUID,
    payload: WorkflowVersionCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    version = await repo.create_version(
        org_id,
        {
            "workflow_id": workflow_id,
            "version_number": payload.version_number,
            "graph_definition": payload.graph_definition.model_dump(),
            "is_published": False,
            "changelog": payload.changelog,
        },
    )
    await db.commit()
    return version


@router.post(
    "/{workflow_id}/versions/{version_id}/publish",
    response_model=WorkflowVersionResponse,
)
async def publish_version(
    workflow_id: uuid.UUID,
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    version = await repo.get_version(version_id)
    if not version or version.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="Version not found")
    published = await repo.publish_version(version)
    await repo.update_workflow(
        await repo.get_workflow(_get_org_id(), workflow_id),
        {"active_version_id": version_id, "status": "published"},
    )
    await db.commit()
    return published


# ─── Execute Workflow ─────────────────────────────────────────────────────────────
@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: uuid.UUID,
    payload: ExecutionTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    workflow = await repo.get_workflow(org_id, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.status != "published":
        raise HTTPException(
            status_code=400, detail="Only published workflows can be executed"
        )
    engine = WorkflowEngine(db)
    execution = await engine.trigger_workflow(
        org_id=org_id,
        workflow_id=workflow_id,
        version_id=workflow.active_version_id,
        trigger_type=payload.trigger_type,
        input_payload=payload.input_payload,
        executed_by="api_user",
    )
    return execution


# ─── Export / Import ─────────────────────────────────────────────────────────────
@router.get("/{workflow_id}/export", response_model=dict[str, Any])
async def export_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    workflow = await repo.get_workflow(org_id, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    versions = await repo.list_versions(workflow_id)
    return {
        "workflow": {
            "name": workflow.name,
            "description": workflow.description,
            "category": workflow.category,
            "trigger_type": workflow.trigger_type,
            "tags": workflow.tags,
        },
        "versions": [
            {
                "version_number": v.version_number,
                "graph_definition": v.graph_definition,
                "changelog": v.changelog,
            }
            for v in versions
        ],
    }


@router.post(
    "/import", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED
)
async def import_workflow(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    wf_data = payload.get("workflow", {})
    workflow = await repo.create_workflow(
        org_id,
        {
            "name": wf_data.get("name", "Imported Workflow"),
            "description": wf_data.get("description"),
            "category": wf_data.get("category", "general"),
            "trigger_type": wf_data.get("trigger_type", "manual"),
            "tags": wf_data.get("tags"),
            "status": "draft",
        },
    )
    for v in payload.get("versions", []):
        await repo.create_version(
            org_id,
            {
                "workflow_id": workflow.id,
                "version_number": v.get("version_number", "1.0.0"),
                "graph_definition": v.get(
                    "graph_definition", {"nodes": [], "edges": [], "layout": {}}
                ),
                "is_published": False,
                "changelog": v.get("changelog"),
            },
        )
    await db.commit()
    return workflow
