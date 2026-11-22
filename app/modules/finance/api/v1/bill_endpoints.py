"""Vendor Bill (AP) API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.repositories.bill_repository import BillRepository
from app.modules.finance.schemas.bill import BillCreate, BillListResponse, BillResponse
from app.modules.finance.services.bill_service import BillService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/bills", tags=["Finance - Accounts Payable (Bills)"])


@router.get(
    "/",
    response_model=BillListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
async def list_bills(
    vendor_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BillListResponse:
    repo = BillRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, vendor_id=vendor_id, status=status_filter, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, vendor_id=vendor_id, status=status_filter)
    return BillListResponse(
        items=[BillResponse.model_validate(b) for b in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=BillResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_WRITE.value))],
)
async def create_bill(
    data: BillCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BillResponse:
    service = BillService(db)
    bill = await service.create_bill(data, tenant_id, org_id)
    return BillResponse.model_validate(bill)


@router.get(
    "/{bill_id}",
    response_model=BillResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
async def get_bill(
    bill_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BillResponse:
    repo = BillRepository(db)
    bill = await repo.get_by_id(bill_id, tenant_id, org_id)
    if not bill:
        raise NotFoundException(f"Bill {bill_id} not found.")
    return BillResponse.model_validate(bill)


@router.post(
    "/{bill_id}/post",
    response_model=BillResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_POST.value))],
)
async def post_bill(
    bill_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> BillResponse:
    service = BillService(db)
    posted_bill = await service.post_bill(bill_id, tenant_id, org_id, user_id=user_id)
    return BillResponse.model_validate(posted_bill)
