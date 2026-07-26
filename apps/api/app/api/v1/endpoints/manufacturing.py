import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.manufacturing import (
    BillOfMaterial,
    Routing,
    WorkCenter,
    Machine,
    ProductionOrder,
    QualityInspection,
    MaintenanceRequest,
    MRPRun,
    ProductionLog,
)
from app.services.manufacturing_service import ManufacturingService
from app.schemas.manufacturing import (
    BOMCreate,
    BOMUpdate,
    BOMResponse,
    BOMCostRollupResponse,
    RoutingCreate,
    RoutingUpdate,
    RoutingResponse,
    WorkCenterCreate,
    WorkCenterUpdate,
    WorkCenterResponse,
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionOrderResponse,
    ProductionLogCreate,
    ProductionLogResponse,
    QualityInspectionCreate,
    QualityInspectionUpdate,
    QualityInspectionResponse,
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    MaintenanceRequestResponse,
    MRPRunCreate,
    MRPRunResponse,
    ManufacturingDashboardMetrics,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


async def get_mfg_service(db: AsyncSession = Depends(get_db_session)) -> ManufacturingService:
    return ManufacturingService(db)


# --- DASHBOARD ---
@router.get("/dashboard", response_model=APIResponse[ManufacturingDashboardMetrics])
async def get_manufacturing_dashboard(
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    metrics = await service.get_dashboard_metrics(current_user.organization_id)
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=metrics, message="Manufacturing dashboard metrics fetched successfully")


# --- BILL OF MATERIALS (BOM) ---
@router.get("/boms", response_model=APIResponse[List[BOMResponse]])
async def list_boms(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(BillOfMaterial).where(
        BillOfMaterial.organization_id == current_user.organization_id,
        BillOfMaterial.is_deleted == False,
    )
    if search:
        stmt = stmt.where(or_(BillOfMaterial.code.ilike(f"%{search}%"), BillOfMaterial.version.ilike(f"%{search}%")))
    
    stmt = stmt.order_by(desc(BillOfMaterial.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    boms = list(res.scalars().all())
    
    detailed_boms = []
    for b in boms:
        detailed_boms.append(await service.bom_repo.get_with_items(b.id))
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=detailed_boms, message="BOMs listed successfully")


@router.post("/boms", response_model=APIResponse[BOMResponse], status_code=status.HTTP_201_CREATED)
async def create_bom(
    data: BOMCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    bom = await service.create_bom(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=bom, message="Bill of Materials created successfully")


@router.get("/boms/{bom_id}", response_model=APIResponse[BOMResponse])
async def get_bom(
    bom_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    bom = await service.bom_repo.get_with_items(bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=bom, message="BOM retrieved successfully")


@router.post("/boms/{bom_id}/approve", response_model=APIResponse[BOMResponse])
async def approve_bom(
    bom_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    bom = await service.approve_bom(bom_id, current_user.id)
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=bom, message="BOM approved successfully")


@router.post("/boms/{bom_id}/cost-rollup", response_model=APIResponse[BOMCostRollupResponse])
async def calculate_bom_cost_rollup(
    bom_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    res = await service.calculate_cost_rollup(bom_id)
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=res, message="BOM Cost Rollup calculated successfully")


# --- ROUTINGS ---
@router.get("/routings", response_model=APIResponse[List[RoutingResponse]])
async def list_routings(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(Routing).where(
        Routing.organization_id == current_user.organization_id,
        Routing.is_deleted == False,
    )
    if search:
        stmt = stmt.where(or_(Routing.code.ilike(f"%{search}%"), Routing.name.ilike(f"%{search}%")))
    
    stmt = stmt.order_by(desc(Routing.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    routings = list(res.scalars().all())
    
    detailed = []
    for r in routings:
        detailed.append(await service.routing_repo.get_with_operations(r.id))
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=detailed, message="Routings listed successfully")


@router.post("/routings", response_model=APIResponse[RoutingResponse], status_code=status.HTTP_201_CREATED)
async def create_routing(
    data: RoutingCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    routing = await service.create_routing(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=routing, message="Manufacturing Routing created successfully")


@router.get("/routings/{routing_id}", response_model=APIResponse[RoutingResponse])
async def get_routing(
    routing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    routing = await service.routing_repo.get_with_operations(routing_id)
    if not routing:
        raise HTTPException(status_code=404, detail="Routing not found")
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=routing, message="Routing retrieved successfully")


# --- WORK CENTERS & MACHINES ---
@router.get("/work-centers", response_model=APIResponse[List[WorkCenterResponse]])
async def list_work_centers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(WorkCenter).where(
        WorkCenter.organization_id == current_user.organization_id,
        WorkCenter.is_deleted == False,
    )
    if search:
        stmt = stmt.where(or_(WorkCenter.code.ilike(f"%{search}%"), WorkCenter.name.ilike(f"%{search}%")))
    
    stmt = stmt.offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    wcs = list(res.scalars().all())
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=wcs, message="Work Centers listed successfully")


@router.post("/work-centers", response_model=APIResponse[WorkCenterResponse], status_code=status.HTTP_201_CREATED)
async def create_work_center(
    data: WorkCenterCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    wc = await service.create_work_center(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=wc, message="Work Center created successfully")


@router.get("/machines", response_model=APIResponse[List[MachineResponse]])
async def list_machines(
    work_center_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    stmt = select(Machine).where(Machine.is_deleted == False)
    if work_center_id:
        stmt = stmt.where(Machine.work_center_id == work_center_id)
    stmt = stmt.offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    machines = list(res.scalars().all())
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=machines, message="Machines listed successfully")


@router.post("/machines", response_model=APIResponse[MachineResponse], status_code=status.HTTP_201_CREATED)
async def create_machine(
    data: MachineCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    m = await service.create_machine(data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=m, message="Machine registered successfully")


# --- PRODUCTION ORDERS ---
@router.get("/production-orders", response_model=APIResponse[List[ProductionOrderResponse]])
async def list_production_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(ProductionOrder).where(
        ProductionOrder.organization_id == current_user.organization_id,
        ProductionOrder.is_deleted == False,
    )
    if status_filter:
        stmt = stmt.where(ProductionOrder.status == status_filter)
    
    stmt = stmt.order_by(desc(ProductionOrder.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    orders = list(res.scalars().all())
    
    detailed = []
    for o in orders:
        detailed.append(await service.order_repo.get_with_items(o.id))
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=detailed, message="Production orders retrieved successfully")


@router.post("/production-orders", response_model=APIResponse[ProductionOrderResponse], status_code=status.HTTP_201_CREATED)
async def create_production_order(
    data: ProductionOrderCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    po = await service.create_production_order(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=po, message="Production order scheduled successfully")


# --- SHOP FLOOR EXECUTION ---
@router.post("/shop-floor/logs", response_model=APIResponse[ProductionLogResponse], status_code=status.HTTP_201_CREATED)
async def log_shop_floor_production(
    data: ProductionLogCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    log = await service.log_production_output(data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=log, message="Shop floor production logged successfully")


# --- QUALITY CONTROL ---
@router.get("/quality/inspections", response_model=APIResponse[List[QualityInspectionResponse]])
async def list_quality_inspections(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(QualityInspection).where(
        QualityInspection.organization_id == current_user.organization_id,
        QualityInspection.is_deleted == False,
    ).order_by(desc(QualityInspection.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    inspections = list(res.scalars().all())
    
    detailed = []
    for i in inspections:
        detailed.append(await service.inspection_repo.get_with_results(i.id))
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=detailed, message="Quality inspections listed successfully")


@router.post("/quality/inspections", response_model=APIResponse[QualityInspectionResponse], status_code=status.HTTP_201_CREATED)
async def create_quality_inspection(
    data: QualityInspectionCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    insp = await service.create_quality_inspection(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=insp, message="Quality inspection recorded successfully")


# --- MAINTENANCE ---
@router.get("/maintenance/requests", response_model=APIResponse[List[MaintenanceRequestResponse]])
async def list_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.organization_id == current_user.organization_id,
        MaintenanceRequest.is_deleted == False,
    ).order_by(desc(MaintenanceRequest.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    reqs = list(res.scalars().all())
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=reqs, message="Maintenance requests retrieved successfully")


@router.post("/maintenance/requests", response_model=APIResponse[MaintenanceRequestResponse], status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
    data: MaintenanceRequestCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    req = await service.create_maintenance_request(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=req, message="Maintenance request filed successfully")


# --- MRP ENGINE ---
@router.get("/mrp/runs", response_model=APIResponse[List[MRPRunResponse]])
async def list_mrp_runs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    
    stmt = select(MRPRun).where(
        MRPRun.organization_id == current_user.organization_id,
        MRPRun.is_deleted == False,
    ).order_by(desc(MRPRun.created_at)).offset(skip).limit(limit)
    res = await service.db.execute(stmt)
    runs = list(res.scalars().all())
    return standard_json_response(status_code=status.HTTP_200_OK, success=True, data=runs, message="MRP runs fetched successfully")


@router.post("/mrp/runs", response_model=APIResponse[MRPRunResponse], status_code=status.HTTP_201_CREATED)
async def execute_mrp_run(
    data: MRPRunCreate,
    current_user: User = Depends(get_current_user),
    service: ManufacturingService = Depends(get_mfg_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User missing organization binding")
    mrp = await service.run_mrp(current_user.organization_id, data)
    return standard_json_response(status_code=status.HTTP_201_CREATED, success=True, data=mrp, message="Material Requirement Planning run completed successfully")
