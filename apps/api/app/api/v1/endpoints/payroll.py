import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.schemas.payroll import (
    EmployeeLoanCreate,
    EmployeeLoanResponse,
    EmployeeLoanUpdate,
    EmployeeSalaryAssignmentCreate,
    EmployeeSalaryAssignmentResponse,
    EmployeeSalaryAssignmentUpdate,
    PayrollAdjustmentCreate,
    PayrollAdjustmentResponse,
    PayrollDashboardSummary,
    PayrollGenerateRequest,
    PayrollPeriodCreate,
    PayrollPeriodResponse,
    PayrollRunResponse,
    PayslipResponse,
    ReimbursementCreate,
    ReimbursementResponse,
    ReimbursementUpdate,
    SalaryComponentCreate,
    SalaryComponentResponse,
    SalaryComponentUpdate,
    SalaryStructureCreate,
    SalaryStructureResponse,
    SalaryStructureUpdate,
)
from app.services.payroll import PayrollService

router = APIRouter()


def get_payroll_service(db: AsyncSession = Depends(get_db_session)) -> PayrollService:
    return PayrollService(db)


# --- Salary Components ---
@router.post("/salary-components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    payload: SalaryComponentCreate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_component(payload)


@router.get("/salary-components", response_model=list[SalaryComponentResponse])
async def list_components(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_components(org_id)


@router.get("/salary-components/{id}", response_model=SalaryComponentResponse)
async def get_component(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.get_component(id)


@router.patch("/salary-components/{id}", response_model=SalaryComponentResponse)
async def update_component(
    id: uuid.UUID,
    payload: SalaryComponentUpdate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.update_component(id, payload)


@router.delete("/salary-components/{id}", response_model=SalaryComponentResponse)
async def delete_component(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.delete_component(id)


# --- Salary Structures ---
@router.post("/salary-structures", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_structure(
    payload: SalaryStructureCreate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_structure(payload)


@router.get("/salary-structures", response_model=list[SalaryStructureResponse])
async def list_structures(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_structures(org_id)


@router.get("/salary-structures/{id}", response_model=SalaryStructureResponse)
async def get_structure(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.get_structure(id)


@router.patch("/salary-structures/{id}", response_model=SalaryStructureResponse)
async def update_structure(
    id: uuid.UUID,
    payload: SalaryStructureUpdate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.update_structure(id, payload)


@router.delete("/salary-structures/{id}", response_model=SalaryStructureResponse)
async def delete_structure(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.delete_structure(id)


# --- Employee Salary Assignments ---
@router.post("/employee-salary-assignments", response_model=EmployeeSalaryAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_salary(
    payload: EmployeeSalaryAssignmentCreate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.assign_salary(payload)


@router.get("/employee-salary-assignments", response_model=list[EmployeeSalaryAssignmentResponse])
async def list_assignments(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_assignments(org_id)


@router.get("/employee-salary-assignments/employee/{employee_id}", response_model=list[EmployeeSalaryAssignmentResponse])
async def get_employee_assignment_history(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.get_employee_assignment_history(employee_id)


@router.patch("/employee-salary-assignments/{id}", response_model=EmployeeSalaryAssignmentResponse)
async def update_assignment(
    id: uuid.UUID,
    payload: EmployeeSalaryAssignmentUpdate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.update_assignment(id, payload)


# --- Payroll Periods & Locking ---
@router.post("/payroll-periods", response_model=PayrollPeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_period(
    payload: PayrollPeriodCreate,
    current_user: User = Depends(PermissionChecker("payroll.generate")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_period(payload)


@router.get("/payroll-periods", response_model=list[PayrollPeriodResponse])
async def list_periods(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_periods(org_id)


@router.post("/payroll-periods/{id}/lock", response_model=PayrollPeriodResponse)
async def lock_period(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.lock")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.lock_period(id)


@router.post("/payroll-periods/{id}/unlock", response_model=PayrollPeriodResponse)
async def unlock_period(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.lock")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.unlock_period(id)


# --- Payroll Runs & Processing ---
@router.post("/payroll-runs/generate", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
async def generate_payroll_run(
    payload: PayrollGenerateRequest,
    current_user: User = Depends(PermissionChecker("payroll.generate")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.generate_payroll_run(payload)


@router.get("/payroll-runs", response_model=list[PayrollRunResponse])
async def list_payroll_runs(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_payroll_runs(org_id)


@router.post("/payroll-runs/{id}/approve", response_model=PayrollRunResponse)
async def approve_payroll_run(
    id: uuid.UUID,
    approver_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.approve")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.approve_payroll_run(id, approver_id)


# --- Payslips & PDF Download ---
@router.get("/payslips/{id}", response_model=PayslipResponse)
async def get_payslip(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.get_payslip(id)


@router.get("/payslips/employee/{employee_id}", response_model=list[PayslipResponse])
async def list_payslips_by_employee(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_payslips_by_employee(employee_id)


@router.get("/payslips/{id}/download")
async def download_payslip_pdf(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    content = await service.generate_payslip_pdf(id)
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=payslip_{id}.txt"},
    )


# --- Reimbursements ---
@router.post("/reimbursements", response_model=ReimbursementResponse, status_code=status.HTTP_201_CREATED)
async def create_reimbursement(
    payload: ReimbursementCreate,
    current_user: User = Depends(PermissionChecker("reimbursement.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_reimbursement(payload)


@router.get("/reimbursements", response_model=list[ReimbursementResponse])
async def list_reimbursements(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_reimbursements(employee_id)


@router.patch("/reimbursements/{id}", response_model=ReimbursementResponse)
async def update_reimbursement(
    id: uuid.UUID,
    payload: ReimbursementUpdate,
    current_user: User = Depends(PermissionChecker("reimbursement.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.update_reimbursement(id, payload)


@router.delete("/reimbursements/{id}", response_model=ReimbursementResponse)
async def delete_reimbursement(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("reimbursement.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.delete_reimbursement(id)


# --- Employee Loans ---
@router.post("/employee-loans", response_model=EmployeeLoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    payload: EmployeeLoanCreate,
    current_user: User = Depends(PermissionChecker("loan.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_loan(payload)


@router.get("/employee-loans", response_model=list[EmployeeLoanResponse])
async def list_loans(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.list_loans(employee_id)


@router.patch("/employee-loans/{id}", response_model=EmployeeLoanResponse)
async def update_loan(
    id: uuid.UUID,
    payload: EmployeeLoanUpdate,
    current_user: User = Depends(PermissionChecker("loan.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.update_loan(id, payload)


@router.delete("/employee-loans/{id}", response_model=EmployeeLoanResponse)
async def delete_loan(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("loan.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.delete_loan(id)


# --- Payroll Adjustments ---
@router.post("/payroll-adjustments", response_model=PayrollAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    payload: PayrollAdjustmentCreate,
    current_user: User = Depends(PermissionChecker("salary.manage")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.create_adjustment(payload)


# --- Dashboard Summary ---
@router.get("/payroll-dashboard-summary", response_model=PayrollDashboardSummary)
async def get_dashboard_summary(
    org_id: uuid.UUID = Query(...),
    employee_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(PermissionChecker("payroll.read")),
    service: PayrollService = Depends(get_payroll_service),
):
    return await service.get_dashboard_summary(org_id, employee_id)
