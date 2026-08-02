import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.business_unit import BusinessUnit
from app.models.user import User
from app.repositories.org_mgmt import BusinessUnitRepository
from app.schemas.org_mgmt import (
    BulkDeleteRequest,
    BusinessUnitCreate,
    BusinessUnitResponse,
    BusinessUnitUpdate,
)
from app.schemas.response import APIResponse
from app.services.org_mgmt import BusinessUnitService, generate_csv_text, parse_csv_file
from app.utils.response import standard_json_response

router = APIRouter()


async def get_business_unit_service(db: AsyncSession = Depends(get_db_session)):
    return BusinessUnitService(BusinessUnitRepository(db))


@router.get("", response_model=APIResponse[list[BusinessUnitResponse]])
async def list_business_units(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort: str | None = None,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(BusinessUnit).where(
        BusinessUnit.organization_id == current_user.organization_id,
        BusinessUnit.is_deleted == False,
    )
    if search:
        stmt = stmt.where(
            or_(
                BusinessUnit.name.ilike(f"%{search}%"),
                BusinessUnit.slug.ilike(f"%{search}%"),
                BusinessUnit.code.ilike(f"%{search}%"),
            )
        )

    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(BusinessUnit, field_name):
            column = getattr(BusinessUnit, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(BusinessUnit.name.asc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    units = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Business units retrieved successfully",
        data=[BusinessUnitResponse.model_validate(u) for u in units],
    )


@router.get("/{id}", response_model=APIResponse[BusinessUnitResponse])
async def get_business_unit(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    unit = await service.get(id)
    if not unit or unit.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Business unit not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Business unit details retrieved",
        data=BusinessUnitResponse.model_validate(unit),
    )


@router.post("", response_model=APIResponse[BusinessUnitResponse])
async def create_business_unit(
    payload: BusinessUnitCreate,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id

    unit = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Business unit created successfully",
        data=BusinessUnitResponse.model_validate(unit),
    )


@router.put("/{id}", response_model=APIResponse[BusinessUnitResponse])
async def update_business_unit(
    id: uuid.UUID,
    payload: BusinessUnitUpdate,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    unit = await service.get(id)
    if not unit or unit.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Business unit not found")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Business unit updated successfully",
        data=BusinessUnitResponse.model_validate(updated),
    )


@router.delete("/{id}", response_model=APIResponse[BusinessUnitResponse])
async def delete_business_unit(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    unit = await service.get(id)
    if not unit or unit.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Business unit not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Business unit deleted successfully",
        data=BusinessUnitResponse.model_validate(deleted),
    )


@router.post("/bulk-delete", response_model=APIResponse[list[uuid.UUID]])
async def bulk_delete_business_units(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    deleted_ids = []
    for item_id in payload.ids:
        unit = await service.get(item_id)
        if unit and unit.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids,
    )


@router.post("/bulk-upload", response_model=APIResponse[list[BusinessUnitResponse]])
async def bulk_upload_business_units(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    content = await file.read()
    rows = parse_csv_file(content)

    created_units = []
    for row in rows:
        name = row.get("name")
        slug = row.get("slug") or (name.lower().replace(" ", "-") if name else None)
        if not name or not slug:
            continue

        unit = await service.repository.create(
            {
                "organization_id": current_user.organization_id,
                "name": name,
                "slug": slug,
                "code": row.get("code"),
                "description": row.get("description"),
                "status": row.get("status", "active"),
            }
        )
        created_units.append(BusinessUnitResponse.model_validate(unit))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_units)} business units successfully",
        data=created_units,
    )


@router.get("/export/csv")
async def export_business_units_csv(
    current_user: User = Depends(get_current_user),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    units = await service.get_by_org(current_user.organization_id)
    headers = ["id", "name", "slug", "code", "description", "status"]
    rows = []
    for u in units:
        rows.append(
            {
                "id": str(u.id),
                "name": u.name,
                "slug": u.slug,
                "code": u.code or "",
                "description": u.description or "",
                "status": u.status,
            }
        )
    csv_text = generate_csv_text(headers, rows)

    from fastapi.responses import Response

    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=business_units.csv"},
    )
