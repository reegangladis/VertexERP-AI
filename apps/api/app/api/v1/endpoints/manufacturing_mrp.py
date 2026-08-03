import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.manufacturing_mrp import (
    BOMRepository,
    MachineRepository,
    ProductionOrderRepository,
    QualityInspectionRepository,
    WorkCenterRepository,
)
from app.schemas.manufacturing_mrp import (
    BOMCreate,
    BOMResponse,
    MachineCreate,
    MachineMaintenanceCreate,
    MachineMaintenanceResponse,
    MachineResponse,
    ManufacturingDashboardSummary,
    MRPRunCreate,
    MRPRunResponse,
    ProductionOrderCreate,
    ProductionOrderResponse,
    QualityInspectionCreate,
    QualityInspectionResponse,
    WorkCenterCreate,
    WorkCenterResponse,
)
from app.services.manufacturing_mrp import (
    BOMEngine,
    MachineMaintenanceService,
    ManufacturingAnalyticsService,
    MRPEngine,
    ProductionPlanningEngine,
    QualityService,
    WorkCenterService,
)

router = APIRouter()


# --- BOM Endpoints ---
@router.post("/manufacturing/bom", response_model=BOMResponse, status_code=status.HTTP_201_CREATED)
async def create_bom(
    payload: BOMCreate,
    current_user: User = Depends(PermissionChecker("bom.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = BOMEngine(db)
    return await engine.create_bom(payload)


@router.get("/manufacturing/bom", response_model=list[BOMResponse])
async def list_boms(
    product_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = BOMRepository(db)
    records, _ = await repo.get_multi(filters={"product_id": product_id} if product_id else None)
    return records


# --- Production Orders ---
@router.post("/manufacturing/production-orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    payload: ProductionOrderCreate,
    current_user: User = Depends(PermissionChecker("production.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = ProductionPlanningEngine(db)
    return await engine.create_production_order(payload)


@router.get("/manufacturing/production-orders", response_model=list[ProductionOrderResponse])
async def list_production_orders(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ProductionOrderRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/manufacturing/production-orders/{id}/start", response_model=ProductionOrderResponse)
async def start_production_order(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("production.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = ProductionPlanningEngine(db)
    return await engine.start_production_order(id)


@router.post("/manufacturing/production-orders/{id}/complete", response_model=ProductionOrderResponse)
async def complete_production_order(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("production.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = ProductionPlanningEngine(db)
    return await engine.complete_production_order(id)


@router.post("/manufacturing/production-orders/{id}/cancel", response_model=ProductionOrderResponse)
async def cancel_production_order(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("production.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = ProductionPlanningEngine(db)
    return await engine.cancel_production_order(id)


# --- Work Centers & Machines ---
@router.post("/manufacturing/work-centers", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    payload: WorkCenterCreate,
    current_user: User = Depends(PermissionChecker("manufacturing.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = WorkCenterService(db)
    return await service.create_work_center(payload)


@router.get("/manufacturing/work-centers", response_model=list[WorkCenterResponse])
async def list_work_centers(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = WorkCenterRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/manufacturing/machines", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    payload: MachineCreate,
    current_user: User = Depends(PermissionChecker("machine.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = WorkCenterService(db)
    return await service.create_machine(payload)


@router.get("/manufacturing/machines", response_model=list[MachineResponse])
async def list_machines(
    work_center_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = MachineRepository(db)
    records, _ = await repo.get_multi(filters={"work_center_id": work_center_id} if work_center_id else None)
    return records


@router.post("/manufacturing/maintenance", response_model=MachineMaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def schedule_maintenance(
    payload: MachineMaintenanceCreate,
    current_user: User = Depends(PermissionChecker("machine.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = MachineMaintenanceService(db)
    return await service.schedule_maintenance(payload)


# --- Quality Inspections ---
@router.post("/manufacturing/quality", response_model=QualityInspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_quality_inspection(
    payload: QualityInspectionCreate,
    current_user: User = Depends(PermissionChecker("quality.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = QualityService(db)
    return await service.create_inspection(payload)


@router.get("/manufacturing/quality", response_model=list[QualityInspectionResponse])
async def list_quality_inspections(
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = QualityInspectionRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- MRP Runs ---
@router.post("/manufacturing/mrp/run", response_model=MRPRunResponse)
async def run_mrp(
    payload: MRPRunCreate,
    current_user: User = Depends(PermissionChecker("mrp.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = MRPEngine(db)
    return await engine.run_mrp_planning(payload)


# --- Dashboard Summary ---
@router.get("/manufacturing/dashboard", response_model=ManufacturingDashboardSummary)
async def get_manufacturing_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("manufacturing.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = ManufacturingAnalyticsService(db)
    return await service.get_dashboard_summary(org_id)
