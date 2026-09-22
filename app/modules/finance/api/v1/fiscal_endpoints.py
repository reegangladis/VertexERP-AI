"""Fiscal Year & Period API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.models.fiscal import FiscalPeriod, FiscalYear
from app.modules.finance.repositories.fiscal_repository import FiscalRepository
from app.modules.finance.schemas.fiscal import (
    FiscalPeriodListResponse,
    FiscalPeriodResponse,
    FiscalYearCreate,
    FiscalYearListResponse,
    FiscalYearResponse,
)
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/fiscal", tags=["Finance - Fiscal Periods & Years"])


@router.get(
    "/years",
    response_model=FiscalYearListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_READ.value))],
)
async def list_fiscal_years(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> FiscalYearListResponse:
    repo = FiscalRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_years_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_years_by_org(tenant_id, org_id)
    return FiscalYearListResponse(
        items=[FiscalYearResponse.model_validate(y) for y in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/years",
    response_model=FiscalYearResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_MANAGE.value))],
)
async def create_fiscal_year(
    data: FiscalYearCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> FiscalYearResponse:
    repo = FiscalRepository(db)
    fy = FiscalYear(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        is_closed=data.is_closed,
    )

    for p in data.periods:
        period = FiscalPeriod(
            tenant_id=tenant_id,
            organization_id=org_id,
            period_number=p.period_number,
            period_name=p.period_name,
            start_date=p.start_date,
            end_date=p.end_date,
            is_locked=p.is_locked,
            is_closed=p.is_closed,
        )
        fy.periods.append(period)

    await repo.create_year(fy)
    await db.commit()
    fresh_fy = await repo.get_year_by_id(fy.id, tenant_id, org_id)
    return FiscalYearResponse.model_validate(fresh_fy)


@router.get(
    "/periods",
    response_model=FiscalPeriodListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_READ.value))],
)
@router.get(
    "/periods/",
    response_model=FiscalPeriodListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_READ.value))],
)
async def list_fiscal_periods(
    fiscal_year_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> FiscalPeriodListResponse:
    repo = FiscalRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_periods_by_org(
        tenant_id, org_id, fiscal_year_id=fiscal_year_id, offset=offset, limit=page_size
    )
    total = await repo.count_periods_by_org(tenant_id, org_id, fiscal_year_id=fiscal_year_id)
    return FiscalPeriodListResponse(
        items=[FiscalPeriodResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )



@router.post(
    "/periods/{period_id}/lock",
    response_model=FiscalPeriodResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_LOCK.value))],
)
async def lock_fiscal_period(
    period_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> FiscalPeriodResponse:
    repo = FiscalRepository(db)
    period = await repo.get_period_by_id(period_id, tenant_id, org_id)
    if not period:
        raise NotFoundException(f"Fiscal Period {period_id} not found.")

    period.is_locked = True
    await db.commit()
    return FiscalPeriodResponse.model_validate(period)


@router.post(
    "/periods/{period_id}/unlock",
    response_model=FiscalPeriodResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PERIODS_LOCK.value))],
)
async def unlock_fiscal_period(
    period_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> FiscalPeriodResponse:
    repo = FiscalRepository(db)
    period = await repo.get_period_by_id(period_id, tenant_id, org_id)
    if not period:
        raise NotFoundException(f"Fiscal Period {period_id} not found.")

    period.is_locked = False
    await db.commit()
    return FiscalPeriodResponse.model_validate(period)
