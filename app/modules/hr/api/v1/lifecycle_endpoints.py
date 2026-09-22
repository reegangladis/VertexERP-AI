"""Employment Contracts, Lifecycle, and Onboarding API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.lifecycle import (
    EmploymentContractCreate,
    EmploymentContractResponse,
    EmploymentContractUpdate,
    LifecycleEventCreate,
    LifecycleEventResponse,
    OnboardingTaskCreate,
    OnboardingTaskResponse,
    OnboardingTaskUpdate,
)
from app.modules.hr.services.lifecycle_service import LifecycleService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/lifecycle", tags=["HR Employment Lifecycle & Contracts"])


# --------------------------------------------------------------------------
# Contracts
# --------------------------------------------------------------------------
@router.post(
    "/contracts",
    response_model=EmploymentContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employment Contract",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_WRITE.value))],
)
async def create_contract(
    req: EmploymentContractCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmploymentContractResponse:
    """Issues a new employment contract."""
    service = LifecycleService(db)
    contract = await service.create_contract(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_CONTRACT_CREATED",
        description=f"Contract '{contract.contract_number}' issued for employee '{contract.employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return EmploymentContractResponse.model_validate(contract)


@router.get(
    "/contracts/employee/{employee_id}",
    response_model=list[EmploymentContractResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Contracts",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_READ.value))],
)
async def list_employee_contracts(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmploymentContractResponse]:
    """Retrieves all contracts for an employee."""
    service = LifecycleService(db)
    contracts = await service.list_contracts_for_employee(employee_id, tenant_id, org_id)
    return [EmploymentContractResponse.model_validate(c) for c in contracts]


@router.put(
    "/contracts/{contract_id}",
    response_model=EmploymentContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Contract",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_WRITE.value))],
)
async def update_contract(
    contract_id: uuid.UUID,
    req: EmploymentContractUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmploymentContractResponse:
    """Updates contract terms and status."""
    service = LifecycleService(db)
    contract = await service.update_contract(contract_id, tenant_id, org_id, req)
    return EmploymentContractResponse.model_validate(contract)


# --------------------------------------------------------------------------
# Lifecycle Events
# --------------------------------------------------------------------------
@router.post(
    "/events",
    response_model=LifecycleEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Lifecycle Event",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_WRITE.value))],
)
async def record_lifecycle_event(
    req: LifecycleEventCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LifecycleEventResponse:
    """Records an immutable lifecycle event."""
    service = LifecycleService(db)
    event = await service.record_lifecycle_event(tenant_id, org_id, current_user.id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_LIFECYCLE_EVENT_RECORDED",
        description=f"Lifecycle event '{event.event_type}' recorded for employee '{event.employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return LifecycleEventResponse.model_validate(event)


@router.get(
    "/events/employee/{employee_id}",
    response_model=list[LifecycleEventResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Lifecycle Events",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_READ.value))],
)
async def list_employee_events(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LifecycleEventResponse]:
    """Retrieves full career timeline for an employee."""
    service = LifecycleService(db)
    events = await service.list_lifecycle_events(employee_id, tenant_id, org_id)
    return [LifecycleEventResponse.model_validate(e) for e in events]


# --------------------------------------------------------------------------
# Onboarding Tasks
# --------------------------------------------------------------------------
@router.post(
    "/onboarding/tasks",
    response_model=OnboardingTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Onboarding Task",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_WRITE.value))],
)
async def create_onboarding_task(
    req: OnboardingTaskCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    """Creates an onboarding / offboarding task."""
    service = LifecycleService(db)
    task = await service.create_onboarding_task(tenant_id, org_id, req)
    return OnboardingTaskResponse.model_validate(task)


@router.get(
    "/onboarding/tasks/employee/{employee_id}",
    response_model=list[OnboardingTaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Onboarding Tasks",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_READ.value))],
)
async def list_employee_tasks(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[OnboardingTaskResponse]:
    """Lists all checklist tasks for an employee."""
    service = LifecycleService(db)
    tasks = await service.list_onboarding_tasks(employee_id, tenant_id, org_id)
    return [OnboardingTaskResponse.model_validate(t) for t in tasks]


@router.put(
    "/onboarding/tasks/{task_id}",
    response_model=OnboardingTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Onboarding Task Status",
    dependencies=[Depends(require_permission(PermissionCode.HR_LIFECYCLE_WRITE.value))],
)
async def update_onboarding_task(
    task_id: uuid.UUID,
    req: OnboardingTaskUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    """Updates task status / marks task completed."""
    service = LifecycleService(db)
    task = await service.update_onboarding_task(task_id, tenant_id, org_id, req)
    return OnboardingTaskResponse.model_validate(task)
