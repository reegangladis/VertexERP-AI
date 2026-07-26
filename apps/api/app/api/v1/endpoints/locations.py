import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.location import Location
from app.repositories.org_mgmt import LocationRepository
from app.services.org_mgmt import LocationService, parse_csv_file, generate_csv_text
from app.schemas.org_mgmt import LocationResponse, LocationCreate, LocationUpdate, BulkDeleteRequest
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_location_service(db: AsyncSession = Depends(get_db_session)):
    return LocationService(LocationRepository(db))

@router.get("", response_model=APIResponse[List[LocationResponse]])
async def list_locations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Location).where(
        Location.organization_id == current_user.organization_id,
        Location.is_deleted == False
    )
    if search:
        stmt = stmt.where(
            or_(
                Location.name.ilike(f"%{search}%"),
                Location.type.ilike(f"%{search}%"),
                Location.city.ilike(f"%{search}%"),
                Location.country.ilike(f"%{search}%")
            )
        )
    
    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(Location, field_name):
            column = getattr(Location, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(Location.name.asc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    locations = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Locations retrieved successfully",
        data=[LocationResponse.model_validate(l) for l in locations]
    )

@router.get("/{id}", response_model=APIResponse[LocationResponse])
async def get_location(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    location = await service.get(id)
    if not location or location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Location not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Location details retrieved",
        data=LocationResponse.model_validate(location)
    )

@router.post("", response_model=APIResponse[LocationResponse])
async def create_location(
    payload: LocationCreate,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id
    
    location = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Location created successfully",
        data=LocationResponse.model_validate(location)
    )

@router.put("/{id}", response_model=APIResponse[LocationResponse])
async def update_location(
    id: uuid.UUID,
    payload: LocationUpdate,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    location = await service.get(id)
    if not location or location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Location not found")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Location updated successfully",
        data=LocationResponse.model_validate(updated)
    )

@router.delete("/{id}", response_model=APIResponse[LocationResponse])
async def delete_location(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    location = await service.get(id)
    if not location or location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Location not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Location deleted successfully",
        data=LocationResponse.model_validate(deleted)
    )

@router.post("/bulk-delete", response_model=APIResponse[List[uuid.UUID]])
async def bulk_delete_locations(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    deleted_ids = []
    for item_id in payload.ids:
        location = await service.get(item_id)
        if location and location.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids
    )

@router.post("/bulk-upload", response_model=APIResponse[List[LocationResponse]])
async def bulk_upload_locations(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    content = await file.read()
    rows = parse_csv_file(content)
    
    created_locations = []
    for row in rows:
        name = row.get("name")
        if not name:
            continue
        
        location = await service.repository.create({
            "organization_id": current_user.organization_id,
            "name": name,
            "type": row.get("type", "office"),
            "address_line1": row.get("address_line1"),
            "address_line2": row.get("address_line2"),
            "country": row.get("country"),
            "state": row.get("state"),
            "city": row.get("city"),
            "postal_code": row.get("postal_code"),
            "is_active": row.get("is_active", "true").lower() == "true"
        })
        created_locations.append(LocationResponse.model_validate(location))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_locations)} locations successfully",
        data=created_locations
    )

@router.get("/export/csv")
async def export_locations_csv(
    current_user: User = Depends(get_current_user),
    service: LocationService = Depends(get_location_service)
):
    locations = await service.get_by_org(current_user.organization_id)
    headers = ["id", "name", "type", "address_line1", "country", "state", "city", "postal_code", "is_active"]
    rows = []
    for l in locations:
        rows.append({
            "id": str(l.id),
            "name": l.name,
            "type": l.type,
            "address_line1": l.address_line1 or "",
            "country": l.country or "",
            "state": l.state or "",
            "city": l.city or "",
            "postal_code": l.postal_code or "",
            "is_active": str(l.is_active)
        })
    csv_text = generate_csv_text(headers, rows)
    
    from fastapi.responses import Response
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=locations.csv"}
    )
