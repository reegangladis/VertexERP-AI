import uuid
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_supplier import Supplier
from app.repositories.inventory_mgmt import SupplierRepository, SupplierContactRepository
from app.services.inventory_mgmt import SupplierService
from app.schemas.inventory_mgmt import SupplierResponse, SupplierCreate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_supplier_service(db=Depends(get_db_session)):
    return SupplierService(SupplierRepository(db), SupplierContactRepository(db))

@router.get("", response_model=APIResponse[List[SupplierResponse]])
async def list_suppliers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Supplier).where(
        Supplier.organization_id == current_user.organization_id,
        Supplier.is_deleted == False
    )

    if search:
        stmt = stmt.where(Supplier.name.ilike(f"%{search}%") | Supplier.code.ilike(f"%{search}%"))

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    suppliers = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Suppliers retrieved successfully",
        data=suppliers
    )

@router.post("", response_model=APIResponse[SupplierResponse])
async def create_supplier(
    payload: SupplierCreate,
    current_user: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        supplier = await service.repository.create({
            "organization_id": current_user.organization_id,
            **payload.dict(exclude={"contacts"})
        })
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Supplier profile created successfully",
            data=supplier
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-upload")
async def bulk_upload_suppliers(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        content = await file.read()
        count = await service.bulk_import_suppliers_csv(current_user.organization_id, content)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} suppliers from CSV."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/csv")
async def export_suppliers(
    current_user: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    suppliers = await service.repository.get_by_org(current_user.organization_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "code", "gst_vat", "payment_terms", "rating"])
    for s in suppliers:
        writer.writerow([s.name, s.code, s.gst_vat or "", s.payment_terms or "Net 30", s.rating or 5.0])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=suppliers_export.csv"}
    )
