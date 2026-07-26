import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.designation import Designation
from app.repositories.org_mgmt import DesignationRepository
from app.services.org_mgmt import DesignationService, parse_csv_file, generate_csv_text
from app.schemas.org_mgmt import DesignationResponse, DesignationCreate, DesignationUpdate, BulkDeleteRequest
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_designation_service(db: AsyncSession = Depends(get_db_session)):
    return DesignationService(DesignationRepository(db))

@router.get("", response_model=APIResponse[List[DesignationResponse]])
async def list_designations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Designation).where(
        Designation.organization_id == current_user.organization_id,
        Designation.is_deleted == False
    )
    if search:
        stmt = stmt.where(
            or_(
                Designation.name.ilike(f"%{search}%"),
                Designation.title.ilike(f"%{search}%"),
                Designation.code.ilike(f"%{search}%")
            )
        )
    
    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(Designation, field_name):
            column = getattr(Designation, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(Designation.reporting_level.desc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    designations = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Designations retrieved successfully",
        data=[DesignationResponse.model_validate(d) for d in designations]
    )

@router.get("/{id}", response_model=APIResponse[DesignationResponse])
async def get_designation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    designation = await service.get(id)
    if not designation or designation.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Designation not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Designation details retrieved",
        data=DesignationResponse.model_validate(designation)
    )

@router.post("", response_model=APIResponse[DesignationResponse])
async def create_designation(
    payload: DesignationCreate,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id
    
    designation = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Designation created successfully",
        data=DesignationResponse.model_validate(designation)
    )

@router.put("/{id}", response_model=APIResponse[DesignationResponse])
async def update_designation(
    id: uuid.UUID,
    payload: DesignationUpdate,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    designation = await service.get(id)
    if not designation or designation.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Designation not found")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Designation updated successfully",
        data=DesignationResponse.model_validate(updated)
    )

@router.delete("/{id}", response_model=APIResponse[DesignationResponse])
async def delete_designation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    designation = await service.get(id)
    if not designation or designation.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Designation not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Designation deleted successfully",
        data=DesignationResponse.model_validate(deleted)
    )

@router.post("/bulk-delete", response_model=APIResponse[List[uuid.UUID]])
async def bulk_delete_designations(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    deleted_ids = []
    for item_id in payload.ids:
        designation = await service.get(item_id)
        if designation and designation.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids
    )

@router.post("/bulk-upload", response_model=APIResponse[List[DesignationResponse]])
async def bulk_upload_designations(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    content = await file.read()
    rows = parse_csv_file(content)
    
    created_designations = []
    for row in rows:
        name = row.get("name")
        title = row.get("title") or name
        slug = row.get("slug") or name.lower().replace(" ", "-") if name else None
        if not name:
            continue
        
        designation = await service.repository.create({
            "organization_id": current_user.organization_id,
            "name": name,
            "title": title,
            "slug": slug,
            "code": row.get("code"),
            "job_level": row.get("job_level"),
            "grade": row.get("grade"),
            "reporting_level": int(row.get("reporting_level", 1) or 1),
            "description": row.get("description")
        })
        created_designations.append(DesignationResponse.model_validate(designation))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_designations)} designations successfully",
        data=created_designations
    )

@router.get("/export/csv")
async def export_designations_csv(
    current_user: User = Depends(get_current_user),
    service: DesignationService = Depends(get_designation_service)
):
    designations = await service.get_by_org(current_user.organization_id)
    headers = ["id", "name", "title", "slug", "code", "job_level", "grade", "reporting_level", "description"]
    rows = []
    for d in designations:
        rows.append({
            "id": str(d.id),
            "name": d.name,
            "title": d.title,
            "slug": d.slug,
            "code": d.code or "",
            "job_level": d.job_level or "",
            "grade": d.grade or "",
            "reporting_level": str(d.reporting_level),
            "description": d.description or ""
        })
    csv_text = generate_csv_text(headers, rows)
    
    from fastapi.responses import Response
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=designations.csv"}
    )
