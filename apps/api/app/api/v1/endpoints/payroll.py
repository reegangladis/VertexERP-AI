import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.payroll import SalaryStructure
from app.repositories.hr_mgmt import SalaryStructureRepository
from app.schemas.hr_mgmt import SalaryStructureResponse, SalaryStructureCreate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

@router.get("/salary-structures", response_model=APIResponse[List[SalaryStructureResponse]])
async def list_salary_structures(
    employee_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    repo = SalaryStructureRepository(db)
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
