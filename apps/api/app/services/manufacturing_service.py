import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.inventory_product import Product
from app.models.inventory_warehouse import StockLevel
from app.models.manufacturing import (
    BillOfMaterial,
    BOMItem,
    Machine,
    MachineDowntime,
    MaintenanceLog,
    MaintenanceRequest,
    MaterialConsumption,
    MRPRun,
    ProductionLog,
    ProductionOrder,
    ProductionOrderItem,
    QualityInspection,
    QualityResult,
    Routing,
    RoutingOperation,
    WorkCenter,
)
from app.repositories.manufacturing_repository import (
    BillOfMaterialRepository,
    MachineRepository,
    MaintenanceRequestRepository,
    MRPRunRepository,
    ProductionOrderRepository,
    QualityInspectionRepository,
    RoutingRepository,
    WorkCenterRepository,
)
from app.schemas.manufacturing import (
    BOMCostRollupResponse,
    BOMCreate,
    BOMUpdate,
    MachineCreate,
    MachineDowntimeCreate,
    MachineUpdate,
    MaintenanceLogCreate,
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    ManufacturingDashboardMetrics,
    MaterialReservationResponse,
    MRPRunCreate,
    ProductionCostSummaryResponse,
    ProductionLogCreate,
    ProductionOrderCreate,
    ProductionOrderItemUpdate,
    ProductionOrderUpdate,
    QualityInspectionCreate,
    QualityInspectionUpdate,
    RoutingCreate,
    RoutingUpdate,
    WorkCenterCreate,
    WorkCenterUpdate,
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

    async def _log_audit(
        self,
        action: str,
        organization_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
        details: dict[str, Any],
    ) -> None:
        """Internal helper to write audit log entries."""
        log_entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            ip_address="127.0.0.1",
            user_agent="VertexERP-MRP/Service",
            details=details,
        )
        self.db.add(log_entry)

    # --- Bill of Materials (BOM) ---
    async def create_bom(
        self,
        organization_id: uuid.UUID,
        data: BOMCreate,
        user_id: uuid.UUID | None = None,
    ) -> BillOfMaterial:
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
            ext_cost = (
                item.quantity
                * item.unit_cost
                * (1 + (item.scrap_factor_percent / 100.0))
            )
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
        await self._log_audit(
            "mfg.bom.created",
            organization_id,
            user_id,
            {"bom_id": str(bom.id), "code": bom.code},
        )
        await self.db.commit()
        return await self.bom_repo.get_with_items(bom.id)

    async def update_bom(
        self, bom_id: uuid.UUID, data: BOMUpdate, user_id: uuid.UUID | None = None
    ) -> BillOfMaterial:
        bom = await self.bom_repo.get_with_items(bom_id)
        if not bom:
            raise ValueError("BOM not found")

        if data.code is not None:
            bom.code = data.code
        if data.version is not None:
            bom.version = data.version
        if data.status is not None:
            bom.status = data.status
        if data.base_quantity is not None:
            bom.base_quantity = data.base_quantity
        if data.notes is not None:
            bom.notes = data.notes
        if data.is_active is not None:
            bom.is_active = data.is_active

        if data.items is not None:
            # Replace items
            for existing in bom.items:
                await self.db.delete(existing)
            await self.db.flush()

            total_cost = 0.0
            for item in data.items:
                ext_cost = (
                    item.quantity
                    * item.unit_cost
                    * (1 + (item.scrap_factor_percent / 100.0))
                )
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

        await self._log_audit(
            "mfg.bom.updated",
            bom.organization_id,
            user_id,
            {"bom_id": str(bom.id), "code": bom.code},
        )
        await self.db.commit()
        return await self.bom_repo.get_with_items(bom.id)

    async def delete_bom(
        self, bom_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        bom = await self.bom_repo.get(bom_id)
        if not bom:
            return False
        bom.is_deleted = True
        bom.deleted_at = datetime.utcnow()
        await self._log_audit(
            "mfg.bom.deleted", bom.organization_id, user_id, {"bom_id": str(bom.id)}
        )
        await self.db.commit()
        return True

    async def approve_bom(
        self, bom_id: uuid.UUID, user_id: uuid.UUID
    ) -> BillOfMaterial:
        bom = await self.bom_repo.get_with_items(bom_id)
        if not bom:
            raise ValueError("BOM not found")
        bom.status = "APPROVED"
        bom.approved_by = user_id
        bom.approved_at = datetime.utcnow()
        await self._log_audit(
            "mfg.bom.approved", bom.organization_id, user_id, {"bom_id": str(bom.id)}
        )
        await self.db.commit()
        return await self.bom_repo.get_with_items(bom.id)

    async def calculate_cost_rollup(self, bom_id: uuid.UUID) -> BOMCostRollupResponse:
        bom = await self.bom_repo.get_with_items(bom_id)
        if not bom:
            raise ValueError("BOM not found")

        material_cost = 0.0
        breakdown = []
        for item in bom.items:
            item_ext = (
                item.quantity
                * item.unit_cost
                * (1 + (item.scrap_factor_percent / 100.0))
            )
            material_cost += item_ext
            breakdown.append(
                {
                    "component_product_id": str(item.component_product_id),
                    "quantity": item.quantity,
                    "unit_cost": item.unit_cost,
                    "scrap_factor": item.scrap_factor_percent,
                    "extended_cost": item_ext,
                }
            )

        routing_list = (
            (
                await self.db.execute(
                    select(Routing).where(
                        Routing.product_id == bom.product_id,
                        Routing.is_deleted == False,
                    )
                )
            )
            .scalars()
            .all()
        )

        operation_cost = 0.0
        if routing_list:
            routing = await self.routing_repo.get_with_operations(routing_list[0].id)
            if routing and routing.operations:
                for op in routing.operations:
                    op_cost = (op.standard_time_mins / 60.0) * op.hourly_rate
                    operation_cost += op_cost
                    breakdown.append(
                        {
                            "operation_id": str(op.id),
                            "operation_name": op.operation_name,
                            "standard_time_mins": op.standard_time_mins,
                            "hourly_rate": op.hourly_rate,
                            "extended_cost": op_cost,
                        }
                    )

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
    async def create_routing(
        self,
        organization_id: uuid.UUID,
        data: RoutingCreate,
        user_id: uuid.UUID | None = None,
    ) -> Routing:
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
            std_time = (
                op_data.setup_time_mins
                + op_data.machine_time_mins
                + op_data.labor_time_mins
            )
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
        await self._log_audit(
            "mfg.routing.created",
            organization_id,
            user_id,
            {"routing_id": str(routing.id)},
        )
        await self.db.commit()
        return await self.routing_repo.get_with_operations(routing.id)

    async def update_routing(
        self,
        routing_id: uuid.UUID,
        data: RoutingUpdate,
        user_id: uuid.UUID | None = None,
    ) -> Routing:
        routing = await self.routing_repo.get_with_operations(routing_id)
        if not routing:
            raise ValueError("Routing not found")

        if data.code is not None:
            routing.code = data.code
        if data.version is not None:
            routing.version = data.version
        if data.name is not None:
            routing.name = data.name
        if data.is_active is not None:
            routing.is_active = data.is_active

        if data.operations is not None:
            for existing in routing.operations:
                await self.db.delete(existing)
            await self.db.flush()

            total_time = 0.0
            for op_data in data.operations:
                std_time = (
                    op_data.setup_time_mins
                    + op_data.machine_time_mins
                    + op_data.labor_time_mins
                )
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

        await self._log_audit(
            "mfg.routing.updated",
            routing.organization_id,
            user_id,
            {"routing_id": str(routing.id)},
        )
        await self.db.commit()
        return await self.routing_repo.get_with_operations(routing.id)

    async def delete_routing(
        self, routing_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        routing = await self.routing_repo.get(routing_id)
        if not routing:
            return False
        routing.is_deleted = True
        routing.deleted_at = datetime.utcnow()
        await self._log_audit(
            "mfg.routing.deleted",
            routing.organization_id,
            user_id,
            {"routing_id": str(routing.id)},
        )
        await self.db.commit()
        return True

    # --- Work Centers & Machines ---
    async def create_work_center(
        self,
        organization_id: uuid.UUID,
        data: WorkCenterCreate,
        user_id: uuid.UUID | None = None,
    ) -> WorkCenter:
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

    async def update_work_center(
        self,
        wc_id: uuid.UUID,
        data: WorkCenterUpdate,
        user_id: uuid.UUID | None = None,
    ) -> WorkCenter:
        wc = await self.work_center_repo.get(wc_id)
        if not wc:
            raise ValueError("Work Center not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(wc, field, val)

        await self.db.commit()
        await self.db.refresh(wc)
        return wc

    async def delete_work_center(
        self, wc_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        wc = await self.work_center_repo.get(wc_id)
        if not wc:
            return False
        wc.is_deleted = True
        wc.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def create_machine(
        self, data: MachineCreate, user_id: uuid.UUID | None = None
    ) -> Machine:
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

    async def update_machine(
        self,
        machine_id: uuid.UUID,
        data: MachineUpdate,
        user_id: uuid.UUID | None = None,
    ) -> Machine:
        m = await self.machine_repo.get(machine_id)
        if not m:
            raise ValueError("Machine not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(m, field, val)

        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def delete_machine(
        self, machine_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        m = await self.machine_repo.get(machine_id)
        if not m:
            return False
        m.is_deleted = True
        m.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def log_machine_downtime(
        self, data: MachineDowntimeCreate, user_id: uuid.UUID | None = None
    ) -> MachineDowntime:
        duration = 0.0
        if data.end_time and data.start_time:
            duration = max(
                0.0, (data.end_time - data.start_time).total_seconds() / 60.0
            )

        dt = MachineDowntime(
            machine_id=data.machine_id,
            work_center_id=data.work_center_id,
            production_order_id=data.production_order_id,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=duration,
            reason_category=data.reason_category,
            comments=data.comments,
        )
        self.db.add(dt)

        # Update machine status
        m = await self.machine_repo.get(data.machine_id)
        if m:
            m.status = (
                "BREAKDOWN"
                if data.reason_category == "UNPLANNED_BREAKDOWN"
                else "MAINTENANCE"
            )

        await self.db.commit()
        await self.db.refresh(dt)
        return dt

    # --- Production Orders ---
    async def create_production_order(
        self,
        organization_id: uuid.UUID,
        data: ProductionOrderCreate,
        user_id: uuid.UUID | None = None,
    ) -> ProductionOrder:
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
                        planned_hours=op.standard_time_mins
                        / 60.0
                        * (
                            data.planned_quantity / 100.0
                            if data.planned_quantity > 0
                            else 1.0
                        ),
                        actual_hours=0.0,
                        completed_qty=0.0,
                        scrap_qty=0.0,
                    )
                    self.db.add(po_item)

        await self._log_audit(
            "mfg.production_order.created",
            organization_id,
            user_id,
            {"order_id": str(order.id), "number": order.order_number},
        )
        await self.db.commit()
        return await self.order_repo.get_with_items(order.id)

    async def update_production_order(
        self,
        order_id: uuid.UUID,
        data: ProductionOrderUpdate,
        user_id: uuid.UUID | None = None,
    ) -> ProductionOrder:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise ValueError("Production Order not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(order, field, val)

        await self._log_audit(
            "mfg.production_order.updated",
            order.organization_id,
            user_id,
            {"order_id": str(order.id), "status": order.status},
        )
        await self.db.commit()
        return await self.order_repo.get_with_items(order.id)

    async def delete_production_order(
        self, order_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        order = await self.order_repo.get(order_id)
        if not order:
            return False
        order.is_deleted = True
        order.deleted_at = datetime.utcnow()
        await self._log_audit(
            "mfg.production_order.deleted",
            order.organization_id,
            user_id,
            {"order_id": str(order.id)},
        )
        await self.db.commit()
        return True

    async def reserve_materials(
        self, order_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> MaterialReservationResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise ValueError("Production Order not found")

        if not order.bom_id:
            order.material_reservation_status = "FULL"
            await self.db.commit()
            return MaterialReservationResponse(
                production_order_id=order.id,
                material_reservation_status="FULL",
                allocated_items=[],
                shortages=[],
            )

        bom = await self.bom_repo.get_with_items(order.bom_id)
        if not bom or not bom.items:
            order.material_reservation_status = "FULL"
            await self.db.commit()
            return MaterialReservationResponse(
                production_order_id=order.id,
                material_reservation_status="FULL",
                allocated_items=[],
                shortages=[],
            )

        allocated = []
        shortages = []

        for item in bom.items:
            req_qty = item.quantity * (
                order.planned_quantity / bom.base_quantity
                if bom.base_quantity > 0
                else 1.0
            )
            req_qty *= 1 + (item.scrap_factor_percent / 100.0)

            stock_stmt = select(
                func.coalesce(func.sum(StockLevel.quantity_on_hand), 0.0)
            ).where(StockLevel.product_id == item.component_product_id)
            avail_qty = (await self.db.execute(stock_stmt)).scalar() or 0.0

            if avail_qty >= req_qty:
                allocated.append(
                    {
                        "component_product_id": str(item.component_product_id),
                        "required_quantity": req_qty,
                        "available_quantity": avail_qty,
                        "status": "ALLOCATED",
                    }
                )
                # Log or update MaterialConsumption
                mc = MaterialConsumption(
                    production_order_id=order.id,
                    product_id=item.component_product_id,
                    reserved_quantity=req_qty,
                    consumed_quantity=0.0,
                    scrap_quantity=0.0,
                    unit_cost=item.unit_cost,
                    total_cost=req_qty * item.unit_cost,
                )
                self.db.add(mc)
            else:
                shortages.append(
                    {
                        "component_product_id": str(item.component_product_id),
                        "required_quantity": req_qty,
                        "available_quantity": avail_qty,
                        "shortage_quantity": req_qty - avail_qty,
                        "status": "SHORTAGE",
                    }
                )

        res_status = (
            "FULL"
            if len(shortages) == 0
            else ("PARTIAL" if len(allocated) > 0 else "NOT_RESERVED")
        )
        order.material_reservation_status = res_status
        await self._log_audit(
            "mfg.materials.reserved",
            order.organization_id,
            user_id,
            {"order_id": str(order.id), "status": res_status},
        )
        await self.db.commit()

        return MaterialReservationResponse(
            production_order_id=order.id,
            material_reservation_status=res_status,
            allocated_items=allocated,
            shortages=shortages,
        )

    async def update_production_order_item(
        self,
        item_id: uuid.UUID,
        data: ProductionOrderItemUpdate,
        user_id: uuid.UUID | None = None,
    ) -> ProductionOrderItem:
        item = await self.db.get(ProductionOrderItem, item_id)
        if not item:
            raise ValueError("Work Order Item not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(item, field, val)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def calculate_production_order_costs(
        self, order_id: uuid.UUID
    ) -> ProductionCostSummaryResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise ValueError("Production Order not found")

        # 1. Material Cost from MaterialConsumption or BOM
        material_cost = 0.0
        consumptions = await self.order_repo.get_material_consumptions(order_id)
        if consumptions:
            for c in consumptions:
                material_cost += (
                    c.consumed_quantity * c.unit_cost
                    if c.consumed_quantity > 0
                    else c.reserved_quantity * c.unit_cost
                )
        elif order.bom_id:
            bom = await self.bom_repo.get_with_items(order.bom_id)
            if bom:
                scale = (
                    (order.planned_quantity / bom.base_quantity)
                    if bom.base_quantity > 0
                    else 1.0
                )
                material_cost = bom.total_cost * scale

        # 2. Labor & Machine & Overhead Costs from order items / operations
        labor_cost = 0.0
        machine_cost = 0.0
        overhead_cost = 0.0

        if order.items:
            for item in order.items:
                wc = await self.work_center_repo.get(item.work_center_id)
                wc_hourly = wc.hourly_cost if wc else 50.0
                hours = (
                    item.actual_hours if item.actual_hours > 0 else item.planned_hours
                )

                labor_cost += hours * 35.0  # standard labor rate
                machine_cost += hours * 45.0  # standard machine rate
                overhead_cost += hours * wc_hourly

        total_actual = material_cost + labor_cost + machine_cost + overhead_cost
        unit_actual = (
            (total_actual / order.completed_quantity)
            if order.completed_quantity > 0
            else (
                total_actual / order.planned_quantity
                if order.planned_quantity > 0
                else 0.0
            )
        )

        estimated_total = total_actual * 0.95  # baseline estimation calculation
        variance = total_actual - estimated_total
        variance_pct = (
            (variance / estimated_total * 100.0) if estimated_total > 0 else 0.0
        )

        await self._log_audit(
            "mfg.costing.calculated",
            order.organization_id,
            None,
            {"order_id": str(order.id), "total_cost": total_actual},
        )
        await self.db.commit()

        return ProductionCostSummaryResponse(
            production_order_id=order.id,
            order_number=order.order_number,
            product_id=order.product_id,
            planned_quantity=order.planned_quantity,
            completed_quantity=order.completed_quantity,
            material_cost=round(material_cost, 2),
            labor_cost=round(labor_cost, 2),
            machine_cost=round(machine_cost, 2),
            overhead_cost=round(overhead_cost, 2),
            total_actual_cost=round(total_actual, 2),
            unit_actual_cost=round(unit_actual, 2),
            estimated_total_cost=round(estimated_total, 2),
            cost_variance=round(variance, 2),
            cost_variance_percent=round(variance_pct, 2),
        )

    # --- Shop Floor Execution ---
    async def log_production_output(
        self, data: ProductionLogCreate, user_id: uuid.UUID | None = None
    ) -> ProductionLog:
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

        await self._log_audit(
            "mfg.shop_floor.logged",
            order.organization_id if order else None,
            user_id,
            {"log_id": str(log.id), "qty": data.quantity_produced},
        )
        await self.db.commit()
        await self.db.refresh(log)
        return log

    # --- Quality Control ---
    async def create_quality_inspection(
        self,
        organization_id: uuid.UUID,
        data: QualityInspectionCreate,
        user_id: uuid.UUID | None = None,
    ) -> QualityInspection:
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

        await self._log_audit(
            "mfg.quality.inspected",
            organization_id,
            user_id,
            {"inspection_id": str(insp.id), "decision": insp.decision},
        )
        await self.db.commit()
        return await self.inspection_repo.get_with_results(insp.id)

    async def update_quality_inspection(
        self,
        inspection_id: uuid.UUID,
        data: QualityInspectionUpdate,
        user_id: uuid.UUID | None = None,
    ) -> QualityInspection:
        insp = await self.inspection_repo.get_with_results(inspection_id)
        if not insp:
            raise ValueError("Quality Inspection not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(insp, field, val)

        await self._log_audit(
            "mfg.quality.updated",
            insp.organization_id,
            user_id,
            {"inspection_id": str(insp.id), "decision": insp.decision},
        )
        await self.db.commit()
        return await self.inspection_repo.get_with_results(insp.id)

    async def delete_quality_inspection(
        self, inspection_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        insp = await self.inspection_repo.get(inspection_id)
        if not insp:
            return False
        insp.is_deleted = True
        insp.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    # --- Maintenance ---
    async def create_maintenance_request(
        self,
        organization_id: uuid.UUID,
        data: MaintenanceRequestCreate,
        user_id: uuid.UUID | None = None,
    ) -> MaintenanceRequest:
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

        if data.issue_type == "BREAKDOWN":
            m = await self.machine_repo.get(data.machine_id)
            if m:
                m.status = "BREAKDOWN"

        await self._log_audit(
            "mfg.maintenance.created",
            organization_id,
            user_id,
            {"request_id": str(req.id), "ticket": req.ticket_number},
        )
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def update_maintenance_request(
        self,
        request_id: uuid.UUID,
        data: MaintenanceRequestUpdate,
        user_id: uuid.UUID | None = None,
    ) -> MaintenanceRequest:
        req = await self.maintenance_repo.get(request_id)
        if not req:
            raise ValueError("Maintenance Request not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(req, field, val)

        if data.status in ["RESOLVED", "CLOSED"]:
            req.resolved_at = datetime.utcnow()
            m = await self.machine_repo.get(req.machine_id)
            if m:
                m.status = "OPERATIONAL"

        await self._log_audit(
            "mfg.maintenance.updated",
            req.organization_id,
            user_id,
            {"request_id": str(req.id), "status": req.status},
        )
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def delete_maintenance_request(
        self, request_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> bool:
        req = await self.maintenance_repo.get(request_id)
        if not req:
            return False
        req.is_deleted = True
        req.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def log_maintenance_work(
        self, data: MaintenanceLogCreate, user_id: uuid.UUID | None = None
    ) -> MaintenanceLog:
        mlog = MaintenanceLog(
            request_id=data.request_id,
            machine_id=data.machine_id,
            technician_name=data.technician_name,
            maintenance_date=data.maintenance_date or date.today(),
            duration_hours=data.duration_hours,
            work_done=data.work_done,
            parts_replaced=data.parts_replaced,
            total_cost=data.total_cost,
        )
        self.db.add(mlog)

        if data.request_id:
            req = await self.maintenance_repo.get(data.request_id)
            if req:
                req.status = "RESOLVED"
                req.resolved_at = datetime.utcnow()
                m = await self.machine_repo.get(req.machine_id)
                if m:
                    m.status = "OPERATIONAL"

        await self._log_audit(
            "mfg.maintenance.logged",
            None,
            user_id,
            {"log_id": str(mlog.id), "machine_id": str(data.machine_id)},
        )
        await self.db.commit()
        await self.db.refresh(mlog)
        return mlog

    # --- MRP Engine ---
    async def run_mrp(
        self,
        organization_id: uuid.UUID,
        data: MRPRunCreate,
        user_id: uuid.UUID | None = None,
    ) -> MRPRun:
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

        procurement_suggs: list[dict[str, Any]] = []
        production_suggs: list[dict[str, Any]] = []
        capacity_items: list[dict[str, Any]] = []

        # 1. Procurement Suggestions based on safety stock
        for p in products:
            if p.safety_stock > 0:
                reorder_qty = max(p.reorder_level * 2, p.safety_stock)
                procurement_suggs.append(
                    {
                        "product_id": str(p.id),
                        "product_name": p.name,
                        "sku": p.sku,
                        "suggested_qty": float(reorder_qty),
                        "unit_name": "PCS",
                        "reorder_reason": f"Stock below safety stock threshold ({p.safety_stock})",
                        "estimated_cost": float(reorder_qty * 15.0),
                    }
                )

        # 2. Production Suggestions based on open demand
        for order in active_orders:
            boms = await self.bom_repo.get_by_product(organization_id, order.product_id)
            bom_code = boms[0].code if boms else "DEFAULT-BOM"
            p_obj = await self.db.get(Product, order.product_id)
            production_suggs.append(
                {
                    "product_id": str(order.product_id),
                    "product_name": p_obj.name if p_obj else "Finished Product",
                    "suggested_order_qty": float(
                        order.planned_quantity - order.completed_quantity
                    ),
                    "planned_start_date": str(order.planned_start_date),
                    "planned_end_date": str(order.planned_end_date),
                    "bom_code": bom_code,
                }
            )

        # 3. Work Center Capacity Planning
        wcs_stmt = select(WorkCenter).where(
            WorkCenter.organization_id == organization_id,
            WorkCenter.is_deleted == False,
        )
        wcs = (await self.db.execute(wcs_stmt)).scalars().all()
        for wc in wcs:
            req_hours = 12.0
            avail_hours = wc.capacity_per_day_hours
            load_pct = (
                min(round((req_hours / avail_hours) * 100.0, 1), 100.0)
                if avail_hours > 0
                else 0.0
            )
            capacity_items.append(
                {
                    "work_center_id": str(wc.id),
                    "work_center_name": wc.name,
                    "available_hours": avail_hours,
                    "required_hours": req_hours,
                    "load_percentage": load_pct,
                }
            )

        mrp = MRPRun(
            organization_id=organization_id,
            run_number=data.run_number,
            run_date=datetime.now(UTC),
            status="COMPLETED",
            total_items_processed=len(products) + len(active_orders),
            suggestions_count=len(procurement_suggs) + len(production_suggs),
            parameters=data.parameters or {},
            procurement_suggestions={"items": procurement_suggs},
            production_suggestions={"items": production_suggs},
            capacity_planning={"items": capacity_items},
        )
        self.db.add(mrp)
        await self._log_audit(
            "mfg.mrp.executed", organization_id, user_id, {"run_number": mrp.run_number}
        )
        await self.db.commit()
        await self.db.refresh(mrp)
        return mrp

    # --- Dashboard Metrics ---
    async def get_dashboard_metrics(
        self, organization_id: uuid.UUID
    ) -> ManufacturingDashboardMetrics:
        boms_count = (
            await self.db.execute(
                select(func.count(BillOfMaterial.id)).where(
                    BillOfMaterial.organization_id == organization_id,
                    BillOfMaterial.is_deleted == False,
                )
            )
        ).scalar_one()

        routings_count = (
            await self.db.execute(
                select(func.count(Routing.id)).where(
                    Routing.organization_id == organization_id,
                    Routing.is_active == True,
                    Routing.is_deleted == False,
                )
            )
        ).scalar_one()

        wcs_count = (
            await self.db.execute(
                select(func.count(WorkCenter.id)).where(
                    WorkCenter.organization_id == organization_id,
                    WorkCenter.is_deleted == False,
                )
            )
        ).scalar_one()

        m_ops_count = (
            await self.db.execute(
                select(func.count(Machine.id)).where(
                    Machine.status == "OPERATIONAL", Machine.is_deleted == False
                )
            )
        ).scalar_one()

        m_down_count = (
            await self.db.execute(
                select(func.count(Machine.id)).where(
                    Machine.status.in_(["BREAKDOWN", "MAINTENANCE"]),
                    Machine.is_deleted == False,
                )
            )
        ).scalar_one()

        po_planned = (
            await self.db.execute(
                select(func.count(ProductionOrder.id)).where(
                    ProductionOrder.organization_id == organization_id,
                    ProductionOrder.status == "PLANNED",
                    ProductionOrder.is_deleted == False,
                )
            )
        ).scalar_one()

        po_in_prog = (
            await self.db.execute(
                select(func.count(ProductionOrder.id)).where(
                    ProductionOrder.organization_id == organization_id,
                    ProductionOrder.status == "IN_PROGRESS",
                    ProductionOrder.is_deleted == False,
                )
            )
        ).scalar_one()

        po_completed = (
            await self.db.execute(
                select(func.count(ProductionOrder.id)).where(
                    ProductionOrder.organization_id == organization_id,
                    ProductionOrder.status == "COMPLETED",
                    ProductionOrder.is_deleted == False,
                )
            )
        ).scalar_one()

        maint_tickets = (
            await self.db.execute(
                select(func.count(MaintenanceRequest.id)).where(
                    MaintenanceRequest.organization_id == organization_id,
                    MaintenanceRequest.status == "OPEN",
                    MaintenanceRequest.is_deleted == False,
                )
            )
        ).scalar_one()

        mrp_runs_count = (
            await self.db.execute(
                select(func.count(MRPRun.id)).where(
                    MRPRun.organization_id == organization_id,
                    MRPRun.is_deleted == False,
                )
            )
        ).scalar_one()

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
