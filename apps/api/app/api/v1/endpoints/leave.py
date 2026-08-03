import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.schemas.leave import (
    CompOffCreate,
    CompOffResponse,
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    HolidayEventCreate,
    HolidayEventResponse,
    LeaveBalanceResponse,
    LeaveBalanceUpdate,
    LeaveDashboardSummary,
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeavePolicyUpdate,
    LeaveApprovalRequest,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeaveTypeUpdate,
)
from app.services.leave import LeaveService

router = APIRouter()


def get_leave_service(db: AsyncSession = Depends(get_db_session)) -> LeaveService:
    return LeaveService(db)


# --- Leave Types ---
@router.post("/leave-types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    payload: LeaveTypeCreate,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.create_leave_type(payload)


@router.get("/leave-types", response_model=list[LeaveTypeResponse])
async def list_leave_types(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_leave_types(org_id)


@router.get("/leave-types/{id}", response_model=LeaveTypeResponse)
async def get_leave_type(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.get_leave_type(id)


@router.patch("/leave-types/{id}", response_model=LeaveTypeResponse)
async def update_leave_type(
    id: uuid.UUID,
    payload: LeaveTypeUpdate,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.update_leave_type(id, payload)


@router.delete("/leave-types/{id}", response_model=LeaveTypeResponse)
async def delete_leave_type(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.delete_leave_type(id)


# --- Leave Policies ---
@router.post("/leave-policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_policy(
    payload: LeavePolicyCreate,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.create_policy(payload)


@router.get("/leave-policies", response_model=list[LeavePolicyResponse])
async def list_leave_policies(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_policies(org_id)


@router.get("/leave-policies/{id}", response_model=LeavePolicyResponse)
async def get_leave_policy(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.get_policy(id)


@router.patch("/leave-policies/{id}", response_model=LeavePolicyResponse)
async def update_leave_policy(
    id: uuid.UUID,
    payload: LeavePolicyUpdate,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.update_policy(id, payload)


@router.delete("/leave-policies/{id}", response_model=LeavePolicyResponse)
async def delete_leave_policy(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("policy.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.delete_policy(id)


# --- Leave Balances ---
@router.get("/leave-balances", response_model=list[LeaveBalanceResponse])
async def list_leave_balances(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_balances(employee_id)


@router.put("/leave-balances/{id}", response_model=LeaveBalanceResponse)
async def update_leave_balance(
    id: uuid.UUID,
    payload: LeaveBalanceUpdate,
    current_user: User = Depends(PermissionChecker("leave.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.update_balance(id, payload)


# --- Leave Requests ---
@router.post("/leave-requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def apply_leave(
    payload: LeaveRequestCreate,
    current_user: User = Depends(PermissionChecker("leave.apply")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.apply_leave(payload)


@router.get("/leave-requests", response_model=list[LeaveRequestResponse])
async def list_leave_requests(
    employee_id: uuid.UUID | None = Query(None),
    leave_status: str | None = Query(None),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_requests(employee_id=employee_id, status_filter=leave_status)


@router.post("/leave-requests/{id}/approve", response_model=LeaveRequestResponse)
async def approve_leave(
    id: uuid.UUID,
    payload: LeaveApprovalRequest,
    current_user: User = Depends(PermissionChecker("leave.approve")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.approve_leave(id, payload)


@router.post("/leave-requests/{id}/reject", response_model=LeaveRequestResponse)
async def reject_leave(
    id: uuid.UUID,
    payload: LeaveApprovalRequest,
    current_user: User = Depends(PermissionChecker("leave.reject")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.reject_leave(id, payload)


@router.post("/leave-requests/{id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("leave.apply")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.cancel_leave(id)


# --- Comp-Off ---
@router.post("/comp-offs", response_model=CompOffResponse, status_code=status.HTTP_201_CREATED)
async def create_compoff(
    payload: CompOffCreate,
    current_user: User = Depends(PermissionChecker("leave.apply")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.create_compoff(payload)


@router.get("/comp-offs", response_model=list[CompOffResponse])
async def list_compoffs(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_compoffs(employee_id)


@router.delete("/comp-offs/{id}", response_model=CompOffResponse)
async def delete_compoff(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("leave.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.delete_compoff(id)


# --- Holiday Calendars & Events ---
@router.post("/holiday-calendars", response_model=HolidayCalendarResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar(
    payload: HolidayCalendarCreate,
    current_user: User = Depends(PermissionChecker("holiday.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.create_calendar(payload)


@router.get("/holiday-calendars", response_model=list[HolidayCalendarResponse])
async def list_calendars(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_calendars(org_id)


@router.post("/holiday-events", response_model=HolidayEventResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday_event(
    payload: HolidayEventCreate,
    current_user: User = Depends(PermissionChecker("holiday.manage")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.create_holiday_event(payload)


@router.get("/holiday-events", response_model=list[HolidayEventResponse])
async def list_holiday_events(
    calendar_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.list_holiday_events(calendar_id)


# --- Dashboard Summary ---
@router.get("/leave-dashboard-summary", response_model=LeaveDashboardSummary)
async def get_dashboard_summary(
    org_id: uuid.UUID = Query(...),
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("leave.read")),
    service: LeaveService = Depends(get_leave_service),
):
    return await service.get_dashboard_summary(org_id, employee_id)
