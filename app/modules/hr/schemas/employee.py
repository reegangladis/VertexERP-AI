"""Employee Pydantic Schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    email: EmailStr
    phone: str | None = Field(None, max_length=32)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=16)  # MALE, FEMALE, NON_BINARY, OTHER
    hire_date: date = Field(default_factory=date.today)
    employment_status: str = Field("PROBATION", max_length=32)
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    reporting_manager_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    employee_number: str | None = Field(None, max_length=32)


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=64)
    last_name: str | None = Field(None, min_length=1, max_length=64)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=32)
    date_of_birth: date | None = None
    gender: str | None = None
    hire_date: date | None = None
    employment_status: str | None = None
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    reporting_manager_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    hire_date: date
    employment_status: str
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    reporting_manager_id: uuid.UUID | None = None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeDirectoryItem(BaseModel):
    id: uuid.UUID
    employee_number: str
    full_name: str
    email: str
    phone: str | None = None
    employment_status: str
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
