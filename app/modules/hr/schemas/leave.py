"""Leave Management, Policies, Balances, and Requests schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Leave Types
# --------------------------------------------------------------------------
class LeaveTypeCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    is_paid: bool = True
    is_encashable: bool = False
    max_consecutive_days: int = Field(30, ge=1)
    color_code: str = Field("#3B82F6", max_length=16)
    is_active: bool = True


class LeaveTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_paid: bool | None = None
    is_encashable: bool | None = None
    max_consecutive_days: int | None = None
    color_code: str | None = None
    is_active: bool | None = None


class LeaveTypeResponse(LeaveTypeCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Leave Policy
# --------------------------------------------------------------------------
class LeavePolicyCreate(BaseModel):
    leave_type_id: uuid.UUID
    annual_allocation_days: float = Field(12.0, ge=0.0)
    accrual_frequency: str = Field("ANNUAL", max_length=32)
    carry_forward_max_days: float = Field(0.0, ge=0.0)
    probation_allowed: bool = False
    is_active: bool = True


class LeavePolicyResponse(LeavePolicyCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Leave Balance
# --------------------------------------------------------------------------
class LeaveBalanceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    fiscal_year: int
    allocated_days: float
    used_days: float
    pending_days: float
    carry_forward_days: float
    balance_days: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Leave Request & Approval
# --------------------------------------------------------------------------
class LeaveRequestCreate(BaseModel):
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    total_days: float = Field(..., gt=0.0)
    reason: str = Field(..., min_length=3)


class LeaveApprovalRequest(BaseModel):
    status: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    remarks: str | None = None


class LeaveRequestResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: str
    approver_id: uuid.UUID | None = None
    approved_at: datetime | None = None
    remarks: str | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
