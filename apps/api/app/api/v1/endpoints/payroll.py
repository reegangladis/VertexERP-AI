import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.payroll import SalaryStructure, PayrollRun, Payslip
from app.repositories.hr_mgmt import (
    SalaryStructureRepository,
    PayrollRunRepository,
    PayslipRepository,
    EmployeeRepository,
)
from app.services.hr_mgmt import PayrollService
from app.schemas.hr_mgmt import (
    SalaryStructureResponse,
    SalaryStructureCreate,
    PayrollRunProcessRequest,
    PayrollRunResponse,
    PayslipResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_payroll_service(db=Depends(get_db_session)):
    return PayrollService(
        PayrollRunRepository(db),
        PayslipRepository(db),
        SalaryStructureRepository(db),
        EmployeeRepository(db),
    )

@router.get("/salary-structures", response_model=APIResponse[List[SalaryStructureResponse]])
async def list_salary_structures(
    employee_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    stmt = select(SalaryStructure).where(SalaryStructure.is_deleted == False)
    if employee_id:
        stmt = stmt.where(SalaryStructure.employee_id == employee_id)
    res = await db.execute(stmt)
    structures = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Salary structures retrieved successfully",
        data=structures
    )

@router.post("/salary-structures", response_model=APIResponse[SalaryStructureResponse])
async def create_salary_structure(
    payload: SalaryStructureCreate,
    db=Depends(get_db_session)
):
    repo = SalaryStructureRepository(db)
    struct = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Salary structure configured successfully",
        data=struct
    )

@router.post("/process", response_model=APIResponse[PayrollRunResponse])
async def process_payroll(
    payload: PayrollRunProcessRequest,
    current_user: User = Depends(get_current_user),
    service: PayrollService = Depends(get_payroll_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        payroll_run = await service.process_payroll(
            current_user.organization_id, payload.period_month, payload.period_year
        )
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Payroll processed for period {payload.period_month}/{payload.period_year}",
            data=payroll_run
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/runs", response_model=APIResponse[List[PayrollRunResponse]])
async def list_payroll_runs(
    current_user: User = Depends(get_current_user),
    service: PayrollService = Depends(get_payroll_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    runs = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Payroll runs retrieved successfully",
        data=runs
    )

@router.get("/payslips", response_model=APIResponse[List[PayslipResponse]])
async def list_payslips(
    payroll_run_id: Optional[uuid.UUID] = None,
    employee_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    stmt = select(Payslip).where(Payslip.is_deleted == False)
    if payroll_run_id:
        stmt = stmt.where(Payslip.payroll_run_id == payroll_run_id)
    if employee_id:
        stmt = stmt.where(Payslip.employee_id == employee_id)
    res = await db.execute(stmt)
    payslips = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Payslips retrieved successfully",
        data=payslips
    )

@router.get("/summary")
async def get_payroll_summary(
    current_user: User = Depends(get_current_user),
    service: PayrollService = Depends(get_payroll_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    runs = await service.repository.get_by_org(current_user.organization_id)
    latest_run = runs[0] if runs else None

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Payroll summary retrieved successfully",
        data={
            "total_runs": len(runs),
            "latest_run": {
                "period": f"{latest_run.period_month}/{latest_run.period_year}" if latest_run else "N/A",
                "status": latest_run.status if latest_run else "N/A",
                "total_gross": float(latest_run.total_gross) if latest_run else 0.0,
                "total_deductions": float(latest_run.total_deductions) if latest_run else 0.0,
                "total_net": float(latest_run.total_net) if latest_run else 0.0,
            }
        }
    )
