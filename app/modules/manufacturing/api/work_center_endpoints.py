"""Work Centers and Machines API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)
from app.modules.manufacturing.models.work_center import Machine, WorkCenter
from app.modules.manufacturing.repositories.work_center_repository import WorkCenterRepository
from app.modules.manufacturing.schemas.work_center import (
    MachineCreate,
    MachineListResponse,
    MachineRead,
    MachineUpdate,
    WorkCenterCreate,
    WorkCenterRead,
    WorkCenterUpdate,
)

router = APIRouter(tags=["Manufacturing - Work Centers & Machines"])


class WorkCenterListResponse(BaseModel):
    items: list[WorkCenterRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/work-centers",
    response_model=WorkCenterListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
@router.get(
    "/work-centers/",
    response_model=WorkCenterListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
async def list_work_centers(
    work_center_type: str | None = None,
    wc_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkCenterListResponse:
    repo = WorkCenterRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_work_centers(
        tenant_id,
        org_id,
        work_center_type=work_center_type,
        status=wc_status,
        offset=offset,
        limit=page_size,
    )
    return WorkCenterListResponse(
        items=[WorkCenterRead.model_validate(w) for w in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/work-centers",
    response_model=WorkCenterRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
@router.post(
    "/work-centers/",
    response_model=WorkCenterRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
async def create_work_center(
    data: WorkCenterCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkCenterRead:
    repo = WorkCenterRepository(db)
    wc = WorkCenter(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code,
        name=data.name,
        work_center_type=data.work_center_type,
        capacity_per_day_hours=data.capacity_per_day_hours,
        cost_per_hour=data.cost_per_hour,
        overhead_cost_per_hour=data.overhead_cost_per_hour,
        location_id=data.location_id,
        status=data.status,
        is_active=data.is_active,
    )
    await repo.create_work_center(wc)
    created = await repo.get_work_center_by_id(wc.id, tenant_id, org_id)
    return WorkCenterRead.model_validate(created or wc)


@router.get(
    "/work-centers/{work_center_id}",
    response_model=WorkCenterRead,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
async def get_work_center(
    work_center_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkCenterRead:
    repo = WorkCenterRepository(db)
    wc = await repo.get_work_center_by_id(work_center_id, tenant_id, org_id)
    if not wc:
        raise NotFoundException(f"Work Center {work_center_id} not found.")
    return WorkCenterRead.model_validate(wc)


@router.put(
    "/work-centers/{work_center_id}",
    response_model=WorkCenterRead,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
async def update_work_center(
    work_center_id: uuid.UUID,
    data: WorkCenterUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkCenterRead:
    repo = WorkCenterRepository(db)
    wc = await repo.get_work_center_by_id(work_center_id, tenant_id, org_id)
    if not wc:
        raise NotFoundException(f"Work Center {work_center_id} not found.")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(wc, field, val)

    await db.flush()
    refreshed = await repo.get_work_center_by_id(work_center_id, tenant_id, org_id)
    return WorkCenterRead.model_validate(refreshed or wc)


@router.get(
    "/machines",
    response_model=MachineListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
@router.get(
    "/machines/",
    response_model=MachineListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
async def list_machines(
    work_center_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MachineListResponse:
    repo = WorkCenterRepository(db)
    offset = (page - 1) * page_size
    machines = await repo.list_machines(
        tenant_id, org_id, work_center_id=work_center_id, offset=offset, limit=page_size
    )
    return MachineListResponse(
        items=[MachineRead.model_validate(m) for m in machines],
        total=len(machines),
        page=page,
        page_size=page_size,
    )


@router.post(
    "/machines",
    response_model=MachineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
@router.post(
    "/machines/",
    response_model=MachineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
async def create_machine(
    data: MachineCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MachineRead:
    repo = WorkCenterRepository(db)
    machine = Machine(
        tenant_id=tenant_id,
        organization_id=org_id,
        work_center_id=data.work_center_id,
        code=data.code,
        name=data.name,
        serial_number=data.serial_number,
        hourly_cost=data.hourly_cost,
        status=data.status,
        last_maintenance_date=data.last_maintenance_date,
        next_maintenance_date=data.next_maintenance_date,
    )
    await repo.create_machine(machine)
    return MachineRead.model_validate(machine)


@router.get(
    "/machines/{machine_id}",
    response_model=MachineRead,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_READ.value))
    ],
)
async def get_machine(
    machine_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MachineRead:
    repo = WorkCenterRepository(db)
    machine = await repo.get_machine_by_id(machine_id, tenant_id, org_id)
    if not machine:
        raise NotFoundException(f"Machine {machine_id} not found.")
    return MachineRead.model_validate(machine)


@router.put(
    "/machines/{machine_id}",
    response_model=MachineRead,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_permission(PermissionCode.MANUFACTURING_WORK_CENTERS_WRITE.value))
    ],
)
async def update_machine(
    machine_id: uuid.UUID,
    data: MachineUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MachineRead:
    repo = WorkCenterRepository(db)
    machine = await repo.get_machine_by_id(machine_id, tenant_id, org_id)
    if not machine:
        raise NotFoundException(f"Machine {machine_id} not found.")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(machine, field, val)

    await db.flush()
    return MachineRead.model_validate(machine)
