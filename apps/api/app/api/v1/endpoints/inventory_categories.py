import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_product import ProductCategory
from app.repositories.inventory_mgmt import ProductCategoryRepository
from app.schemas.inventory_mgmt import ProductCategoryResponse, ProductCategoryCreate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

@router.get("", response_model=APIResponse[List[ProductCategoryResponse]])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = ProductCategoryRepository(db)
    categories = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Categories retrieved successfully",
        data=categories
    )

@router.post("", response_model=APIResponse[ProductCategoryResponse])
async def create_category(
    payload: ProductCategoryCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = ProductCategoryRepository(db)
    category = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Product category registered successfully",
        data=category
    )
