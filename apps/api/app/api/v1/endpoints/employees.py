import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.employee import Employee, EmployeeProfile
from app.models.department import Department
from app.models.designation import Designation
from app.repositories.hr_mgmt import EmployeeRepository, EmployeeProfileRepository
from app.services.hr_mgmt import EmployeeService
from app.schemas.hr_mgmt import EmployeeResponse, EmployeeCreate, EmployeeUpdate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_employee_service(db=Depends(get_db_session)):
    return EmployeeService(EmployeeRepository(db), EmployeeProfileRepository(db))

@router.get("", response_model=APIResponse[List[EmployeeResponse]])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    department_id: Optional[uuid.UUID] = None,
    designation_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Employee).where(
        Employee.organization_id == current_user.organization_id,
        Employee.is_deleted == False
    ).options(selectinload(Employee.profile))

    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    if designation_id:
        stmt = stmt.where(Employee.designation_id == designation_id)

    if search:
        # Search by code, name, email, phone (joining User or Profile)
        stmt = stmt.outerjoin(Employee.profile).outerjoin(User, Employee.user_id == User.id).where(
            or_(
                Employee.employee_code.ilike(f"%{search}%"),
                EmployeeProfile.personal_email.ilike(f"%{search}%"),
                EmployeeProfile.personal_phone.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    employees = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employees retrieved successfully",
        data=employees
    )

@router.post("", response_model=APIResponse[EmployeeResponse])
async def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        emp = await service.create_employee(current_user.organization_id, payload.dict())
        # Reload profile relationship
        stmt = select(Employee).where(Employee.id == emp.id).options(selectinload(Employee.profile))
        res = await service.repository.db.execute(stmt)
        emp_reloaded = res.scalar_one()
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Employee created successfully",
            data=emp_reloaded
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=APIResponse[EmployeeResponse])
async def update_employee(
    id: uuid.UUID,
    payload: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    try:
        emp = await service.update_employee(id, payload.dict(exclude_unset=True))
        stmt = select(Employee).where(Employee.id == emp.id).options(selectinload(Employee.profile))
        res = await service.repository.db.execute(stmt)
        emp_reloaded = res.scalar_one()
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Employee updated successfully",
            data=emp_reloaded
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_employee(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    emp = await service.repository.get(id)
    if emp:
        await service.repository.delete(emp)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employee deleted successfully"
    )

@router.post("/bulk-upload")
async def bulk_upload_employees(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        content = await file.read()
        count = await service.bulk_import_csv(current_user.organization_id, content)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} employees from CSV."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/csv")
async def export_employees(
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    employees = await service.repository.get_by_org(current_user.organization_id)
    import io
    import csv
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["employee_code", "employment_type", "status", "date_joined"])
    for e in employees:
        writer.writerow([e.employee_code, e.employment_type, e.status, e.date_joined.isoformat()])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees_export.csv"}
    )
