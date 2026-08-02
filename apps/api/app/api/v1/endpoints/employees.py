import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user, get_db_session
from app.models.employee import Employee, EmployeeDocument, EmployeeProfile
from app.models.user import User
from app.repositories.hr_mgmt import (
    EmployeeDocumentRepository,
    EmployeeProfileRepository,
    EmployeeRepository,
)
from app.schemas.hr_mgmt import (
    EmployeeCreate,
    EmployeeDocumentResponse,
    EmployeeResponse,
    EmployeeStatusUpdate,
    EmployeeUpdate,
)
from app.schemas.response import APIResponse
from app.services.hr_mgmt import DocumentUploadService, EmployeeService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_employee_service(db=Depends(get_db_session)):
    return EmployeeService(EmployeeRepository(db), EmployeeProfileRepository(db))


@router.get("", response_model=APIResponse[list[EmployeeResponse]])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    department_id: uuid.UUID | None = None,
    designation_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = (
        select(Employee)
        .where(
            Employee.organization_id == current_user.organization_id,
            Employee.is_deleted == False,
        )
        .options(selectinload(Employee.profile))
    )

    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    if designation_id:
        stmt = stmt.where(Employee.designation_id == designation_id)

    if search:
        # Search by code, name, email, phone (joining User or Profile)
        stmt = (
            stmt.outerjoin(Employee.profile)
            .outerjoin(User, Employee.user_id == User.id)
            .where(
                or_(
                    Employee.employee_code.ilike(f"%{search}%"),
                    EmployeeProfile.personal_email.ilike(f"%{search}%"),
                    EmployeeProfile.personal_phone.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                )
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    employees = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employees retrieved successfully",
        data=employees,
    )


@router.post("", response_model=APIResponse[EmployeeResponse])
async def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        emp = await service.create_employee(
            current_user.organization_id, payload.dict()
        )
        # Reload profile relationship
        stmt = (
            select(Employee)
            .where(Employee.id == emp.id)
            .options(selectinload(Employee.profile))
        )
        res = await service.repository.db.execute(stmt)
        emp_reloaded = res.scalar_one()
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Employee created successfully",
            data=emp_reloaded,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{id}", response_model=APIResponse[EmployeeResponse])
async def update_employee(
    id: uuid.UUID,
    payload: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    try:
        emp = await service.update_employee(id, payload.dict(exclude_unset=True))
        stmt = (
            select(Employee)
            .where(Employee.id == emp.id)
            .options(selectinload(Employee.profile))
        )
        res = await service.repository.db.execute(stmt)
        emp_reloaded = res.scalar_one()
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Employee updated successfully",
            data=emp_reloaded,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{id}")
async def delete_employee(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    emp = await service.repository.get(id)
    if emp:
        await service.repository.delete(emp)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employee deleted successfully",
    )


@router.post("/bulk-upload")
async def bulk_upload_employees(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        content = await file.read()
        count = await service.bulk_import_csv(current_user.organization_id, content)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} employees from CSV.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{id}", response_model=APIResponse[EmployeeResponse])
async def get_employee(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = (
        select(Employee)
        .where(
            Employee.id == id,
            Employee.organization_id == current_user.organization_id,
            Employee.is_deleted == False,
        )
        .options(selectinload(Employee.profile))
    )
    res = await service.repository.db.execute(stmt)
    emp = res.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employee profile retrieved successfully",
        data=emp,
    )


@router.put("/{id}/status", response_model=APIResponse[EmployeeResponse])
async def update_employee_status(
    id: uuid.UUID,
    payload: EmployeeStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    emp = await service.repository.get(id)
    if not emp or emp.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_dict = payload.dict(exclude_unset=True)
    updated = await service.repository.update(emp, update_dict)

    stmt = (
        select(Employee)
        .where(Employee.id == updated.id)
        .options(selectinload(Employee.profile))
    )
    res = await service.repository.db.execute(stmt)
    emp_reloaded = res.scalar_one()

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message=f"Employee status updated to '{payload.status}' successfully",
        data=emp_reloaded,
    )


@router.get(
    "/{id}/documents", response_model=APIResponse[list[EmployeeDocumentResponse]]
)
async def list_employee_documents(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    stmt = select(EmployeeDocument).where(
        EmployeeDocument.employee_id == id, EmployeeDocument.is_deleted == False
    )
    res = await db.execute(stmt)
    docs = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employee documents retrieved successfully",
        data=docs,
    )


@router.post("/{id}/documents", response_model=APIResponse[EmployeeDocumentResponse])
async def upload_employee_document(
    id: uuid.UUID,
    name: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    doc_service = DocumentUploadService(EmployeeDocumentRepository(db))
    doc = await doc_service.upload_document(id, name, type, file)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Employee document uploaded successfully",
        data=doc,
    )


@router.delete("/documents/{doc_id}")
async def delete_employee_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    repo = EmployeeDocumentRepository(db)
    doc = await repo.get(doc_id)
    if doc:
        await repo.delete(doc)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Employee document deleted successfully",
    )


@router.get("/export/csv")
async def export_employees(
    current_user: User = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    employees = await service.repository.get_by_org(current_user.organization_id)
    import csv
    import io

    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["employee_code", "employment_type", "status", "date_joined"])
    for e in employees:
        writer.writerow(
            [e.employee_code, e.employment_type, e.status, e.date_joined.isoformat()]
        )

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees_export.csv"},
    )
