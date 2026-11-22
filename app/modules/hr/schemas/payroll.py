"""Payroll Processing, Salary Structures, Runs, and Payslips schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Salary Components
# --------------------------------------------------------------------------
class SalaryComponentCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    component_type: str = Field("EARNING", pattern="^(EARNING|DEDUCTION|STATUTORY)$")
    calculation_type: str = Field("FIXED", pattern="^(FIXED|PERCENTAGE|FORMULA)$")
    is_taxable: bool = True
    formula_expression: str | None = None
    is_active: bool = True


class SalaryComponentUpdate(BaseModel):
    name: str | None = None
    component_type: str | None = None
    calculation_type: str | None = None
    is_taxable: bool | None = None
    formula_expression: str | None = None
    is_active: bool | None = None


class SalaryComponentResponse(SalaryComponentCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Salary Structure & Items
# --------------------------------------------------------------------------
class SalaryStructureItemCreate(BaseModel):
    component_id: uuid.UUID
    calculation_type: str = Field("FIXED", pattern="^(FIXED|PERCENTAGE)$")
    amount_or_percentage: float = Field(..., ge=0.0)
    is_active: bool = True


class SalaryStructureItemResponse(SalaryStructureItemCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    salary_structure_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SalaryStructureCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    is_active: bool = True
    items: list[SalaryStructureItemCreate] = []


class SalaryStructureUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class SalaryStructureResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    is_active: bool
    version: int
    items: list[SalaryStructureItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Employee Salary Assignment
# --------------------------------------------------------------------------
class EmployeeSalaryAssignmentCreate(BaseModel):
    employee_id: uuid.UUID
    salary_structure_id: uuid.UUID
    base_gross_salary: float = Field(..., gt=0.0)
    currency: str = Field("USD", min_length=3, max_length=3)
    effective_from: date
    effective_to: date | None = None
    is_active: bool = True


class EmployeeSalaryAssignmentResponse(EmployeeSalaryAssignmentCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Payroll Run
# --------------------------------------------------------------------------
class PayrollRunCreate(BaseModel):
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    payment_method: str = Field("DIRECT_DEPOSIT", max_length=32)


class PayrollRunApproveRequest(BaseModel):
    status: str = Field("APPROVED", pattern="^(APPROVED|CANCELLED)$")
    remarks: str | None = None


class PayrollRunResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    run_number: str
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    status: str
    total_gross: float
    total_deductions: float
    total_net: float
    total_employees: int
    payment_method: str
    processed_by_id: uuid.UUID | None = None
    approved_by_id: uuid.UUID | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Payslip & Payslip Lines
# --------------------------------------------------------------------------
class PayslipLineResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    payslip_id: uuid.UUID
    component_id: uuid.UUID | None = None
    component_name: str
    component_type: str
    amount: float
    is_taxable: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayslipResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    payroll_run_id: uuid.UUID
    employee_id: uuid.UUID
    payslip_number: str
    pay_period_start: date
    pay_period_end: date
    basic_pay: float
    allowances: float
    gross_pay: float
    deductions: float
    net_pay: float
    total_worked_days: float
    loss_of_pay_days: float
    status: str
    transaction_reference: str | None = None
    pdf_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayslipDetailedResponse(PayslipResponse):
    lines: list[PayslipLineResponse] = []
