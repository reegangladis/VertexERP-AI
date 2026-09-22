"""Employee API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.modules.hr.services.employee_service import EmployeeService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/employees", tags=["HR Employee Directory"])


@router.get(
    "/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employees",
    dependencies=[Depends(require_permission(PermissionCode.HR_EMPLOYEES_READ.value))],
)
async def list_employees(
    department_id: uuid.UUID | None = None,
    branch_id: uuid.UUID | None = None,
    designation_id: uuid.UUID | None = None,
    employment_status: str | None = None,
    is_active: bool | None = None,
    search: str | None = Query(None, description="Search by name, email, or employee number"),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmployeeResponse]:
    """List all employees in the active organization with filtering."""
    service = EmployeeService(db)
    employees = await service.list_employees(
        tenant_id=tenant_id,
        org_id=org_id,
        department_id=department_id,
        branch_id=branch_id,
        designation_id=designation_id,
        status=employment_status,
        is_active=is_active,
        search=search,
    )
    return [EmployeeResponse.model_validate(e) for e in employees]


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee",
    dependencies=[Depends(require_permission(PermissionCode.HR_EMPLOYEES_WRITE.value))],
)
async def create_employee(
    req: EmployeeCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Creates a new employee master record."""
    service = EmployeeService(db)
    employee = await service.create_employee(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_EMPLOYEE_CREATED",
        description=f"Employee '{employee.first_name} {employee.last_name}' ({employee.employee_number}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return EmployeeResponse.model_validate(employee)


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Details",
    dependencies=[Depends(require_permission(PermissionCode.HR_EMPLOYEES_READ.value))],
)
async def get_employee(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Retrieves detailed employee information enforcing tenant and organization isolation."""
    service = EmployeeService(db)
    employee = await service.get_employee(employee_id, tenant_id, org_id)
    return EmployeeResponse.model_validate(employee)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Employee",
    dependencies=[Depends(require_permission(PermissionCode.HR_EMPLOYEES_WRITE.value))],
)
async def update_employee(
    employee_id: uuid.UUID,
    req: EmployeeUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Updates employee master data."""
    service = EmployeeService(db)
    employee = await service.update_employee(employee_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_EMPLOYEE_UPDATED",
        description=f"Employee '{employee.employee_number}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return EmployeeResponse.model_validate(employee)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee",
    dependencies=[Depends(require_permission(PermissionCode.HR_EMPLOYEES_DELETE.value))],
)
async def delete_employee(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes an employee."""
    service = EmployeeService(db)
    await service.delete_employee(employee_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_EMPLOYEE_DELETED",
        description=f"Employee '{employee_id}' soft-deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
