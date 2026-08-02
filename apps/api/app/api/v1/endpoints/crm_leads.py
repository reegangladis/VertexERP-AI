import csv
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select

from app.core.dependencies import get_current_user, get_db_session
from app.models.crm_lead import Lead
from app.models.user import User
from app.repositories.crm_mgmt import (
    ContactRepository,
    CustomerRepository,
    DealRepository,
    LeadActivityRepository,
    LeadRepository,
    LeadSourceRepository,
    OpportunityRepository,
)
from app.schemas.crm_mgmt import (
    LeadConvertRequest,
    LeadCreate,
    LeadResponse,
    LeadUpdate,
)
from app.schemas.response import APIResponse
from app.services.crm_mgmt import LeadService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_lead_service(db=Depends(get_db_session)):
    return LeadService(
        LeadRepository(db), LeadSourceRepository(db), LeadActivityRepository(db)
    )


@router.get("", response_model=APIResponse[list[LeadResponse]])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Lead).where(
        Lead.organization_id == current_user.organization_id, Lead.is_deleted == False
    )

    if search:
        stmt = stmt.where(
            or_(
                Lead.first_name.ilike(f"%{search}%"),
                Lead.last_name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.company.ilike(f"%{search}%"),
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    leads = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Leads retrieved successfully",
        data=leads,
    )


@router.post("", response_model=APIResponse[LeadResponse])
async def create_lead(
    payload: LeadCreate,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        lead = await service.create_lead(current_user.organization_id, payload.dict())
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Lead captured successfully",
            data=lead,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{id}", response_model=APIResponse[LeadResponse])
async def get_lead(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    lead = await service.repository.get(id)
    if (
        not lead
        or lead.organization_id != current_user.organization_id
        or lead.is_deleted
    ):
        raise HTTPException(status_code=404, detail="Lead not found")

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Lead details retrieved",
        data=lead,
    )


@router.post("/{id}/convert")
async def convert_lead(
    id: uuid.UUID,
    payload: LeadConvertRequest,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        res = await service.convert_lead(
            lead_id=id,
            customer_repo=CustomerRepository(db),
            contact_repo=ContactRepository(db),
            opp_repo=OpportunityRepository(db),
            deal_repo=DealRepository(db),
            payload_data=payload.dict(),
        )
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Lead converted successfully to Customer account and Deal.",
            data={
                "customer_id": res["customer"].id,
                "contact_id": res["contact"].id,
                "deal_id": res["deal"].id if res["deal"] else None,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{id}", response_model=APIResponse[LeadResponse])
async def update_lead(
    id: uuid.UUID,
    payload: LeadUpdate,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.repository.get(id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    updated = await service.repository.update(lead, payload.dict(exclude_unset=True))
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Lead details updated",
        data=updated,
    )


@router.delete("/{id}")
async def delete_lead(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.repository.get(id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await service.repository.delete(lead)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Lead deleted successfully",
    )


@router.post("/bulk-upload")
async def bulk_upload_leads(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        content = await file.read()
        count = await service.bulk_import_leads_csv(
            current_user.organization_id, content
        )
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} leads from CSV.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/export/csv")
async def export_leads(
    current_user: User = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    leads = await service.repository.get_by_org(current_user.organization_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["first_name", "last_name", "email", "phone", "company", "status", "score"]
    )
    for l in leads:
        writer.writerow(
            [
                l.first_name,
                l.last_name,
                l.email,
                l.phone or "",
                l.company or "",
                l.status,
                l.score,
            ]
        )

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )
