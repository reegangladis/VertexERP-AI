import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


# --- Leave Type Schemas ---
class LeaveTypeCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: str | None = None
    color: str = "#3B82F6"
    is_paid: bool = True
    allow_half_day: bool = True
    requires_approval: bool = True
    allow_negative_balance: bool = False
    max_days_per_year: float = 20.0
    carry_forward: bool = False
    carry_forward_limit: float = 0.0
    status: str = "active"


class LeaveTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    is_paid: bool | None = None
    allow_half_day: bool | None = None
    requires_approval: bool | None = None
    allow_negative_balance: bool | None = None
    max_days_per_year: float | None = None
    carry_forward: bool | None = None
    carry_forward_limit: float | None = None
    status: str | None = None


class LeaveTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    color: str
    is_paid: bool
    allow_half_day: bool
    requires_approval: bool
    allow_negative_balance: bool
    max_days_per_year: float
    carry_forward: bool
    carry_forward_limit: float
    status: str
    created_at: datetime
    updated_at: datetime


# --- Leave Policy & Assignment Schemas ---
class LeavePolicyCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    description: str | None = None
    effective_from: date
    effective_to: date | None = None
    accrual_method: str = "annual"  # annual, monthly, quarterly
    approval_levels: int = 1
    status: str = "active"


class LeavePolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    accrual_method: str | None = None
    approval_levels: int | None = None
    status: str | None = None


class LeavePolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    effective_from: date
    effective_to: date | None = None
    accrual_method: str
    approval_levels: int
    status: str
    created_at: datetime
    updated_at: datetime


class LeavePolicyAssignmentCreate(BaseModel):
    policy_id: uuid.UUID
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    employment_type: str | None = None
    effective_from: date


class LeavePolicyAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    policy_id: uuid.UUID
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    employment_type: str | None = None
    effective_from: date
    created_at: datetime
    updated_at: datetime


# --- Leave Balance Schemas ---
class LeaveBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    available_days: float
    used_days: float
    pending_days: float
    carry_forward_days: float
    accrued_days: float
    last_updated: datetime
    created_at: datetime
    updated_at: datetime


class LeaveBalanceUpdate(BaseModel):
    available_days: float | None = None
    carry_forward_days: float | None = None
    accrued_days: float | None = None


# --- Leave Request & Approval Schemas ---
class LeaveRequestCreate(BaseModel):
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    is_half_day: bool = False
    half_day_session: str | None = None  # morning, afternoon
    reason: str = Field(..., max_length=500)
    attachment_url: str | None = None


class LeaveApprovalRequest(BaseModel):
    approver_id: uuid.UUID
    decision: Literal["Approved", "Rejected"]
    remarks: str | None = None


class LeaveApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    leave_request_id: uuid.UUID
    approver_id: uuid.UUID
    approval_level: int
    decision: str
    remarks: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class LeaveRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    number_of_days: float
    is_half_day: bool
    half_day_session: str | None = None
    reason: str
    attachment_url: str | None = None
    status: str
    applied_at: datetime
    approved_at: datetime | None = None
    cancelled_at: datetime | None = None
    approvals: list[LeaveApprovalResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Leave Accrual & Comp-Off Schemas ---
class LeaveAccrualResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    accrual_date: date
    days_added: float
    reason: str
    created_at: datetime
    updated_at: datetime


class CompOffCreate(BaseModel):
    employee_id: uuid.UUID
    attendance_record_id: uuid.UUID | None = None
    attendance_id: uuid.UUID | None = None  # Alias
    earned_date: date
    expiry_date: date
    days: float = 1.0


class CompOffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    attendance_record_id: uuid.UUID | None = None
    earned_date: date
    expiry_date: date
    days: float
    status: str
    created_at: datetime
    updated_at: datetime


# --- Holiday Calendar & Event Schemas ---
class HolidayCalendarCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    state: str | None = None
    year: int


class HolidayCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    country: str
    state: str | None = None
    year: int
    created_at: datetime
    updated_at: datetime


class HolidayEventCreate(BaseModel):
    calendar_id: uuid.UUID
    holiday_date: date
    holiday_name: str = Field(..., max_length=100)
    holiday_type: str = "national"
    is_optional: bool = False


class HolidayEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    calendar_id: uuid.UUID
    holiday_date: date
    holiday_name: str
    holiday_type: str
    is_optional: bool
    created_at: datetime
    updated_at: datetime


# --- Dashboard Summary Schema ---
class LeaveDashboardSummary(BaseModel):
    total_balances: list[LeaveBalanceResponse]
    pending_requests_count: int
    approved_leaves_count: int
    rejected_leaves_count: int
    upcoming_holidays: list[HolidayEventResponse]
    team_leave_today_count: int
    comp_off_available_days: float


# Backward compatibility aliases
LeaveRequestApply = LeaveRequestCreate
LeaveRequestAction = LeaveApprovalRequest
