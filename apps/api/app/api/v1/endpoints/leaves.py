import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db_session
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.user import User
from app.repositories.hr_mgmt import (
    LeaveBalanceRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
)
from app.schemas.hr_mgmt import (
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestUpdate,
    LeaveTypeCreate,
    LeaveTypeResponse,
)
from app.schemas.response import APIResponse
from app.services.hr_mgmt import LeaveService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_leave_service(db=Depends(get_db_session)):
    return LeaveService(
        LeaveRequestRepository(db), LeaveBalanceRepository(db), LeaveTypeRepository(db)
    )


# 1. Leave Types Endpoints
@router.get("/types", response_model=APIResponse[list[LeaveTypeResponse]])
async def list_leave_types(
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    types = await service.type_repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Leave types retrieved successfully",
        data=types,
    )


@router.post("/types", response_model=APIResponse[LeaveTypeResponse])
async def create_leave_type(
    payload: LeaveTypeCreate,
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    ltype = await service.type_repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Leave type created successfully",
        data=ltype,
    )


# 2. Leave Request Endpoints
@router.get("/requests", response_model=APIResponse[list[LeaveRequestResponse]])
async def list_leave_requests(
    employee_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    stmt = select(LeaveRequest).where(LeaveRequest.is_deleted == False)
    if employee_id:
        stmt = stmt.where(LeaveRequest.employee_id == employee_id)
    res = await service.repository.db.execute(stmt)
    reqs = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Leave requests retrieved successfully",
        data=reqs,
    )


@router.post("/requests", response_model=APIResponse[LeaveRequestResponse])
async def submit_leave_request(
    payload: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        req = await service.submit_request(current_user.organization_id, payload.dict())
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Leave request submitted successfully",
            data=req,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/requests/{id}/approval", response_model=APIResponse[LeaveRequestResponse])
async def approve_leave_request(
    id: uuid.UUID,
    payload: LeaveRequestUpdate,
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    # Retrieve mock employee id for current_user if applicable (simplification for testing)
    mock_approver_id = current_user.id
    try:
        req = await service.process_approval(
            id, mock_approver_id, payload.status, payload.approval_comment
        )
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Leave request updated to status: {payload.status}",
            data=req,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# 3. Leave Balances Endpoints
@router.get("/balances", response_model=APIResponse[list[LeaveBalanceResponse]])
async def list_leave_balances(
    employee_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: LeaveService = Depends(get_leave_service),
):
    stmt = select(LeaveBalance).where(LeaveBalance.is_deleted == False)
    if employee_id:
        stmt = stmt.where(LeaveBalance.employee_id == employee_id)
    res = await service.balance_repo.db.execute(stmt)
    balances = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Leave balances retrieved successfully",
        data=balances,
    )
