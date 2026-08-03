import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


# --- Salary Component Schemas ---
class SalaryComponentCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    component_type: str = Field(
        ..., description="Basic, Allowance, Deduction, Bonus, Incentive, Employer Contribution"
    )
    calculation_type: str = "flat"  # flat, percentage, formula
    taxable: bool = True
    affects_pf: bool = False
    affects_esi: bool = False
    display_order: int = 0
    status: str = "active"


class SalaryComponentUpdate(BaseModel):
    name: str | None = None
    component_type: str | None = None
    calculation_type: str | None = None
    taxable: bool | None = None
    affects_pf: bool | None = None
    affects_esi: bool | None = None
    display_order: int | None = None
    status: str | None = None


class SalaryComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    component_type: str
    calculation_type: str
    taxable: bool
    affects_pf: bool
    affects_esi: bool
    display_order: int
    status: str
    created_at: datetime
    updated_at: datetime


# --- Salary Structure & Components Schemas ---
class SalaryStructureComponentCreate(BaseModel):
    salary_component_id: uuid.UUID
    amount: float = 0.0
    percentage: float = 0.0
    formula: str | None = None
    sequence: int = 1


class SalaryStructureComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    salary_structure_id: uuid.UUID
    salary_component_id: uuid.UUID
    amount: float
    percentage: float
    formula: str | None = None
    sequence: int
    created_at: datetime
    updated_at: datetime


class SalaryStructureCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: str | None = None
    effective_from: date
    effective_to: date | None = None
    status: str = "active"
    components: list[SalaryStructureComponentCreate] = []


class SalaryStructureUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    status: str | None = None


class SalaryStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    effective_from: date
    effective_to: date | None = None
    status: str
    components: list[SalaryStructureComponentResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Employee Salary Assignment Schemas ---
class EmployeeSalaryAssignmentCreate(BaseModel):
    employee_id: uuid.UUID
    salary_structure_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    gross_salary: float = 0.0
    ctc: float = 0.0
    status: str = "active"


class EmployeeSalaryAssignmentUpdate(BaseModel):
    salary_structure_id: uuid.UUID | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    gross_salary: float | None = None
    ctc: float | None = None
    status: str | None = None


class EmployeeSalaryAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    salary_structure_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    gross_salary: float
    ctc: float
    status: str
    created_at: datetime
    updated_at: datetime


# --- Payroll Period & Run Schemas ---
class PayrollPeriodCreate(BaseModel):
    organization_id: uuid.UUID
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2050)
    start_date: date
    end_date: date
    status: str = "Open"


class PayrollPeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    month: int
    year: int
    start_date: date
    end_date: date
    status: str
    locked: bool
    created_at: datetime
    updated_at: datetime


class PayrollGenerateRequest(BaseModel):
    payroll_period_id: uuid.UUID
    processed_by: uuid.UUID | None = None


class PayrollAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payroll_run_id: uuid.UUID
    action: str
    performed_by: uuid.UUID
    timestamp: datetime
    remarks: str | None = None


class PayslipItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payslip_id: uuid.UUID
    salary_component_id: uuid.UUID | None = None
    amount: float
    component_type: str


class PayslipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    payroll_run_id: uuid.UUID
    gross_salary: float
    total_earnings: float
    total_deductions: float
    net_salary: float
    generated_at: datetime
    status: str
    items: list[PayslipItemResponse] = []
    created_at: datetime
    updated_at: datetime


class PayrollRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payroll_period_id: uuid.UUID
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processed_by: uuid.UUID | None = None
    status: str
    employees_processed: int
    payslips: list[PayslipResponse] = []
    audit_logs: list[PayrollAuditLogResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Reimbursement Schemas ---
class ReimbursementCreate(BaseModel):
    employee_id: uuid.UUID
    title: str = Field(..., max_length=200)
    amount: float
    submitted_date: date


class ReimbursementUpdate(BaseModel):
    title: str | None = None
    amount: float | None = None
    approved_date: date | None = None
    status: Literal["Pending", "Approved", "Rejected", "Paid"] | None = None


class ReimbursementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    title: str
    amount: float
    submitted_date: date
    approved_date: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# --- Employee Loan Schemas ---
class EmployeeLoanCreate(BaseModel):
    employee_id: uuid.UUID
    loan_type: str = Field(..., max_length=100)
    principal_amount: float
    remaining_amount: float | None = None
    emi_amount: float
    interest_rate: float = 0.0


class EmployeeLoanUpdate(BaseModel):
    remaining_amount: float | None = None
    emi_amount: float | None = None
    status: Literal["Pending", "Active", "Closed", "Rejected"] | None = None


class EmployeeLoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    loan_type: str
    principal_amount: float
    remaining_amount: float
    emi_amount: float
    interest_rate: float
    status: str
    created_at: datetime
    updated_at: datetime


# --- Payroll Adjustment Schemas ---
class PayrollAdjustmentCreate(BaseModel):
    employee_id: uuid.UUID
    adjustment_type: str = Field(..., description="Earning, Deduction, Bonus, Incentive, Tax Adjustment")
    amount: float
    reason: str = Field(..., max_length=500)
    payroll_period_id: uuid.UUID | None = None


class PayrollAdjustmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    adjustment_type: str
    amount: float
    reason: str
    payroll_period_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


# --- Dashboard Summary Schema ---
class PayrollDashboardSummary(BaseModel):
    payroll_status: str
    current_period: PayrollPeriodResponse | None = None
    employees_paid: int
    pending_payroll: int
    total_gross_salary: float
    total_deductions: float
    total_net_salary: float
    pending_reimbursements: float
    outstanding_loans: float


# Backward compatibility aliases
PayrollRunGenerate = PayrollGenerateRequest
LoanCreate = EmployeeLoanCreate
LoanResponse = EmployeeLoanResponse
