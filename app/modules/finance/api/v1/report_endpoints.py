"""Financial Reports API Endpoints."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.schemas.reports import (
    BalanceSheetResponse,
    ProfitLossResponse,
    TrialBalanceResponse,
)
from app.modules.finance.services.report_service import FinancialReportService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/reports", tags=["Finance - Financial Reporting Statements"])


@router.get(
    "/trial-balance",
    response_model=TrialBalanceResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_REPORTS_READ.value))],
)
async def get_trial_balance(
    as_of_date: date | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> TrialBalanceResponse:
    target_date = as_of_date or date.today()
    service = FinancialReportService(db)
    return await service.get_trial_balance(target_date, tenant_id, org_id)


@router.get(
    "/balance-sheet",
    response_model=BalanceSheetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_REPORTS_READ.value))],
)
async def get_balance_sheet(
    as_of_date: date | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BalanceSheetResponse:
    target_date = as_of_date or date.today()
    service = FinancialReportService(db)
    return await service.get_balance_sheet(target_date, tenant_id, org_id)


@router.get(
    "/profit-loss",
    response_model=ProfitLossResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_REPORTS_READ.value))],
)
async def get_profit_loss(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProfitLossResponse:
    today = date.today()
    s_date = start_date or date(today.year, 1, 1)
    e_date = end_date or today
    service = FinancialReportService(db)
    return await service.get_profit_and_loss(s_date, e_date, tenant_id, org_id)
