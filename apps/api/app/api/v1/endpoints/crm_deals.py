import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.crm_deal import Opportunity, Deal, Quotation, SalesOrder
from app.repositories.crm_mgmt import (
    OpportunityRepository,
    DealRepository,
    QuotationRepository,
    SalesOrderRepository,
)
from app.services.crm_mgmt import DealService, SalesOrderService
from app.schemas.crm_mgmt import (
    OpportunityResponse,
    OpportunityCreate,
    DealResponse,
    DealCreate,
    DealUpdate,
    QuotationCreate,
    QuotationResponse,
    QuotationStatusUpdate,
    SalesOrderResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_deal_service(db=Depends(get_db_session)):
    return DealService(DealRepository(db), QuotationRepository(db))

async def get_sales_order_service(db=Depends(get_db_session)):
    return SalesOrderService(SalesOrderRepository(db), QuotationRepository(db))

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

# 2. Quotation Endpoints
@router.get("/quotations", response_model=APIResponse[List[QuotationResponse]])
async def list_quotations(
    deal_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    repo = QuotationRepository(db)
    stmt = select(Quotation).where(Quotation.is_deleted == False)
    if deal_id:
        stmt = stmt.where(Quotation.deal_id == deal_id)
    res = await db.execute(stmt)
    quotes = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Quotations retrieved successfully",
        data=quotes
    )

@router.post("/quotations", response_model=APIResponse[QuotationResponse])
async def create_quotation(
    payload: QuotationCreate,
    db=Depends(get_db_session)
):
    repo = QuotationRepository(db)
    quote = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Quotation created successfully",
        data=quote
    )

@router.put("/quotations/{id}/status", response_model=APIResponse[QuotationResponse])
async def update_quotation_status(
    id: uuid.UUID,
    payload: QuotationStatusUpdate,
    db=Depends(get_db_session)
):
    repo = QuotationRepository(db)
    quote = await repo.get(id)
    if not quote or quote.is_deleted:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    updated = await repo.update(quote, {"status": payload.status})
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message=f"Quotation status updated to '{payload.status}'",
        data=updated
    )

@router.post("/quotations/{id}/convert-to-order", response_model=APIResponse[SalesOrderResponse])
async def convert_quotation_to_sales_order(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: SalesOrderService = Depends(get_sales_order_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    try:
        order = await service.convert_quotation_to_order(id, current_user.organization_id)
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Quotation converted to Sales Order successfully",
            data=order
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Sales Orders Endpoints
@router.get("/sales-orders", response_model=APIResponse[List[SalesOrderResponse]])
async def list_sales_orders(
    current_user: User = Depends(get_current_user),
    service: SalesOrderService = Depends(get_sales_order_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    orders = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Sales Orders retrieved successfully",
        data=orders
    )

# 4. CRM Summary Telemetry Endpoint
@router.get("/summary")
async def get_crm_summary(
    current_user: User = Depends(get_current_user),
    deal_service: DealService = Depends(get_deal_service),
    so_service: SalesOrderService = Depends(get_sales_order_service),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    deals = await deal_service.repository.get_by_org(current_user.organization_id)
    sales_orders = await so_service.repository.get_by_org(current_user.organization_id)

    total_pipeline_value = sum(float(d.amount) for d in deals if d.status == "pipeline")
    total_won_value = sum(float(d.amount) for d in deals if d.status == "won")
    total_sales_order_value = sum(float(so.total_amount) for so in sales_orders)

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="CRM Summary telemetry retrieved successfully",
        data={
            "total_deals": len(deals),
            "pipeline_deals": len([d for d in deals if d.status == "pipeline"]),
            "won_deals": len([d for d in deals if d.status == "won"]),
            "lost_deals": len([d for d in deals if d.status == "lost"]),
            "total_pipeline_value": total_pipeline_value,
            "total_won_value": total_won_value,
            "total_sales_orders": len(sales_orders),
            "total_sales_order_value": total_sales_order_value,
        }
    )

# 5. Deals Base & Parameterized Endpoints
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

@router.get("/{id}", response_model=APIResponse[DealResponse])
async def get_deal(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DealService = Depends(get_deal_service)
):
    deal = await service.repository.get(id)
    if not deal or deal.organization_id != current_user.organization_id or deal.is_deleted:
        raise HTTPException(status_code=404, detail="Deal not found")

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Deal details retrieved",
        data=deal
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
