import uuid
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.crm_customer import Customer
from app.repositories.crm_mgmt import CustomerRepository, ContactRepository
from app.services.crm_mgmt import CustomerService
from app.schemas.crm_mgmt import CustomerResponse, CustomerCreate, CustomerUpdate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_customer_service(db=Depends(get_db_session)):
    return CustomerService(CustomerRepository(db), ContactRepository(db))

@router.get("", response_model=APIResponse[List[CustomerResponse]])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Customer).where(
        Customer.organization_id == current_user.organization_id,
        Customer.is_deleted == False
    )

    if search:
        stmt = stmt.where(Customer.name.ilike(f"%{search}%") | Customer.industry.ilike(f"%{search}%"))

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    customers = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Customers retrieved successfully",
        data=customers
    )

@router.post("", response_model=APIResponse[CustomerResponse])
async def create_customer(
    payload: CustomerCreate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        customer = await service.create_customer(current_user.organization_id, payload.dict())
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Customer account created",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=APIResponse[CustomerResponse])
async def update_customer(
    id: uuid.UUID,
    payload: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    customer = await service.repository.get(id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    updated = await service.repository.update(customer, payload.dict(exclude_unset=True))
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Customer details updated",
        data=updated
    )

@router.delete("/{id}")
async def delete_customer(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    customer = await service.repository.get(id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await service.repository.delete(customer)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Customer deleted successfully"
    )

@router.post("/bulk-upload")
async def bulk_upload_customers(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        content = await file.read()
        count = await service.bulk_import_customers_csv(current_user.organization_id, content)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} customers from CSV."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/csv")
async def export_customers(
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    customers = await service.repository.get_by_org(current_user.organization_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "type", "industry", "status", "tags"])
    for c in customers:
        tags_str = ",".join(c.tags.get("list", [])) if c.tags else ""
        writer.writerow([c.name, c.type, c.industry or "", c.status, tags_str])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers_export.csv"}
    )
