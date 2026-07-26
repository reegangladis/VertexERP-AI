import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_purchase import PurchaseOrder, PurchaseOrderItem
from app.repositories.inventory_mgmt import (
    PurchaseOrderRepository,
    GoodsReceiptRepository,
    StockLevelRepository,
    InventoryTransactionRepository,
    PurchaseOrderItemRepository,
)
from app.services.inventory_mgmt import PurchaseOrderService
from app.schemas.inventory_mgmt import PurchaseOrderResponse, PurchaseOrderCreate, GoodsReceiptResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_po_service(db=Depends(get_db_session)):
    return PurchaseOrderService(
        PurchaseOrderRepository(db),
        GoodsReceiptRepository(db),
        StockLevelRepository(db),
        InventoryTransactionRepository(db)
    )

@router.get("", response_model=APIResponse[List[PurchaseOrderResponse]])
async def list_purchase_orders(
    current_user: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    pos = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Purchase orders retrieved successfully",
        data=pos
    )

@router.post("", response_model=APIResponse[PurchaseOrderResponse])
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    current_user: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    total = sum(i.quantity * i.unit_price for i in payload.items)
    
    po = await service.repository.create({
        "organization_id": current_user.organization_id,
        "supplier_id": payload.supplier_id,
        "po_number": payload.po_number,
        "status": "draft",
        "total_amount": total
    })

    item_repo = PurchaseOrderItemRepository(service.repository.db)
    for it in payload.items:
        await item_repo.create({
            "purchase_order_id": po.id,
            "product_id": it.product_id,
            "quantity": it.quantity,
            "unit_price": it.unit_price
        })

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Purchase Order created successfully",
        data=po
    )

@router.post("/{id}/receive", response_model=APIResponse[GoodsReceiptResponse])
async def receive_purchase_order_goods(
    id: uuid.UUID,
    warehouse_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service)
):
    try:
        grn = await service.receive_goods(id, current_user.id, warehouse_id)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Goods received under GRN: {grn.grn_number}",
            data=grn
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
