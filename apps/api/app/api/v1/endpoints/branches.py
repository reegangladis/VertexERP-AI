import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.branch import BranchRepository
from app.schemas.branch import BranchCreate, BranchResponse, BranchUpdate
from app.services.branch_service import BranchService

router = APIRouter()


def get_branch_service(
    db: AsyncSession = Depends(get_db_session),
) -> BranchService:
    return BranchService(BranchRepository(db))


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    data: BranchCreate,
    service: BranchService = Depends(get_branch_service),
):
    return await service.create(data)


@router.get("", response_model=list[BranchResponse])
async def list_branches(
    organization_id: uuid.UUID | None = None,
    service: BranchService = Depends(get_branch_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi()
    return items


@router.get("/{id}", response_model=BranchResponse)
async def get_branch(
    id: uuid.UUID,
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.get(id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found"
        )
    return branch


@router.put("/{id}", response_model=BranchResponse)
async def update_branch(
    id: uuid.UUID,
    data: BranchUpdate,
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.update(id, data)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found"
        )
    return branch


@router.delete("/{id}", response_model=BranchResponse)
async def delete_branch(
    id: uuid.UUID,
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.delete(id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found"
        )
    return branch
