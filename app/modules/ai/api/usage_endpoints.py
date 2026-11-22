"""AI Usage and Telemetry Endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.ai.schemas.usage import AIUsageSummaryResponse
from app.modules.ai.services.ai_usage_service import AIUsageService
from app.modules.ai.tools.registry import erp_tool_registry
from app.modules.identity.api.dependencies import (
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/usage", tags=["AI Telemetry & Tools"])


@router.get(
    "/summary",
    response_model=AIUsageSummaryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_USAGE_READ.value))],
)
async def get_usage_summary(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> AIUsageSummaryResponse:
    """Retrieve aggregated AI usage, token consumption, and dollar costs."""
    return await AIUsageService.get_usage_summary(
        db=db,
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/tools",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_TOOLS_EXECUTE.value))],
)
async def list_available_tools() -> dict[str, Any]:
    """List registered ERP domain tools available to AI Copilot."""
    tools = erp_tool_registry.get_all_tools()
    return {
        "count": len(tools),
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "action_type": t.action_type,
                "is_mutation": t.is_mutation,
                "parameters_schema": t.parameters_schema,
            }
            for t in tools
        ],
    }
