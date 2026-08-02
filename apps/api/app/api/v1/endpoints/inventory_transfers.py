import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.inventory_mgmt import (
    InventoryTransactionRepository,
    StockLevelRepository,
    StockMovementRepository,
    StockTransferItemRepository,
    StockTransferRepository,
)
from app.schemas.inventory_mgmt import (
    InterWarehouseTransferCreate,
    InterWarehouseTransferResponse,
    StockMovementResponse,
    StockTransferCreate,
)
from app.schemas.response import APIResponse
from app.services.inventory_mgmt import StockMovementService, StockTransferService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_movement_service(db=Depends(get_db_session)):
    return StockMovementService(
        StockMovementRepository(db),
        StockLevelRepository(db),
        InventoryTransactionRepository(db),
    )


async def get_transfer_service(db=Depends(get_db_session)):
    return StockTransferService(
        StockTransferRepository(db),
        StockTransferItemRepository(db),
        StockLevelRepository(db),
        InventoryTransactionRepository(db),
    )


# 1. Intra-Bin Stock Movements
@router.get("", response_model=APIResponse[list[StockMovementResponse]])
async def list_transfers(
    current_user: User = Depends(get_current_user),
    service: StockMovementService = Depends(get_movement_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    transfers = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Stock movements retrieved successfully",
        data=transfers,
    )


@router.post("", response_model=APIResponse[StockMovementResponse])
async def create_stock_transfer(
    payload: StockTransferCreate,
    current_user: User = Depends(get_current_user),
    service: StockMovementService = Depends(get_movement_service),
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
            payload.quantity,
        )
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Stock transfer completed successfully",
            data=movement,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# 2. Inter-Warehouse Transfers
@router.get(
    "/inter-warehouse", response_model=APIResponse[list[InterWarehouseTransferResponse]]
)
async def list_inter_warehouse_transfers(
    current_user: User = Depends(get_current_user),
    service: StockTransferService = Depends(get_transfer_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    transfers = await service.repository.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Inter-warehouse stock transfers retrieved successfully",
        data=transfers,
    )


@router.post(
    "/inter-warehouse", response_model=APIResponse[InterWarehouseTransferResponse]
)
async def create_inter_warehouse_transfer(
    payload: InterWarehouseTransferCreate,
    current_user: User = Depends(get_current_user),
    service: StockTransferService = Depends(get_transfer_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        items_dict = [i.dict() for i in payload.items]
        transfer = await service.create_transfer(
            current_user.organization_id,
            payload.source_warehouse_id,
            payload.target_warehouse_id,
            items_dict,
            current_user.id,
        )
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Inter-warehouse stock transfer initiated",
            data=transfer,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put(
    "/inter-warehouse/{id}/approve",
    response_model=APIResponse[InterWarehouseTransferResponse],
)
async def approve_inter_warehouse_transfer(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StockTransferService = Depends(get_transfer_service),
):
    try:
        transfer = await service.approve_transfer(id, current_user.id)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Inter-warehouse stock transfer {transfer.transfer_number} approved & executed",
            data=transfer,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
