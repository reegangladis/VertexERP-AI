import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    BusinessRuleCreate,
    BusinessRuleResponse,
    BusinessRuleUpdate,
    RuleEvaluationRequest,
    RuleEvaluationResult,
)
from app.services.rule_engine import RuleEngine

router = APIRouter()


def _get_org_id() -> uuid.UUID | None:
    return None


@router.post(
    "/", response_model=BusinessRuleResponse, status_code=status.HTTP_201_CREATED
)
async def create_rule(
    payload: BusinessRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    engine = RuleEngine(db)
    valid, msg = engine.validate_conditions_schema(payload.conditions_json)
    if not valid:
        raise HTTPException(status_code=422, detail=f"Invalid conditions schema: {msg}")
    repo = WorkflowRepository(db)
    rule = await repo.create_rule(_get_org_id(), payload.model_dump())
    await db.commit()
    return rule


@router.get("/", response_model=list[BusinessRuleResponse])
async def list_rules(
    rule_group: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    return await repo.list_rules(
        _get_org_id(), rule_group=rule_group, is_active=is_active
    )


@router.get("/groups")
async def list_rule_groups(db: AsyncSession = Depends(get_db)) -> list[str]:
    from sqlalchemy import distinct, select

    from app.models.workflow import BusinessRule

    stmt = select(distinct(BusinessRule.rule_group)).where(
        BusinessRule.organization_id == _get_org_id()
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


@router.get("/{rule_id}", response_model=BusinessRuleResponse)
async def get_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    rule = await repo.get_rule(_get_org_id(), rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Business rule not found")
    return rule


@router.patch("/{rule_id}", response_model=BusinessRuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    payload: BusinessRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    rule = await repo.get_rule(_get_org_id(), rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Business rule not found")
    updates = payload.model_dump(exclude_unset=True)
    if "conditions_json" in updates:
        engine = RuleEngine(db)
        valid, msg = engine.validate_conditions_schema(updates["conditions_json"])
        if not valid:
            raise HTTPException(
                status_code=422, detail=f"Invalid conditions schema: {msg}"
            )
    updated = await repo.update_rule(rule, updates)
    await db.commit()
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = WorkflowRepository(db)
    rule = await repo.get_rule(_get_org_id(), rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Business rule not found")
    await repo.delete_rule(rule)
    await db.commit()


@router.post("/evaluate", response_model=RuleEvaluationResult)
async def evaluate_rules(
    payload: RuleEvaluationRequest,
    db: AsyncSession = Depends(get_db),
):
    engine = RuleEngine(db)
    return await engine.evaluate_rules(_get_org_id(), payload)


@router.post("/{rule_id}/test")
async def test_rule(
    rule_id: uuid.UUID,
    context_data: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    engine = RuleEngine(db)
    return await engine.test_rule(rule_id, _get_org_id(), context_data)
