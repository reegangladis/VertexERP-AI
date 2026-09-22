"""Leave Management, Policies, Balances, and Requests API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.leave import (
    LeaveApprovalRequest,
    LeaveBalanceResponse,
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
)
from app.modules.hr.services.leave_service import LeaveService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/leaves", tags=["HR Leave Management"])


# --------------------------------------------------------------------------
# Leave Types
# --------------------------------------------------------------------------
@router.post(
    "/types",
    response_model=LeaveTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Leave Type",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_WRITE.value))],
)
async def create_leave_type(
    req: LeaveTypeCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaveTypeResponse:
    """Creates a new leave category."""
    service = LeaveService(db)
    lt = await service.create_type(tenant_id, org_id, req)
    return LeaveTypeResponse.model_validate(lt)


@router.get(
    "/types",
    response_model=list[LeaveTypeResponse],
    status_code=status.HTTP_200_OK,
    summary="List Leave Types",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_READ.value))],
)
async def list_leave_types(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveTypeResponse]:
    """Lists leave types."""
    service = LeaveService(db)
    types = await service.list_types(tenant_id, org_id, is_active)
    return [LeaveTypeResponse.model_validate(t) for t in types]


# --------------------------------------------------------------------------
# Policies
# --------------------------------------------------------------------------
@router.post(
    "/policies",
    response_model=LeavePolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Leave Policy",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_WRITE.value))],
)
async def create_leave_policy(
    req: LeavePolicyCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeavePolicyResponse:
    """Configures accrual and allocation rules for a leave type."""
    service = LeaveService(db)
    policy = await service.create_policy(tenant_id, org_id, req)
    return LeavePolicyResponse.model_validate(policy)


# --------------------------------------------------------------------------
# Balances
# --------------------------------------------------------------------------
@router.get(
    "/balances/{employee_id}",
    response_model=list[LeaveBalanceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Employee Leave Balances",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_READ.value))],
)
async def get_leave_balances(
    employee_id: uuid.UUID,
    fiscal_year: int = Query(2024),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveBalanceResponse]:
    """Retrieves real-time leave quota and balances."""
    service = LeaveService(db)
    balances = await service.list_balances(employee_id, fiscal_year, tenant_id, org_id)
    return [LeaveBalanceResponse.model_validate(b) for b in balances]


# --------------------------------------------------------------------------
# Requests & Approvals
# --------------------------------------------------------------------------
@router.post(
    "/requests",
    response_model=LeaveRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply for Leave",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_WRITE.value))],
)
async def apply_for_leave(
    req: LeaveRequestCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaveRequestResponse:
    """Submits a leave application."""
    service = LeaveService(db)
    leave_req = await service.submit_request(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_LEAVE_APPLIED",
        description=f"Leave request ({leave_req.total_days} days) submitted for employee '{leave_req.employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return LeaveRequestResponse.model_validate(leave_req)


@router.put(
    "/requests/{request_id}/review",
    response_model=LeaveRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve or Reject Leave Request",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_APPROVE.value))],
)
async def review_leave_request(
    request_id: uuid.UUID,
    req: LeaveApprovalRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaveRequestResponse:
    """Manager approval or rejection of leave application."""
    service = LeaveService(db)
    reviewed = await service.review_request(request_id, tenant_id, org_id, current_user.id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_LEAVE_REVIEWED",
        description=f"Leave request '{request_id}' set to '{reviewed.status}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return LeaveRequestResponse.model_validate(reviewed)


@router.get(
    "/requests",
    response_model=list[LeaveRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="List Leave Requests",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEAVES_READ.value))],
)
async def list_leave_requests(
    employee_id: uuid.UUID | None = None,
    status: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveRequestResponse]:
    """Lists leave requests with filtering."""
    service = LeaveService(db)
    requests = await service.list_requests(tenant_id, org_id, employee_id, status)
    return [LeaveRequestResponse.model_validate(r) for r in requests]
