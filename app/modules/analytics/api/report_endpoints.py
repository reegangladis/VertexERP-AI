"""Analytics Reports Execution and Export API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.analytics.schemas.report import (
    AnalyticsReportResponse,
    ReportExecutionRequest,
    ReportExecutionResponse,
)
from app.modules.analytics.services.reporting_service import ReportingService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(tags=["Analytics - Reports"])


class ReportListResponse(BaseModel):
    items: list[AnalyticsReportResponse]
    total: int


@router.get(
    "/reports",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_REPORTS_READ.value))],
)
async def list_reports(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ReportListResponse:
    """List available analytical report definitions."""
    service = ReportingService(db)
    items = await service.list_reports(tenant_id, org_id)
    return ReportListResponse(
        items=[AnalyticsReportResponse.model_validate(r) for r in items],
        total=len(items),
    )


@router.post(
    "/reports/{code}/execute",
    response_model=ReportExecutionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_REPORTS_READ.value))],
)
async def execute_report(
    code: str,
    req: ReportExecutionRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ReportExecutionResponse:
    """Runs parameterized analytical report with optional CSV export."""
    service = ReportingService(db)
    is_csv = req.format == "CSV"
    try:
        return await service.execute_report(
            tenant_id=tenant_id,
            org_id=org_id,
            report_code=code.upper(),
            parameters=req.parameters,
            user_id=user_id,
            export_csv=is_csv,
        )
    except ValueError as e:
        raise NotFoundException(str(e))
