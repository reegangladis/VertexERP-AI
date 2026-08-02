import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    WorkflowResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
)

router = APIRouter()


def _get_org_id() -> uuid.UUID | None:
    return None


@router.post(
    "/", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_template(
    payload: WorkflowTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    data = payload.model_dump()
    data["graph_definition"] = payload.graph_definition.model_dump()
    template = await repo.create_template(_get_org_id(), data)
    await db.commit()
    return template


@router.get("/", response_model=list[WorkflowTemplateResponse])
async def list_templates(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_templates(_get_org_id(), category=category)


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    template = await repo.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post(
    "/{template_id}/deploy",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def deploy_from_template(
    template_id: uuid.UUID,
    customization: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Instantiate a new workflow from a template."""
    repo = WorkflowRepository(db)
    org_id = _get_org_id()
    template = await repo.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    cust = customization or {}
    workflow = await repo.create_workflow(
        org_id,
        {
            "name": cust.get("name", f"[From Template] {template.name}"),
            "description": cust.get("description", template.description),
            "category": template.category,
            "trigger_type": "manual",
            "status": "draft",
            "tags": [],
        },
    )
    await repo.create_version(
        org_id,
        {
            "workflow_id": workflow.id,
            "version_number": "1.0.0",
            "graph_definition": template.graph_definition,
            "is_published": False,
            "changelog": f"Deployed from template: {template.name}",
        },
    )
    await db.commit()
    return workflow
