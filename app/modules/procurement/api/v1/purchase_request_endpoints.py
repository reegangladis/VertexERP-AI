"""Purchase Requests API Endpoints."""

import uuid

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.procurement.repositories.purchase_request_repository import (
    PurchaseRequestRepository,
)
from app.modules.procurement.schemas.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestListResponse,
    PurchaseRequestReject,
    PurchaseRequestResponse,
)
from app.modules.procurement.services.procurement_service import ProcurementService

router = APIRouter(tags=["Procurement - Purchase Requests"])


@router.get(
    "/procurement/purchase-requests",
    response_model=PurchaseRequestListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
@router.get(
    "/procurement/purchase-requests/",
    response_model=PurchaseRequestListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
@router.get(
    "/procurement/requests",
    response_model=PurchaseRequestListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
@router.get(
    "/procurement/requests/",
    response_model=PurchaseRequestListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
async def list_purchase_requests(
    status_filter: str | None = Query(None, alias="status"),
    requester_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestListResponse:
    repo = PurchaseRequestRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        status=status_filter,
        requester_id=requester_id,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return PurchaseRequestListResponse(
        items=[PurchaseRequestResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/procurement/purchase-requests",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
@router.post(
    "/procurement/purchase-requests/",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
@router.post(
    "/procurement/requests",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
@router.post(
    "/procurement/requests/",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
async def create_purchase_request(
    data: PurchaseRequestCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestResponse:
    service = ProcurementService(db)
    pr = await service.create_purchase_request(
        tenant_id, org_id, data, requester_id=current_user.id
    )
    return PurchaseRequestResponse.model_validate(pr)


@router.get(
    "/procurement/purchase-requests/{request_id}",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
@router.get(
    "/procurement/requests/{request_id}",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_READ.value))],
)
async def get_purchase_request(
    request_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestResponse:
    repo = PurchaseRequestRepository(db)
    pr = await repo.get_by_id(request_id, tenant_id, org_id)
    if not pr:
        raise NotFoundException(f"Purchase Request {request_id} not found.")
    return PurchaseRequestResponse.model_validate(pr)


@router.post(
    "/procurement/purchase-requests/{request_id}/submit",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
@router.post(
    "/procurement/requests/{request_id}/submit",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_WRITE.value))],
)
async def submit_purchase_request(
    request_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestResponse:
    service = ProcurementService(db)
    pr = await service.submit_purchase_request(request_id, tenant_id, org_id)
    return PurchaseRequestResponse.model_validate(pr)


@router.post(
    "/procurement/purchase-requests/{request_id}/approve",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_APPROVE.value))],
)
@router.post(
    "/procurement/requests/{request_id}/approve",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_APPROVE.value))],
)
async def approve_purchase_request(
    request_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestResponse:
    service = ProcurementService(db)
    pr = await service.approve_purchase_request(request_id, tenant_id, org_id)
    return PurchaseRequestResponse.model_validate(pr)


@router.post(
    "/procurement/purchase-requests/{request_id}/reject",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_APPROVE.value))],
)
@router.post(
    "/procurement/requests/{request_id}/reject",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_REQUESTS_APPROVE.value))],
)
async def reject_purchase_request(
    request_id: uuid.UUID,
    data: PurchaseRequestReject | None = Body(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestResponse:
    service = ProcurementService(db)
    reason = data.reason if data and data.reason else ""
    pr = await service.reject_purchase_request(request_id, tenant_id, org_id, reason=reason)
    return PurchaseRequestResponse.model_validate(pr)
