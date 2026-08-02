from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.inventory_mgmt import InventoryAdjustmentRepository
from app.schemas.inventory_mgmt import (
    InventoryAdjustmentCreate,
    InventoryAdjustmentResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


@router.get("", response_model=APIResponse[list[InventoryAdjustmentResponse]])
async def list_adjustments(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = InventoryAdjustmentRepository(db)
    adjustments = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Inventory adjustments retrieved successfully",
        data=adjustments,
    )


@router.post("", response_model=APIResponse[InventoryAdjustmentResponse])
async def create_adjustment(
    payload: InventoryAdjustmentCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = InventoryAdjustmentRepository(db)
    adjustment = await repo.create(
        {
            "organization_id": current_user.organization_id,
            "warehouse_id": payload.warehouse_id,
            "adjusted_by_id": current_user.id,
            "status": payload.status,
        }
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Inventory adjustment registered successfully",
        data=adjustment,
    )
