import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.department import Department
from app.repositories.org_mgmt import DepartmentRepository
from app.services.org_mgmt import DepartmentService, parse_csv_file, generate_csv_text, OrgMgmtServiceException
from app.schemas.org_mgmt import DepartmentResponse, DepartmentCreate, DepartmentUpdate, BulkDeleteRequest
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_department_service(db: AsyncSession = Depends(get_db_session)):
    return DepartmentService(DepartmentRepository(db))

@router.get("", response_model=APIResponse[List[DepartmentResponse]])
async def list_departments(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    branch_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Department).where(
        Department.organization_id == current_user.organization_id,
        Department.is_deleted == False
    )
    if branch_id:
        stmt = stmt.where(Department.branch_id == branch_id)
        
    if search:
        stmt = stmt.where(
            or_(
                Department.name.ilike(f"%{search}%"),
                Department.slug.ilike(f"%{search}%"),
                Department.code.ilike(f"%{search}%")
            )
        )
    
    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(Department, field_name):
            column = getattr(Department, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(Department.name.asc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    departments = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Departments retrieved successfully",
        data=[DepartmentResponse.model_validate(d) for d in departments]
    )

@router.get("/{id}", response_model=APIResponse[DepartmentResponse])
async def get_department(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    dept = await service.get(id)
    if not dept or dept.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Department not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Department details retrieved",
        data=DepartmentResponse.model_validate(dept)
    )

@router.post("", response_model=APIResponse[DepartmentResponse])
async def create_department(
    payload: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    if payload.parent_department_id:
        parent = await service.get(payload.parent_department_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent department")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id
    
    dept = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Department created successfully",
        data=DepartmentResponse.model_validate(dept)
    )

@router.put("/{id}", response_model=APIResponse[DepartmentResponse])
async def update_department(
    id: uuid.UUID,
    payload: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    dept = await service.get(id)
    if not dept or dept.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Department not found")

    if payload.parent_department_id:
        try:
            await service.validate_parent(id, payload.parent_department_id)
        except OrgMgmtServiceException as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        parent = await service.get(payload.parent_department_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent department")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Department updated successfully",
        data=DepartmentResponse.model_validate(updated)
    )

@router.delete("/{id}", response_model=APIResponse[DepartmentResponse])
async def delete_department(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    dept = await service.get(id)
    if not dept or dept.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Department not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Department deleted successfully",
        data=DepartmentResponse.model_validate(deleted)
    )

@router.post("/bulk-delete", response_model=APIResponse[List[uuid.UUID]])
async def bulk_delete_departments(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    deleted_ids = []
    for item_id in payload.ids:
        dept = await service.get(item_id)
        if dept and dept.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids
    )

@router.post("/bulk-upload", response_model=APIResponse[List[DepartmentResponse]])
async def bulk_upload_departments(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    content = await file.read()
    rows = parse_csv_file(content)
    
    created_depts = []
    for row in rows:
        name = row.get("name")
        slug = row.get("slug") or name.lower().replace(" ", "-") if name else None
        if not name:
            continue
        
        dept = await service.repository.create({
            "organization_id": current_user.organization_id,
            "name": name,
            "slug": slug,
            "code": row.get("code"),
            "budget": float(row.get("budget", 0.0) or 0.0),
            "status": row.get("status", "active")
        })
        created_depts.append(DepartmentResponse.model_validate(dept))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_depts)} departments successfully",
        data=created_depts
    )

@router.get("/export/csv")
async def export_departments_csv(
    current_user: User = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service)
):
    depts = await service.get_by_org(current_user.organization_id)
    headers = ["id", "name", "slug", "code", "budget", "status"]
    rows = []
    for d in depts:
        rows.append({
            "id": str(d.id),
            "name": d.name,
            "slug": d.slug,
            "code": d.code or "",
            "budget": str(d.budget),
            "status": d.status
        })
    csv_text = generate_csv_text(headers, rows)
    
    from fastapi.responses import Response
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=departments.csv"}
    )
