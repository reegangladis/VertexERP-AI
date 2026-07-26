import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.crm_deal import Opportunity, Deal
from app.repositories.crm_mgmt import OpportunityRepository, DealRepository, QuotationRepository
from app.services.crm_mgmt import DealService
from app.schemas.crm_mgmt import (
    OpportunityResponse,
    OpportunityCreate,
    DealResponse,
    DealCreate,
    DealUpdate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_deal_service(db=Depends(get_db_session)):
    return DealService(DealRepository(db), QuotationRepository(db))

# 1. Opportunities Endpoints
@router.get("/opportunities", response_model=APIResponse[List[OpportunityResponse]])
async def list_opportunities(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = OpportunityRepository(db)
    opps = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Opportunities retrieved successfully",
        data=opps
    )

@router.post("/opportunities", response_model=APIResponse[OpportunityResponse])
async def create_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = OpportunityRepository(db)
    opp = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Opportunity defined successfully",
        data=opp
    )

# 2. Deals Endpoints
@router.get("", response_model=APIResponse[List[DealResponse]])
async def list_deals(
    current_user: User = Depends(get_current_user),
    service: DealService = Depends(get_deal_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    deals = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Deals retrieved successfully",
        data=deals
    )

@router.post("", response_model=APIResponse[DealResponse])
async def create_deal(
    payload: DealCreate,
    current_user: User = Depends(get_current_user),
    service: DealService = Depends(get_deal_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    deal = await service.repository.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Deal launched into pipeline",
        data=deal
    )

@router.put("/{id}/result", response_model=APIResponse[DealResponse])
async def process_deal_result(
    id: uuid.UUID,
    payload: DealUpdate,
    current_user: User = Depends(get_current_user),
    service: DealService = Depends(get_deal_service)
):
    try:
        deal = await service.process_deal_result(id, payload.status, payload.won_lost_reason)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Deal status updated to: {payload.status}",
            data=deal
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
