"""Department API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.organization.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentTreeNode,
    DepartmentUpdate,
)
from app.modules.organization.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Department Management"])


@router.get(
    "/",
    response_model=list[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Departments",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_READ.value))],
)
async def list_departments(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentResponse]:
    """Lists all departments in active organization."""
    service = DepartmentService(db)
    depts = await service.list_departments(tenant_id, org_id, is_active)
    return [DepartmentResponse.model_validate(d) for d in depts]


@router.get(
    "/tree",
    response_model=list[DepartmentTreeNode],
    status_code=status.HTTP_200_OK,
    summary="Get Department Hierarchy Tree",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_READ.value))],
)
async def get_department_tree(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentTreeNode]:
    """Retrieves hierarchical department tree."""
    service = DepartmentService(db)
    return await service.get_department_tree(tenant_id, org_id)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Department",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_WRITE.value))],
)
async def create_department(
    req: DepartmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    """Creates a department within the active organization."""
    service = DepartmentService(db)
    dept = await service.create_department(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="DEPARTMENT_CREATED",
        description=f"Department '{dept.name}' ({dept.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return DepartmentResponse.model_validate(dept)


@router.get(
    "/{dept_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Department Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_READ.value))],
)
async def get_department(
    dept_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    """Retrieves department details enforcing tenant and org isolation."""
    service = DepartmentService(db)
    dept = await service.get_department(dept_id, tenant_id, org_id)
    return DepartmentResponse.model_validate(dept)


@router.put(
    "/{dept_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Department",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_WRITE.value))],
)
async def update_department(
    dept_id: uuid.UUID,
    req: DepartmentUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    """Updates department properties."""
    service = DepartmentService(db)
    dept = await service.update_department(dept_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="DEPARTMENT_UPDATED",
        description=f"Department '{dept.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return DepartmentResponse.model_validate(dept)


@router.delete(
    "/{dept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Department",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DEPARTMENTS_WRITE.value))],
)
async def delete_department(
    dept_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a department."""
    service = DepartmentService(db)
    await service.delete_department(dept_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="DEPARTMENT_DELETED",
        description=f"Department '{dept_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
