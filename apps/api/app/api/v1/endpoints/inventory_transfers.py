import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_transaction import StockMovement
from app.repositories.inventory_mgmt import StockMovementRepository, StockLevelRepository, InventoryTransactionRepository
from app.services.inventory_mgmt import StockMovementService
from app.schemas.inventory_mgmt import StockMovementResponse, StockTransferCreate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_transfer_service(db=Depends(get_db_session)):
    return StockMovementService(
        StockMovementRepository(db),
        StockLevelRepository(db),
        InventoryTransactionRepository(db)
    )

@router.get("", response_model=APIResponse[List[StockMovementResponse]])
async def list_transfers(
    current_user: User = Depends(get_current_user),
    service: StockMovementService = Depends(get_transfer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    transfers = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Stock movements retrieved successfully",
        data=transfers
    )

@router.post("", response_model=APIResponse[StockMovementResponse])
async def create_stock_transfer(
    payload: StockTransferCreate,
    current_user: User = Depends(get_current_user),
    service: StockMovementService = Depends(get_transfer_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        movement = await service.transfer_stock(
            current_user.organization_id,
            payload.product_id,
            payload.warehouse_id,
            payload.from_bin_id,
            payload.to_bin_id,
            payload.quantity
        )
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Stock transfer completed successfully",
            data=movement
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
