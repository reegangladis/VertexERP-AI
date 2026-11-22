"""Analytics KPI Endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.analytics.schemas.aggregation import AnalyticsFilterParams
from app.modules.analytics.schemas.kpi import (
    KPIDefinitionCreate,
    KPIDefinitionResponse,
    MetricCardData,
)
from app.modules.analytics.services.kpi_service import KPIService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(tags=["Analytics - KPIs & Metrics"])


class KPIDefinitionListResponse(BaseModel):
    items: list[KPIDefinitionResponse]
    total: int


class ExecutiveSummaryResponse(BaseModel):
    kpis: list[MetricCardData]
    period_label: str


@router.get(
    "/kpis",
    response_model=KPIDefinitionListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_KPIS_READ.value))],
)
async def list_kpis(
    category: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionListResponse:
    """List KPI definitions with benchmark thresholds."""
    service = KPIService(db)
    items = await service.get_kpi_definitions(tenant_id, org_id, category=category)
    return KPIDefinitionListResponse(
        items=[KPIDefinitionResponse.model_validate(k) for k in items],
        total=len(items),
    )


@router.post(
    "/kpis",
    response_model=KPIDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_KPIS_MANAGE.value))],
)
async def create_kpi(
    data: KPIDefinitionCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionResponse:
    """Create a new KPI definition."""
    service = KPIService(db)
    kpi = await service.create_kpi_definition(tenant_id, org_id, data)
    return KPIDefinitionResponse.model_validate(kpi)


@router.post(
    "/kpis/{code}/calculate",
    response_model=MetricCardData,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_KPIS_READ.value))],
)
async def calculate_kpi(
    code: str,
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MetricCardData:
    """Calculates specific KPI metric with delta comparisons."""
    service = KPIService(db)
    return await service.calculate_kpi(tenant_id, org_id, code.upper(), params)


DOMAIN_SUMMARY_KPI_MAP: dict[str, list[str]] = {
    "EXECUTIVE": [
        "FIN_GROSS_REVENUE",
        "FIN_NET_PROFIT_MARGIN",
        "SALES_PIPELINE_VALUE",
        "INV_TOTAL_VALUATION",
        "MFG_FIRST_PASS_YIELD",
        "HR_TOTAL_HEADCOUNT",
    ],
    "FINANCE": [
        "FIN_GROSS_REVENUE",
        "FIN_NET_PROFIT_MARGIN",
        "FIN_OUTSTANDING_AR",
        "FIN_OUTSTANDING_AP",
    ],
    "SALES": [
        "SALES_PIPELINE_VALUE",
        "SALES_WIN_RATE",
        "SALES_NEW_LEADS",
        "SALES_BOOKINGS_TOTAL",
    ],
    "INVENTORY": [
        "INV_TOTAL_VALUATION",
        "INV_STOCKOUT_RATE",
        "INV_ACTIVE_SKUS",
        "INV_DEAD_STOCK_VAL",
    ],
    "MANUFACTURING": [
        "MFG_FIRST_PASS_YIELD",
        "MFG_ACTIVE_ORDERS",
        "MFG_SCRAP_RATE",
        "MFG_TOTAL_OUTPUT",
    ],
    "MFG": [
        "MFG_FIRST_PASS_YIELD",
        "MFG_ACTIVE_ORDERS",
        "MFG_SCRAP_RATE",
        "MFG_TOTAL_OUTPUT",
    ],
    "HR": [
        "HR_TOTAL_HEADCOUNT",
        "HR_MONTHLY_TURNOVER",
        "HR_ACTIVE_DEPARTMENTS",
        "HR_PAYROLL_RUN_TOTAL",
    ],
}


@router.post(
    "/summary/executive",
    response_model=ExecutiveSummaryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_DASHBOARDS_READ.value))],
)
async def get_executive_summary(
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveSummaryResponse:
    """Fetches core cross-domain executive KPIs with period-over-period delta tracking."""
    service = KPIService(db)
    codes = DOMAIN_SUMMARY_KPI_MAP["EXECUTIVE"]
    cards: list[MetricCardData] = []
    for c in codes:
        card = await service.calculate_kpi(tenant_id, org_id, c, params)
        cards.append(card)

    _, _, _, _, label = service.resolve_date_range(params)
    return ExecutiveSummaryResponse(kpis=cards, period_label=label)


@router.post(
    "/summary/{domain}",
    response_model=ExecutiveSummaryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_DASHBOARDS_READ.value))],
)
async def get_domain_summary(
    domain: str,
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveSummaryResponse:
    """Fetches domain-specific KPIs with period-over-period delta tracking."""
    service = KPIService(db)
    dom_key = domain.upper()
    codes = DOMAIN_SUMMARY_KPI_MAP.get(dom_key, DOMAIN_SUMMARY_KPI_MAP["EXECUTIVE"])
    cards: list[MetricCardData] = []
    for c in codes:
        card = await service.calculate_kpi(tenant_id, org_id, c, params)
        cards.append(card)

    _, _, _, _, label = service.resolve_date_range(params)
    return ExecutiveSummaryResponse(kpis=cards, period_label=label)
