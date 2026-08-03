import uuid
from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


# --- Attendance Record Schemas ---
class CheckInRequest(BaseModel):
    employee_id: uuid.UUID
    attendance_source: str = "Web"  # Manual, Web, Mobile, Biometric, Face Recognition, API
    latitude: float | None = None
    longitude: float | None = None
    remarks: str | None = None


class CheckOutRequest(BaseModel):
    attendance_record_id: uuid.UUID | None = None
    attendance_id: uuid.UUID | None = None  # Alias
    employee_id: uuid.UUID | None = None
    remarks: str | None = None


class AttendanceRecordUpdate(BaseModel):
    check_in: datetime | None = None
    check_out: datetime | None = None
    worked_hours: float | None = None
    late_minutes: int | None = None
    early_exit_minutes: int | None = None
    status: str | None = None
    remarks: str | None = None


class AttendanceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    attendance_date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    worked_hours: float
    late_minutes: int
    early_exit_minutes: int
    status: str
    attendance_source: str
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Shift Schemas ---
class ShiftCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    start_time: str = Field(..., description="HH:MM format, e.g. 09:00")
    end_time: str = Field(..., description="HH:MM format, e.g. 17:00")
    grace_time_minutes: int = 15
    break_duration_minutes: int = 60
    is_night_shift: bool = False
    status: str = "active"


class ShiftUpdate(BaseModel):
    name: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    grace_time_minutes: int | None = None
    break_duration_minutes: int | None = None
    is_night_shift: bool | None = None
    status: str | None = None


class ShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    start_time: str
    end_time: str
    grace_time_minutes: int
    break_duration_minutes: int
    is_night_shift: bool
    status: str
    created_at: datetime
    updated_at: datetime


# --- Employee Shift Assignment Schemas ---
class EmployeeShiftAssignmentCreate(BaseModel):
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    status: str = "active"


class EmployeeShiftAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# --- Attendance Correction Schemas ---
class AttendanceCorrectionCreate(BaseModel):
    attendance_record_id: uuid.UUID
    requested_by: uuid.UUID | None = None
    reason: str = Field(..., max_length=500)
    old_check_in: datetime | None = None
    old_check_out: datetime | None = None
    new_check_in: datetime
    new_check_out: datetime


class AttendanceCorrectionApproveRequest(BaseModel):
    status: Literal["Approved", "Rejected"]
    approved_by: uuid.UUID | None = None


class AttendanceCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    attendance_record_id: uuid.UUID
    requested_by: uuid.UUID | None = None
    reason: str
    old_check_in: datetime | None = None
    old_check_out: datetime | None = None
    new_check_in: datetime
    new_check_out: datetime
    status: str
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# --- Overtime Record Schemas ---
class OvertimeRecordCreate(BaseModel):
    employee_id: uuid.UUID
    attendance_record_id: uuid.UUID | None = None
    hours: float
    reason: str = Field(..., max_length=500)


class OvertimeApproveRequest(BaseModel):
    approved: bool = True
    approved_by: uuid.UUID | None = None


class OvertimeRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    attendance_record_id: uuid.UUID | None = None
    hours: float
    reason: str
    approved: bool
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# --- Work Schedule Schemas ---
class WorkScheduleCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    description: str | None = None
    weekly_pattern: dict[str, Any]
    status: str = "active"


class WorkScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    weekly_pattern: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


# --- Employee Work Schedule Schemas ---
class EmployeeWorkScheduleCreate(BaseModel):
    employee_id: uuid.UUID
    work_schedule_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None


class EmployeeWorkScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    work_schedule_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    created_at: datetime
    updated_at: datetime


# --- Break Record Schemas ---
class BreakRecordCreate(BaseModel):
    attendance_record_id: uuid.UUID
    break_start: datetime
    break_end: datetime | None = None
    duration_minutes: int = 0


class BreakRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    attendance_record_id: uuid.UUID
    break_start: datetime
    break_end: datetime | None = None
    duration_minutes: int
    created_at: datetime
    updated_at: datetime


# --- Attendance Device Schemas ---
class AttendanceDeviceCreate(BaseModel):
    organization_id: uuid.UUID
    device_name: str = Field(..., max_length=100)
    device_type: str = Field(..., description="Biometric, RFID, Face, QR")
    serial_number: str = Field(..., max_length=100)
    location: str | None = None
    status: str = "active"


class AttendanceDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    device_name: str
    device_type: str
    serial_number: str
    location: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# --- Attendance Sync Log Schemas ---
class AttendanceSyncLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_id: uuid.UUID
    sync_time: datetime
    records_processed: int
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Dashboard Analytics & Summary ---
class AttendanceDashboardSummary(BaseModel):
    total_employees: int
    present_today: int
    absent_today: int
    late_today: int
    overtime_today: float
    on_duty_today: int
    attendance_rate: float
    recent_punches: list[AttendanceRecordResponse]


# Backward compatibility aliases
WorkShiftCreate = ShiftCreate
WorkShiftResponse = ShiftResponse
OvertimeRequestCreate = OvertimeRecordCreate
OvertimeRequestResponse = OvertimeRecordResponse
BiometricLogResponse = AttendanceSyncLogResponse
