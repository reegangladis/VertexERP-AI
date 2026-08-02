import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db_session
from app.models.attendance import Attendance
from app.models.user import User
from app.repositories.hr_mgmt import AttendanceRepository
from app.schemas.hr_mgmt import AttendanceResponse, CheckInRequest, CheckOutRequest
from app.schemas.response import APIResponse
from app.services.hr_mgmt import AttendanceService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_attendance_service(db=Depends(get_db_session)):
    return AttendanceService(AttendanceRepository(db))


@router.get("", response_model=APIResponse[list[AttendanceResponse]])
async def list_attendance(
    skip: int = 0,
    limit: int = 100,
    employee_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    stmt = select(Attendance).where(Attendance.is_deleted == False)
    if employee_id:
        stmt = stmt.where(Attendance.employee_id == employee_id)

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    records = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Attendance records retrieved successfully",
        data=records,
    )


@router.post("/check-in", response_model=APIResponse[AttendanceResponse])
async def check_in(
    payload: CheckInRequest,
    current_user: User = Depends(get_current_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    try:
        check_in_time = payload.check_in_time or datetime.now()
        record = await service.check_in(payload.employee_id, check_in_time)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Checked in successfully",
            data=record,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/check-out", response_model=APIResponse[AttendanceResponse])
async def check_out(
    payload: CheckOutRequest,
    current_user: User = Depends(get_current_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    try:
        check_out_time = payload.check_out_time or datetime.now()
        record = await service.check_out(payload.employee_id, check_out_time)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Checked out successfully",
            data=record,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
