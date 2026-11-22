"""Sales Invoice (AR) API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.repositories.invoice_repository import InvoiceRepository
from app.modules.finance.schemas.invoice import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
)
from app.modules.finance.services.invoice_service import InvoiceService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/invoices", tags=["Finance - Accounts Receivable (Invoices)"])


@router.get(
    "/",
    response_model=InvoiceListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
async def list_invoices(
    customer_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> InvoiceListResponse:
    repo = InvoiceRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        customer_id=customer_id,
        status=status_filter,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(
        tenant_id, org_id, customer_id=customer_id, status=status_filter
    )
    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_WRITE.value))],
)
async def create_invoice(
    data: InvoiceCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    inv = await service.create_invoice(data, tenant_id, org_id)
    return InvoiceResponse.model_validate(inv)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
async def get_invoice(
    invoice_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    repo = InvoiceRepository(db)
    inv = await repo.get_by_id(invoice_id, tenant_id, org_id)
    if not inv:
        raise NotFoundException(f"Invoice {invoice_id} not found.")
    return InvoiceResponse.model_validate(inv)


@router.post(
    "/{invoice_id}/post",
    response_model=InvoiceResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_POST.value))],
)
async def post_invoice(
    invoice_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    posted_inv = await service.post_invoice(invoice_id, tenant_id, org_id, user_id=user_id)
    return InvoiceResponse.model_validate(posted_inv)
