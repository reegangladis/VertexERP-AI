import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.department import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentTreeNode, DepartmentUpdate
from app.services.department import DepartmentService

router = APIRouter()


def get_department_service(db: AsyncSession = Depends(get_db_session)) -> DepartmentService:
    return DepartmentService(DepartmentRepository(db))


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    current_user: User = Depends(PermissionChecker("department.create")),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.create_department(data)


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("department.read")),
    service: DepartmentService = Depends(get_department_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/tree", response_model=list[DepartmentTreeNode])
async def get_department_tree(
    org_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("department.read")),
    service: DepartmentService = Depends(get_department_service),
):
    target_org_id = org_id or current_user.organization_id
    if not target_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID required"
        )
    return await service.get_department_tree(target_org_id)


@router.get("/{id}", response_model=DepartmentResponse)
async def get_department(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("department.read")),
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.get(id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    return dept


@router.patch("/{id}", response_model=DepartmentResponse)
async def update_department(
    id: uuid.UUID,
    data: DepartmentUpdate,
    current_user: User = Depends(PermissionChecker("department.update")),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.update_department(id, data)


@router.delete("/{id}", response_model=DepartmentResponse)
async def delete_department(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("department.delete")),
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.delete(id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    return dept
