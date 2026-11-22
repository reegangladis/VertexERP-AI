"""Payroll Processing, Salary Structures, Runs, and Payslips API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.payroll import (
    EmployeeSalaryAssignmentCreate,
    EmployeeSalaryAssignmentResponse,
    PayrollRunApproveRequest,
    PayrollRunCreate,
    PayrollRunResponse,
    PayslipDetailedResponse,
    PayslipLineResponse,
    PayslipResponse,
    SalaryComponentCreate,
    SalaryComponentResponse,
    SalaryStructureCreate,
    SalaryStructureItemResponse,
    SalaryStructureResponse,
)
from app.modules.hr.services.payroll_service import PayrollService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/payroll", tags=["HR Payroll Processing"])


# --------------------------------------------------------------------------
# Salary Components
# --------------------------------------------------------------------------
@router.post(
    "/components",
    response_model=SalaryComponentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Salary Component",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_WRITE.value))],
)
async def create_salary_component(
    req: SalaryComponentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SalaryComponentResponse:
    """Creates a salary earning, deduction, or statutory component."""
    service = PayrollService(db)
    comp = await service.create_component(tenant_id, org_id, req)
    return SalaryComponentResponse.model_validate(comp)


@router.get(
    "/components",
    response_model=list[SalaryComponentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Salary Components",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def list_salary_components(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[SalaryComponentResponse]:
    """Lists salary components."""
    service = PayrollService(db)
    comps = await service.list_components(tenant_id, org_id, is_active)
    return [SalaryComponentResponse.model_validate(c) for c in comps]


# --------------------------------------------------------------------------
# Salary Structures
# --------------------------------------------------------------------------
@router.post(
    "/structures",
    response_model=SalaryStructureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Salary Structure Template",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_WRITE.value))],
)
async def create_salary_structure(
    req: SalaryStructureCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SalaryStructureResponse:
    """Creates a salary package template structure with items."""
    service = PayrollService(db)
    struct, items = await service.create_structure(tenant_id, org_id, req)
    return SalaryStructureResponse(
        id=struct.id,
        tenant_id=struct.tenant_id,
        organization_id=struct.organization_id,
        code=struct.code,
        name=struct.name,
        description=struct.description,
        is_active=struct.is_active,
        version=struct.version,
        items=[SalaryStructureItemResponse.model_validate(i) for i in items],
        created_at=struct.created_at,
        updated_at=struct.updated_at,
    )


@router.get(
    "/structures",
    response_model=list[SalaryStructureResponse],
    status_code=status.HTTP_200_OK,
    summary="List Salary Structures",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def list_salary_structures(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[SalaryStructureResponse]:
    """Lists salary structures."""
    service = PayrollService(db)
    structs = await service.list_structures(tenant_id, org_id, is_active)
    result = []
    for s in structs:
        _, items = await service.get_structure(s.id, tenant_id, org_id)
        result.append(
            SalaryStructureResponse(
                id=s.id,
                tenant_id=s.tenant_id,
                organization_id=s.organization_id,
                code=s.code,
                name=s.name,
                description=s.description,
                is_active=s.is_active,
                version=s.version,
                items=[SalaryStructureItemResponse.model_validate(i) for i in items],
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )
    return result


# --------------------------------------------------------------------------
# Salary Assignments
# --------------------------------------------------------------------------
@router.post(
    "/assignments",
    response_model=EmployeeSalaryAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Salary Structure to Employee",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_WRITE.value))],
)
async def assign_salary_structure(
    req: EmployeeSalaryAssignmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeSalaryAssignmentResponse:
    """Assigns compensation structure and base gross salary to an employee."""
    service = PayrollService(db)
    asgn = await service.create_assignment(tenant_id, org_id, req)
    return EmployeeSalaryAssignmentResponse.model_validate(asgn)


@router.get(
    "/assignments/employee/{employee_id}",
    response_model=EmployeeSalaryAssignmentResponse | None,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Salary Assignment",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def get_employee_salary_assignment(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> EmployeeSalaryAssignmentResponse | None:
    """Gets current active salary assignment for an employee."""
    service = PayrollService(db)
    asgn = await service.get_assignment_by_employee(employee_id, tenant_id, org_id)
    if not asgn:
        return None
    return EmployeeSalaryAssignmentResponse.model_validate(asgn)


# --------------------------------------------------------------------------
# Payroll Runs & Batches
# --------------------------------------------------------------------------
@router.post(
    "/runs",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Draft Payroll Run",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_WRITE.value))],
)
async def create_payroll_run(
    req: PayrollRunCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PayrollRunResponse:
    """Creates a new draft payroll batch."""
    service = PayrollService(db)
    run = await service.create_payroll_run(tenant_id, org_id, req, current_user.id)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PAYROLL_RUN_CREATED",
        description=f"Payroll run '{run.run_number}' for period {run.pay_period_start} to {run.pay_period_end} created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return PayrollRunResponse.model_validate(run)


@router.post(
    "/runs/{run_id}/process",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Batch Payroll Calculation",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_PROCESS.value))],
)
async def process_payroll_run(
    run_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PayrollRunResponse:
    """Calculates gross-to-net payslips atomically for all assigned employees."""
    service = PayrollService(db)
    run = await service.process_payroll_run(run_id, tenant_id, org_id, current_user.id)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PAYROLL_RUN_PROCESSED",
        description=f"Payroll run '{run.run_number}' processed for {run.total_employees} employees. Net total: {run.total_net}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return PayrollRunResponse.model_validate(run)


@router.put(
    "/runs/{run_id}/approve",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Payroll Run",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_APPROVE.value))],
)
async def approve_payroll_run(
    run_id: uuid.UUID,
    req: PayrollRunApproveRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PayrollRunResponse:
    """Approves a calculated payroll batch."""
    service = PayrollService(db)
    run = await service.approve_payroll_run(run_id, tenant_id, org_id, current_user.id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PAYROLL_RUN_APPROVED",
        description=f"Payroll run '{run.run_number}' approved by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return PayrollRunResponse.model_validate(run)


@router.post(
    "/runs/{run_id}/disburse",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Disburse Payroll Run",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_DISBURSE.value))],
)
async def disburse_payroll_run(
    run_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PayrollRunResponse:
    """Finalizes disbursement and marks all payslips as paid."""
    service = PayrollService(db)
    run = await service.disburse_payroll_run(run_id, tenant_id, org_id, current_user.id)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PAYROLL_RUN_DISBURSED",
        description=f"Payroll run '{run.run_number}' disbursed by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return PayrollRunResponse.model_validate(run)


@router.get(
    "/runs",
    response_model=list[PayrollRunResponse],
    status_code=status.HTTP_200_OK,
    summary="List Payroll Runs",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def list_payroll_runs(
    status: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[PayrollRunResponse]:
    """Lists payroll runs."""
    service = PayrollService(db)
    runs = await service.list_payroll_runs(tenant_id, org_id, status)
    return [PayrollRunResponse.model_validate(r) for r in runs]


@router.get(
    "/runs/{run_id}",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Payroll Run Details",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def get_payroll_run(
    run_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PayrollRunResponse:
    """Gets payroll run by ID."""
    service = PayrollService(db)
    run = await service.get_payroll_run(run_id, tenant_id, org_id)
    return PayrollRunResponse.model_validate(run)


# --------------------------------------------------------------------------
# Payslips
# --------------------------------------------------------------------------
@router.get(
    "/payslips/run/{run_id}",
    response_model=list[PayslipResponse],
    status_code=status.HTTP_200_OK,
    summary="List Payslips in Payroll Run",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def list_payslips_for_run(
    run_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[PayslipResponse]:
    """Lists all payslips generated for a specific payroll run."""
    service = PayrollService(db)
    payslips = await service.list_payslips_for_run(run_id, tenant_id, org_id)
    return [PayslipResponse.model_validate(p) for p in payslips]


@router.get(
    "/payslips/{payslip_id}",
    response_model=PayslipDetailedResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Payslip Details with Itemized Lines",
    dependencies=[Depends(require_permission(PermissionCode.HR_PAYROLL_READ.value))],
)
async def get_payslip(
    payslip_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PayslipDetailedResponse:
    """Gets itemized payslip breakdown."""
    service = PayrollService(db)
    payslip, lines = await service.get_payslip(payslip_id, tenant_id, org_id)
    return PayslipDetailedResponse(
        id=payslip.id,
        tenant_id=payslip.tenant_id,
        organization_id=payslip.organization_id,
        payroll_run_id=payslip.payroll_run_id,
        employee_id=payslip.employee_id,
        payslip_number=payslip.payslip_number,
        pay_period_start=payslip.pay_period_start,
        pay_period_end=payslip.pay_period_end,
        basic_pay=float(payslip.basic_pay),
        allowances=float(payslip.allowances),
        gross_pay=float(payslip.gross_pay),
        deductions=float(payslip.deductions),
        net_pay=float(payslip.net_pay),
        total_worked_days=float(payslip.total_worked_days),
        loss_of_pay_days=float(payslip.loss_of_pay_days),
        status=payslip.status,
        transaction_reference=payslip.transaction_reference,
        pdf_url=payslip.pdf_url,
        lines=[
            PayslipLineResponse(
                id=l.id,
                tenant_id=l.tenant_id,
                organization_id=l.organization_id,
                payslip_id=l.payslip_id,
                component_id=l.component_id,
                component_name=l.component_name,
                component_type=l.component_type,
                amount=float(l.amount),
                is_taxable=l.is_taxable,
                created_at=l.created_at,
            )
            for l in lines
        ],
        created_at=payslip.created_at,
    )
