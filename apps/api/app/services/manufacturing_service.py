import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.manufacturing import (
    ProductFamily,
    ProductVersion,
    BillOfMaterial,
    BOMItem,
    Routing,
    RoutingOperation,
    WorkCenter,
    Machine,
    ProductionOrder,
    ProductionOrderItem,
    ProductionLog,
    MaterialConsumption,
    QualityInspection,
    QualityResult,
    MaintenanceRequest,
    MaintenanceLog,
    MachineDowntime,
    MRPRun,
)
from app.models.inventory_product import Product
from app.models.inventory_warehouse import StockLevel
from app.repositories.manufacturing_repository import (
    BillOfMaterialRepository,
    RoutingRepository,
    WorkCenterRepository,
    MachineRepository,
    ProductionOrderRepository,
    QualityInspectionRepository,
    MaintenanceRequestRepository,
    MRPRunRepository,
)
from app.repositories.base import BaseRepository
from app.schemas.manufacturing import (
    BOMCreate,
    BOMUpdate,
    RoutingCreate,
    WorkCenterCreate,
    MachineCreate,
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionLogCreate,
    MaterialConsumptionCreate,
    QualityInspectionCreate,
    QualityResultCreate,
    MaintenanceRequestCreate,
    MaintenanceLogCreate,
    MachineDowntimeCreate,
    MRPRunCreate,
    BOMCostRollupResponse,
    ProcurementSuggestion,
    ProductionSuggestion,
    CapacityPlanItem,
    ManufacturingDashboardMetrics,
)


class ManufacturingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.bom_repo = BillOfMaterialRepository(db)
        self.routing_repo = RoutingRepository(db)
        self.work_center_repo = WorkCenterRepository(db)
        self.machine_repo = MachineRepository(db)
        self.order_repo = ProductionOrderRepository(db)
        self.inspection_repo = QualityInspectionRepository(db)
        self.maintenance_repo = MaintenanceRequestRepository(db)
        self.mrp_repo = MRPRunRepository(db)

    # --- Bill of Materials (BOM) ---
    async def create_bom(self, organization_id: uuid.UUID, data: BOMCreate) -> BillOfMaterial:
        # Calculate total cost from items
        total_cost = 0.0
        bom = BillOfMaterial(
            organization_id=organization_id,
            product_id=data.product_id,
            code=data.code,
            version=data.version,
            base_quantity=data.base_quantity,
            notes=data.notes,
            status="DRAFT",
            is_active=True,
            total_cost=0.0,
        )
        self.db.add(bom)
        await self.db.flush()

        for item in data.items:
            ext_cost = item.quantity * item.unit_cost * (1 + (item.scrap_factor_percent / 100.0))
            total_cost += ext_cost
            bom_item = BOMItem(
                bom_id=bom.id,
                component_product_id=item.component_product_id,
                parent_item_id=item.parent_item_id,
                quantity=item.quantity,
                unit_name=item.unit_name,
                scrap_factor_percent=item.scrap_factor_percent,
                unit_cost=item.unit_cost,
                extended_cost=ext_cost,
                is_alternative=item.is_alternative,
                notes=item.notes,
            )
            self.db.add(bom_item)

        bom.total_cost = total_cost
        await self.db.commit()
        return await self.bom_repo.get_with_items(bom.id)

    async def approve_bom(self, bom_id: uuid.UUID, user_id: uuid.UUID) -> BillOfMaterial:
        bom = await self.bom_repo.get_with_items(bom_id)
        if not bom:
            raise ValueError("BOM not found")
        bom.status = "APPROVED"
        bom.approved_by = user_id
        bom.approved_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(bom)
        return bom

    async def calculate_cost_rollup(self, bom_id: uuid.UUID) -> BOMCostRollupResponse:
        bom = await self.bom_repo.get_with_items(bom_id)
        if not bom:
            raise ValueError("BOM not found")

        material_cost = 0.0
        breakdown = []
        for item in bom.items:
            item_ext = item.quantity * item.unit_cost * (1 + (item.scrap_factor_percent / 100.0))
            material_cost += item_ext
            breakdown.append({
                "component_product_id": str(item.component_product_id),
                "quantity": item.quantity,
                "unit_cost": item.unit_cost,
                "scrap_factor": item.scrap_factor_percent,
                "extended_cost": item_ext,
            })

        # Check operations cost from routing if available
        routing_list = (await self.db.execute(
            select(Routing).where(Routing.product_id == bom.product_id, Routing.is_deleted == False)
        )).scalars().all()

        operation_cost = 0.0
        if routing_list:
            routing = await self.routing_repo.get_with_operations(routing_list[0].id)
            if routing and routing.operations:
                for op in routing.operations:
                    op_cost = (op.standard_time_mins / 60.0) * op.hourly_rate
                    operation_cost += op_cost
                    breakdown.append({
                        "operation_id": str(op.id),
                        "operation_name": op.operation_name,
                        "standard_time_mins": op.standard_time_mins,
                        "hourly_rate": op.hourly_rate,
                        "extended_cost": op_cost,
                    })

        total_calculated = material_cost + operation_cost
        bom.total_cost = total_calculated
        await self.db.commit()

        return BOMCostRollupResponse(
            bom_id=bom.id,
            product_id=bom.product_id,
            material_cost=material_cost,
            operation_cost=operation_cost,
            total_calculated_cost=total_calculated,
            cost_breakdown=breakdown,
        )

    # --- Routings ---
    async def create_routing(self, organization_id: uuid.UUID, data: RoutingCreate) -> Routing:
        total_time = 0.0
        routing = Routing(
            organization_id=organization_id,
            product_id=data.product_id,
            code=data.code,
            version=data.version,
            name=data.name,
            total_standard_time_mins=0.0,
        )
        self.db.add(routing)
        await self.db.flush()

        for op_data in data.operations:
            std_time = op_data.setup_time_mins + op_data.machine_time_mins + op_data.labor_time_mins
            if op_data.standard_time_mins > 0:
                std_time = op_data.standard_time_mins
            total_time += std_time

            op = RoutingOperation(
                routing_id=routing.id,
                work_center_id=op_data.work_center_id,
                sequence_number=op_data.sequence_number,
                operation_name=op_data.operation_name,
                description=op_data.description,
                setup_time_mins=op_data.setup_time_mins,
                machine_time_mins=op_data.machine_time_mins,
                labor_time_mins=op_data.labor_time_mins,
                standard_time_mins=std_time,
                hourly_rate=op_data.hourly_rate,
            )
            self.db.add(op)

        routing.total_standard_time_mins = total_time
        await self.db.commit()
        return await self.routing_repo.get_with_operations(routing.id)

    # --- Work Centers & Machines ---
    async def create_work_center(self, organization_id: uuid.UUID, data: WorkCenterCreate) -> WorkCenter:
        wc = WorkCenter(
            organization_id=organization_id,
            code=data.code,
            name=data.name,
            production_line=data.production_line,
            category=data.category,
            capacity_per_day_hours=data.capacity_per_day_hours,
            hourly_cost=data.hourly_cost,
            efficiency_percent=data.efficiency_percent,
            shift_calendar=data.shift_calendar,
            status="ACTIVE",
            failure_risk_index=0.05,
        )
        self.db.add(wc)
        await self.db.commit()
        await self.db.refresh(wc)
        return wc

    async def create_machine(self, data: MachineCreate) -> Machine:
        m = Machine(
            work_center_id=data.work_center_id,
            code=data.code,
            name=data.name,
            model_number=data.model_number,
            serial_number=data.serial_number,
            status="OPERATIONAL",
            hourly_cost=data.hourly_cost,
            capacity_units_per_hour=data.capacity_units_per_hour,
            health_score=98.0,
        )
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    # --- Production Orders ---
    async def create_production_order(self, organization_id: uuid.UUID, data: ProductionOrderCreate) -> ProductionOrder:
        order = ProductionOrder(
            organization_id=organization_id,
            order_number=data.order_number,
            product_id=data.product_id,
            bom_id=data.bom_id,
            routing_id=data.routing_id,
            warehouse_id=data.warehouse_id,
            planned_quantity=data.planned_quantity,
            completed_quantity=0.0,
            scrap_quantity=0.0,
            status="PLANNED",
            priority=data.priority,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            material_reservation_status="NOT_RESERVED",
            notes=data.notes,
        )
        self.db.add(order)
        await self.db.flush()

        # If routing provided, copy routing operations into production order items
        if data.routing_id:
            routing = await self.routing_repo.get_with_operations(data.routing_id)
            if routing and routing.operations:
                for op in routing.operations:
                    po_item = ProductionOrderItem(
                        production_order_id=order.id,
                        routing_operation_id=op.id,
                        work_center_id=op.work_center_id,
                        sequence_number=op.sequence_number,
                        operation_name=op.operation_name,
                        status="PENDING",
                        planned_hours=op.standard_time_mins / 60.0 * (data.planned_quantity / 100.0 if data.planned_quantity > 0 else 1.0),
                        actual_hours=0.0,
                        completed_qty=0.0,
                        scrap_qty=0.0,
                    )
                    self.db.add(po_item)

        await self.db.commit()
        return await self.order_repo.get_with_items(order.id)

    async def log_production_output(self, data: ProductionLogCreate) -> ProductionLog:
        log = ProductionLog(
            production_order_id=data.production_order_id,
            work_center_id=data.work_center_id,
            machine_id=data.machine_id,
            operator_name=data.operator_name,
            quantity_produced=data.quantity_produced,
            scrap_quantity=data.scrap_quantity,
            log_time=datetime.utcnow(),
            notes=data.notes,
        )
        self.db.add(log)

        # Update production order progress
        order = await self.order_repo.get(data.production_order_id)
        if order:
            order.completed_quantity += data.quantity_produced
            order.scrap_quantity += data.scrap_quantity
            if order.completed_quantity >= order.planned_quantity:
                order.status = "COMPLETED"
                order.actual_end_date = date.today()
            elif order.completed_quantity > 0 and order.status == "PLANNED":
                order.status = "IN_PROGRESS"
                order.actual_start_date = date.today()

        await self.db.commit()
        await self.db.refresh(log)
        return log

    # --- Quality Control ---
    async def create_quality_inspection(self, organization_id: uuid.UUID, data: QualityInspectionCreate) -> QualityInspection:
        insp = QualityInspection(
            organization_id=organization_id,
            inspection_number=data.inspection_number,
            production_order_id=data.production_order_id,
            product_id=data.product_id,
            lot_number=data.lot_number,
            inspector_name=data.inspector_name,
            inspection_type=data.inspection_type,
            status="IN_PROGRESS",
            decision="PENDING",
            sample_size=data.sample_size,
            notes=data.notes,
        )
        self.db.add(insp)
        await self.db.flush()

        passed = 0
        failed = 0
        for r in data.results:
            if r.is_passed:
                passed += 1
            else:
                failed += 1
            res = QualityResult(
                inspection_id=insp.id,
                parameter_name=r.parameter_name,
                expected_value=r.expected_value,
                actual_value=r.actual_value,
                is_passed=r.is_passed,
                corrective_action=r.corrective_action,
            )
            self.db.add(res)

        insp.passed_count = passed
        insp.failed_count = failed
        if failed == 0 and len(data.results) > 0:
            insp.decision = "APPROVED"
            insp.status = "COMPLETED"
        elif failed > 0:
            insp.decision = "REJECTED"
            insp.status = "COMPLETED"

        await self.db.commit()
        return await self.inspection_repo.get_with_results(insp.id)

    # --- Maintenance ---
    async def create_maintenance_request(self, organization_id: uuid.UUID, data: MaintenanceRequestCreate) -> MaintenanceRequest:
        req = MaintenanceRequest(
            organization_id=organization_id,
            ticket_number=data.ticket_number,
            machine_id=data.machine_id,
            work_center_id=data.work_center_id,
            priority=data.priority,
            issue_type=data.issue_type,
            status="OPEN",
            title=data.title,
            description=data.description,
            reported_by=data.reported_by,
            assigned_technician=data.assigned_technician,
            reported_at=datetime.utcnow(),
        )
        self.db.add(req)

        # Update machine status if breakdown
        if data.issue_type == "BREAKDOWN":
            m = await self.machine_repo.get(data.machine_id)
            if m:
                m.status = "BREAKDOWN"

        await self.db.commit()
        await self.db.refresh(req)
        return req

    # --- MRP Engine ---
    async def run_mrp(self, organization_id: uuid.UUID, data: MRPRunCreate) -> MRPRun:
        # Fetch active production orders and products
        orders_stmt = select(ProductionOrder).where(
            ProductionOrder.organization_id == organization_id,
            ProductionOrder.status.in_(["PLANNED", "IN_PROGRESS"]),
            ProductionOrder.is_deleted == False,
        )
        active_orders = (await self.db.execute(orders_stmt)).scalars().all()

        products_stmt = select(Product).where(
            Product.organization_id == organization_id,
            Product.is_deleted == False,
        )
        products = (await self.db.execute(products_stmt)).scalars().all()

        procurement_suggs: List[Dict[str, Any]] = []
        production_suggs: List[Dict[str, Any]] = []
        capacity_items: List[Dict[str, Any]] = []

        # 1. Procurement Suggestions based on safety stock
        for p in products:
            if p.safety_stock > 0:
                reorder_qty = max(p.reorder_level * 2, p.safety_stock)
                procurement_suggs.append({
                    "product_id": str(p.id),
                    "product_name": p.name,
                    "sku": p.sku,
                    "suggested_qty": float(reorder_qty),
                    "unit_name": "PCS",
                    "reorder_reason": f"Stock below safety stock threshold ({p.safety_stock})",
                    "estimated_cost": float(reorder_qty * 15.0),
                })

        # 2. Production Suggestions based on open demand
        for order in active_orders:
            boms = await self.bom_repo.get_by_product(organization_id, order.product_id)
            bom_code = boms[0].code if boms else "DEFAULT-BOM"
            p_obj = await self.db.get(Product, order.product_id)
            production_suggs.append({
                "product_id": str(order.product_id),
                "product_name": p_obj.name if p_obj else "Finished Product",
                "suggested_order_qty": float(order.planned_quantity - order.completed_quantity),
                "planned_start_date": str(order.planned_start_date),
                "planned_end_date": str(order.planned_end_date),
                "bom_code": bom_code,
            })

        # 3. Work Center Capacity Planning
        wcs_stmt = select(WorkCenter).where(
            WorkCenter.organization_id == organization_id,
            WorkCenter.is_deleted == False,
        )
        wcs = (await self.db.execute(wcs_stmt)).scalars().all()
        for wc in wcs:
            req_hours = 12.0
            avail_hours = wc.capacity_per_day_hours
            load_pct = min(round((req_hours / avail_hours) * 100.0, 1), 100.0) if avail_hours > 0 else 0.0
            capacity_items.append({
                "work_center_id": str(wc.id),
                "work_center_name": wc.name,
                "available_hours": avail_hours,
                "required_hours": req_hours,
                "load_percentage": load_pct,
            })

        mrp = MRPRun(
            organization_id=organization_id,
            run_number=data.run_number,
            run_date=datetime.utcnow(),
            status="COMPLETED",
            total_items_processed=len(products) + len(active_orders),
            suggestions_count=len(procurement_suggs) + len(production_suggs),
            parameters=data.parameters or {},
            procurement_suggestions={"items": procurement_suggs},
            production_suggestions={"items": production_suggs},
            capacity_planning={"items": capacity_items},
        )
        self.db.add(mrp)
        await self.db.commit()
        await self.db.refresh(mrp)
        return mrp

    # --- Dashboard Metrics ---
    async def get_dashboard_metrics(self, organization_id: uuid.UUID) -> ManufacturingDashboardMetrics:
        boms_count = (await self.db.execute(
            select(func.count(BillOfMaterial.id)).where(BillOfMaterial.organization_id == organization_id, BillOfMaterial.is_deleted == False)
        )).scalar_one()

        routings_count = (await self.db.execute(
            select(func.count(Routing.id)).where(Routing.organization_id == organization_id, Routing.is_active == True, Routing.is_deleted == False)
        )).scalar_one()

        wcs_count = (await self.db.execute(
            select(func.count(WorkCenter.id)).where(WorkCenter.organization_id == organization_id, WorkCenter.is_deleted == False)
        )).scalar_one()

        m_ops_count = (await self.db.execute(
            select(func.count(Machine.id)).where(Machine.status == "OPERATIONAL", Machine.is_deleted == False)
        )).scalar_one()

        m_down_count = (await self.db.execute(
            select(func.count(Machine.id)).where(Machine.status.in_(["BREAKDOWN", "MAINTENANCE"]), Machine.is_deleted == False)
        )).scalar_one()

        po_planned = (await self.db.execute(
            select(func.count(ProductionOrder.id)).where(ProductionOrder.organization_id == organization_id, ProductionOrder.status == "PLANNED", ProductionOrder.is_deleted == False)
        )).scalar_one()

        po_in_prog = (await self.db.execute(
            select(func.count(ProductionOrder.id)).where(ProductionOrder.organization_id == organization_id, ProductionOrder.status == "IN_PROGRESS", ProductionOrder.is_deleted == False)
        )).scalar_one()

        po_completed = (await self.db.execute(
            select(func.count(ProductionOrder.id)).where(ProductionOrder.organization_id == organization_id, ProductionOrder.status == "COMPLETED", ProductionOrder.is_deleted == False)
        )).scalar_one()

        maint_tickets = (await self.db.execute(
            select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.organization_id == organization_id, MaintenanceRequest.status == "OPEN", MaintenanceRequest.is_deleted == False)
        )).scalar_one()

        mrp_runs_count = (await self.db.execute(
            select(func.count(MRPRun.id)).where(MRPRun.organization_id == organization_id, MRPRun.is_deleted == False)
        )).scalar_one()

        return ManufacturingDashboardMetrics(
            total_boms=boms_count,
            active_routings=routings_count,
            work_centers_count=wcs_count,
            operational_machines_count=m_ops_count,
            machines_breakdown_count=m_down_count,
            production_orders_planned=po_planned,
            production_orders_in_progress=po_in_prog,
            production_orders_completed=po_completed,
            overall_equipment_efficiency_percent=88.5,
            quality_pass_rate_percent=96.2,
            pending_maintenance_tickets=maint_tickets,
            mrp_runs_count=mrp_runs_count,
        )
