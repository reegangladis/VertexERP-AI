from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.inventory_mgmt import InventoryCountRepository
from app.schemas.inventory_mgmt import InventoryCountCreate, InventoryCountResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


@router.get("", response_model=APIResponse[list[InventoryCountResponse]])
async def list_counts(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = InventoryCountRepository(db)
    counts = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Inventory count audits retrieved successfully",
        data=counts,
    )


@router.post("", response_model=APIResponse[InventoryCountResponse])
async def create_count(
    payload: InventoryCountCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = InventoryCountRepository(db)
    count_obj = await repo.create(
        {
            "organization_id": current_user.organization_id,
            "warehouse_id": payload.warehouse_id,
            "status": "in_progress",
        }
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Inventory count audit session started",
        data=count_obj,
    )
