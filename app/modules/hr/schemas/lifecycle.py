"""Employment Lifecycle, Contracts, and Onboarding schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Employment Contracts
# --------------------------------------------------------------------------
class EmploymentContractCreate(BaseModel):
    employee_id: uuid.UUID
    contract_number: str = Field(..., min_length=1, max_length=64)
    contract_type: str = Field("PERMANENT", max_length=32)
    start_date: date
    end_date: date | None = None
    probation_end_date: date | None = None
    notice_period_days: int = Field(30, ge=0)
    base_salary: float = Field(..., ge=0.0)
    currency: str = Field("USD", min_length=3, max_length=3)
    terms_and_conditions: str | None = None
    status: str = Field("ACTIVE", max_length=32)


class EmploymentContractUpdate(BaseModel):
    contract_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    probation_end_date: date | None = None
    notice_period_days: int | None = None
    base_salary: float | None = None
    currency: str | None = None
    terms_and_conditions: str | None = None
    status: str | None = None


class EmploymentContractResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    contract_number: str
    contract_type: str
    start_date: date
    end_date: date | None = None
    probation_end_date: date | None = None
    notice_period_days: int
    base_salary: float
    currency: str
    terms_and_conditions: str | None = None
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Lifecycle Transition Events
# --------------------------------------------------------------------------
class LifecycleEventCreate(BaseModel):
    employee_id: uuid.UUID
    event_type: str = Field(
        ..., max_length=64
    )  # HIRED, PROMOTED, TRANSFERRED, DESIGNATION_CHANGED, SALARY_REVISED, PROBATION_CONFIRMED, RESIGNED, TERMINATED, RETIRED
    effective_date: date = Field(default_factory=date.today)
    previous_value_json: dict | None = None
    new_value_json: dict | None = None
    remarks: str | None = None


class LifecycleEventResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    event_type: str
    effective_date: date
    previous_value_json: dict | None = None
    new_value_json: dict | None = None
    remarks: str | None = None
    processed_by_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Onboarding Tasks
# --------------------------------------------------------------------------
class OnboardingTaskCreate(BaseModel):
    employee_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str = Field("DOCUMENTATION", max_length=64)
    due_date: date | None = None
    assigned_to_id: uuid.UUID | None = None


class OnboardingTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    due_date: date | None = None
    status: str | None = None  # PENDING, IN_PROGRESS, COMPLETED
    assigned_to_id: uuid.UUID | None = None
    completed_at: datetime | None = None


class OnboardingTaskResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    title: str
    description: str | None = None
    category: str
    due_date: date | None = None
    status: str
    assigned_to_id: uuid.UUID | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
