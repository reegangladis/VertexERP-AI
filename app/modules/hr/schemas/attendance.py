"""Shifts and Attendance schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Shifts
# --------------------------------------------------------------------------
class ShiftCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    start_time: str = Field(..., min_length=5, max_length=8)  # "09:00:00"
    end_time: str = Field(..., min_length=5, max_length=8)  # "17:00:00"
    break_duration_minutes: int = Field(60, ge=0)
    grace_period_minutes: int = Field(15, ge=0)
    is_night_shift: bool = False
    is_active: bool = True


class ShiftUpdate(BaseModel):
    name: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    break_duration_minutes: int | None = None
    grace_period_minutes: int | None = None
    is_night_shift: bool | None = None
    is_active: bool | None = None


class ShiftResponse(ShiftCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Shift Assignment
# --------------------------------------------------------------------------
class ShiftAssignmentCreate(BaseModel):
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    start_date: date
    end_date: date | None = None
    is_active: bool = True


class ShiftAssignmentResponse(ShiftAssignmentCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Attendance Records & Clock In / Out
# --------------------------------------------------------------------------
class AttendanceClockIn(BaseModel):
    employee_id: uuid.UUID
    work_date: date = Field(default_factory=date.today)
    check_in_time: datetime = Field(default_factory=datetime.utcnow)
    check_in_ip: str | None = None
    check_in_latitude: float | None = None
    check_in_longitude: float | None = None
    verification_method: str = "WEB"


class AttendanceClockOut(BaseModel):
    employee_id: uuid.UUID
    work_date: date = Field(default_factory=date.today)
    check_out_time: datetime = Field(default_factory=datetime.utcnow)
    check_out_ip: str | None = None
    check_out_latitude: float | None = None
    check_out_longitude: float | None = None


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    shift_id: uuid.UUID | None = None
    work_date: date
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    check_in_ip: str | None = None
    check_out_ip: str | None = None
    check_in_latitude: float | None = None
    check_in_longitude: float | None = None
    check_out_latitude: float | None = None
    check_out_longitude: float | None = None
    status: str
    regular_hours: float
    overtime_hours: float
    verification_method: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Regularization
# --------------------------------------------------------------------------
class RegularizationCreate(BaseModel):
    attendance_record_id: uuid.UUID
    employee_id: uuid.UUID
    requested_check_in: datetime | None = None
    requested_check_out: datetime | None = None
    reason: str = Field(..., min_length=5)


class RegularizationReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    remarks: str | None = None


class RegularizationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    attendance_record_id: uuid.UUID
    employee_id: uuid.UUID
    requested_check_in: datetime | None = None
    requested_check_out: datetime | None = None
    reason: str
    status: str
    approver_id: uuid.UUID | None = None
    approved_at: datetime | None = None
    remarks: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
