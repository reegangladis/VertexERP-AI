import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_warehouse import Warehouse, WarehouseBin, StockLevel
from app.repositories.inventory_mgmt import WarehouseRepository, WarehouseBinRepository, StockLevelRepository
from app.schemas.inventory_mgmt import (
    WarehouseResponse,
    WarehouseCreate,
    WarehouseBinResponse,
    WarehouseBinCreate,
    StockLevelResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

# 1. Warehouse CRUD
@router.get("", response_model=APIResponse[List[WarehouseResponse]])
async def list_warehouses(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = WarehouseRepository(db)
    warehouses = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Warehouses retrieved successfully",
        data=warehouses
    )

@router.post("", response_model=APIResponse[WarehouseResponse])
async def create_warehouse(
    payload: WarehouseCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = WarehouseRepository(db)
    warehouse = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Warehouse registered successfully",
        data=warehouse
    )

# 2. Bins Endpoints
@router.get("/bins", response_model=APIResponse[List[WarehouseBinResponse]])
async def list_bins(
    warehouse_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = WarehouseBinRepository(db)
    stmt = select(WarehouseBin).where(WarehouseBin.is_deleted == False)
    if warehouse_id:
        stmt = stmt.where(WarehouseBin.warehouse_id == warehouse_id)
    res = await db.execute(stmt)
    bins = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Warehouse bins retrieved successfully",
        data=bins
    )

@router.post("/bins", response_model=APIResponse[WarehouseBinResponse])
async def create_bin(
    payload: WarehouseBinCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    repo = WarehouseBinRepository(db)
    bin_obj = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Warehouse bin coordinate logged successfully",
        data=bin_obj
    )

# 3. Stock Levels
@router.get("/stock-levels", response_model=APIResponse[List[StockLevelResponse]])
async def list_stock_levels(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = StockLevelRepository(db)
    levels = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Stock levels retrieved successfully",
        data=levels
    )
