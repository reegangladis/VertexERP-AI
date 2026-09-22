"""Payment API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.repositories.payment_repository import PaymentRepository
from app.modules.finance.schemas.payment import (
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
)
from app.modules.finance.services.payment_service import PaymentService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/payments", tags=["Finance - Payments & Allocations"])


@router.get(
    "/",
    response_model=PaymentListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PAYMENTS_READ.value))],
)
async def list_payments(
    payment_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PaymentListResponse:
    repo = PaymentRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        payment_type=payment_type,
        status=status_filter,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(
        tenant_id, org_id, payment_type=payment_type, status=status_filter
    )
    return PaymentListResponse(
        items=[PaymentResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PAYMENTS_WRITE.value))],
)
async def create_payment(
    payload: PaymentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    service = PaymentService(db)
    payment = await service.create_payment(payload, tenant_id, org_id)
    return PaymentResponse.model_validate(payment)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PAYMENTS_READ.value))],
)
async def get_payment(
    payment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    repo = PaymentRepository(db)
    payment = await repo.get_by_id(payment_id, tenant_id, org_id)
    if not payment:
        raise NotFoundException(f"Payment {payment_id} not found.")
    return PaymentResponse.model_validate(payment)


@router.post(
    "/{payment_id}/post",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_PAYMENTS_POST.value))],
)
async def post_payment(
    payment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    service = PaymentService(db)
    payment = await service.post_payment(payment_id, tenant_id, org_id, user_id=user_id)
    return PaymentResponse.model_validate(payment)
