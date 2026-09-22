"""Production Order and Shop-Floor Execution Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException,
)
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.manufacturing.models.production_order import (
    MaterialConsumption,
    ProductionOrder,
    ProductionOutput,
    ProductionScrap,
    WorkOrder,
)
from app.modules.manufacturing.repositories.bom_repository import BOMRepository
from app.modules.manufacturing.repositories.production_order_repository import (
    ProductionOrderRepository,
)
from app.modules.manufacturing.repositories.routing_repository import RoutingRepository
from app.modules.manufacturing.repositories.work_center_repository import WorkCenterRepository
from app.modules.manufacturing.schemas.production_order import (
    MaterialConsumptionCreate,
    ProductionOrderCreate,
    ProductionOutputCreate,
    ProductionScrapCreate,
    WorkOrderUpdateStatus,
)


class ProductionService:
    """Domain service managing Production Orders, Shop-Floor Work Orders, and Auditable Ledger movements."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.order_repo = ProductionOrderRepository(session)
        self.bom_repo = BOMRepository(session)
        self.routing_repo = RoutingRepository(session)
        self.work_center_repo = WorkCenterRepository(session)
        self.product_repo = ProductRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.stock_ledger = StockLedgerService(session)

    async def create_production_order(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: ProductionOrderCreate,
        created_by_id: uuid.UUID | None = None,
    ) -> ProductionOrder:
        # 1. Validate Product
        product = await self.product_repo.get_by_id(data.product_id, tenant_id, org_id)
        if not product:
            raise NotFoundException(f"Product {data.product_id} not found.")

        # 2. Resolve BOM and Version
        bom_id = data.bom_id
        bom_version_id = data.bom_version_id
        if not bom_id or not bom_version_id:
            default_bom = await self.bom_repo.get_default_bom_by_product(
                data.product_id, tenant_id, org_id
            )
            if not default_bom or not default_bom.versions:
                raise ValidationException(
                    f"No active Bill of Materials configured for product '{product.name}' ({product.sku})."
                )
            bom_id = default_bom.id
            active_version = next(
                (v for v in default_bom.versions if v.status == "ACTIVE"), default_bom.versions[0]
            )
            bom_version_id = active_version.id

        # 3. Resolve Routing
        routing_id = data.routing_id
        if not routing_id:
            routing = await self.routing_repo.get_routing_by_product(
                data.product_id, tenant_id, org_id
            )
            if routing:
                routing_id = routing.id

        # 4. Generate Order Number
        order_number = f"MO-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

        order = ProductionOrder(
            tenant_id=tenant_id,
            organization_id=org_id,
            order_number=order_number,
            product_id=data.product_id,
            bom_id=bom_id,
            bom_version_id=bom_version_id,
            routing_id=routing_id,
            source_sales_order_id=data.source_sales_order_id,
            planned_quantity=data.planned_quantity,
            target_warehouse_id=data.target_warehouse_id,
            planned_start_date=data.planned_start_date,
            planned_due_date=data.planned_due_date,
            priority=data.priority,
            status="PLANNED",
            created_by_id=created_by_id,
            notes=data.notes,
        )

        await self.order_repo.create_order(order)
        return order

    async def confirm_production_order(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductionOrder:
        """Transitions order to CONFIRMED and dispatches Work Orders from Routing."""
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        if order.status != "PLANNED":
            raise BadRequestException(
                f"Cannot confirm production order in status '{order.status}'."
            )

        order.status = "CONFIRMED"

        # Generate Work Orders if routing is configured
        if order.routing_id and not order.work_orders:
            routing = await self.routing_repo.get_routing_by_id(order.routing_id, tenant_id, org_id)
            if routing and routing.operations:
                for op in routing.operations:
                    wc = await self.work_center_repo.get_work_center_by_id(
                        op.work_center_id, tenant_id, org_id
                    )
                    hourly_rate = (
                        (wc.cost_per_hour + wc.overhead_cost_per_hour) if wc else Decimal("50.0000")
                    )
                    planned_hours = op.setup_time_hours + (
                        op.run_time_per_unit_hours * order.planned_quantity
                    )

                    wo = WorkOrder(
                        tenant_id=tenant_id,
                        organization_id=org_id,
                        production_order_id=order.id,
                        sequence=op.sequence,
                        operation_name=op.operation_name,
                        work_center_id=op.work_center_id,
                        machine_id=op.preferred_machine_id,
                        planned_duration_hours=planned_hours,
                        hourly_rate=hourly_rate,
                        status="PENDING",
                    )
                    order.work_orders.append(wo)

        await self.session.flush()
        return order

    async def start_production_order(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductionOrder:
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        if order.status not in ("PLANNED", "CONFIRMED"):
            raise BadRequestException(f"Cannot start production order in status '{order.status}'.")

        order.status = "IN_PROGRESS"
        order.actual_start_date = datetime.now(UTC)
        await self.session.flush()
        return order

    async def complete_production_order(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductionOrder:
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        order.status = "COMPLETED"
        order.actual_end_date = datetime.now(UTC)
        await self.session.flush()
        return order

    async def cancel_production_order(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductionOrder:
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        if order.status in ("COMPLETED", "CANCELLED"):
            raise BadRequestException(f"Cannot cancel order in status '{order.status}'.")
        order.status = "CANCELLED"
        await self.session.flush()
        return order

    async def update_work_order_status(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: WorkOrderUpdateStatus,
    ) -> WorkOrder:
        wo = await self.order_repo.get_work_order_by_id(wo_id, tenant_id, org_id, for_update=True)
        if not wo:
            raise NotFoundException(f"Work Order {wo_id} not found.")

        wo.status = data.status
        if data.technician_id:
            wo.technician_id = data.technician_id
        if data.notes:
            wo.notes = data.notes
        if data.actual_duration_hours is not None:
            wo.actual_duration_hours = data.actual_duration_hours
            wo.total_labor_cost = wo.actual_duration_hours * wo.hourly_rate

        if data.status == "IN_PROGRESS" and not wo.started_at:
            wo.started_at = datetime.now(UTC)
        elif data.status == "COMPLETED" and not wo.completed_at:
            wo.completed_at = datetime.now(UTC)
            if wo.actual_duration_hours == 0:
                wo.actual_duration_hours = wo.planned_duration_hours
                wo.total_labor_cost = wo.actual_duration_hours * wo.hourly_rate

        await self.session.flush()
        return wo

    async def record_material_consumption(
        self,
        order_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: MaterialConsumptionCreate,
        consumed_by_id: uuid.UUID | None = None,
    ) -> MaterialConsumption:
        """Deducts raw materials from inventory ledger and logs consumption against the production order."""
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        if order.status not in ("CONFIRMED", "IN_PROGRESS"):
            raise BadRequestException(
                f"Cannot consume materials for order in status '{order.status}'."
            )

        # 1. Fetch product to get cost
        product = await self.product_repo.get_by_id(data.product_id, tenant_id, org_id)
        if not product:
            raise NotFoundException(f"Product {data.product_id} not found.")

        unit_cost = getattr(
            product, "cost_price", getattr(product, "standard_cost", Decimal("10.0000"))
        ) or Decimal("10.0000")
        total_cost = data.consumed_quantity * unit_cost

        # 2. Record immutable Stock Movement via StockLedgerService (outflow is negative quantity)
        movement, _ = await self.stock_ledger.record_movement(
            tenant_id=tenant_id,
            org_id=org_id,
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            movement_type="MFG_CONSUMPTION",
            quantity=-abs(data.consumed_quantity),
            unit_cost=unit_cost,
            location_id=data.location_id,
            batch_number=data.batch_number,
            reference_doc_type="PRODUCTION_ORDER",
            reference_doc_id=order.id,
            created_by_id=consumed_by_id,
            notes=f"Raw material issuance for Production Order {order.order_number}",
        )

        # 3. Create Consumption Record
        consumption = MaterialConsumption(
            tenant_id=tenant_id,
            organization_id=org_id,
            production_order_id=order.id,
            work_order_id=data.work_order_id,
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            location_id=data.location_id,
            planned_quantity=data.consumed_quantity,
            consumed_quantity=data.consumed_quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            stock_movement_id=movement.id,
            batch_number=data.batch_number,
            consumed_by_id=consumed_by_id,
        )

        order.total_cost += total_cost
        if order.status == "CONFIRMED":
            order.status = "IN_PROGRESS"
            order.actual_start_date = datetime.now(UTC)

        await self.order_repo.create_consumption(consumption)
        await self.session.flush()
        return consumption

    async def record_production_output(
        self,
        order_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: ProductionOutputCreate,
        created_by_id: uuid.UUID | None = None,
    ) -> ProductionOutput:
        """Records finished goods output into inventory ledger with computed unit manufacturing cost."""
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")
        if order.status not in ("CONFIRMED", "IN_PROGRESS"):
            raise BadRequestException(f"Cannot record output for order in status '{order.status}'.")

        target_wh_id = data.target_warehouse_id or order.target_warehouse_id

        # 1. Calculate Unit Manufacturing Cost from consumed materials + work order labor
        total_material_cost = sum((c.total_cost for c in order.consumptions), Decimal("0.0000"))
        if total_material_cost == Decimal("0.0000") and order.total_cost > Decimal("0.0000"):
            total_material_cost = order.total_cost
        total_labor_cost = sum((w.total_labor_cost for w in order.work_orders), Decimal("0.0000"))
        total_accumulated_cost = total_material_cost + total_labor_cost

        new_total_produced = order.produced_quantity + data.produced_quantity
        if new_total_produced > 0 and total_accumulated_cost > 0:
            unit_mfg_cost = total_accumulated_cost / new_total_produced
        else:
            prod = await self.product_repo.get_by_id(order.product_id, tenant_id, org_id)
            unit_mfg_cost = (
                getattr(prod, "cost_price", getattr(prod, "standard_cost", Decimal("100.0000")))
                if prod
                else Decimal("100.0000")
            )

        total_output_cost = data.produced_quantity * unit_mfg_cost

        # 2. Record immutable Stock Movement via StockLedgerService (inflow is positive quantity)
        movement, _ = await self.stock_ledger.record_movement(
            tenant_id=tenant_id,
            org_id=org_id,
            product_id=order.product_id,
            warehouse_id=target_wh_id,
            movement_type="MFG_OUTPUT",
            quantity=data.produced_quantity,
            unit_cost=unit_mfg_cost,
            location_id=data.location_id,
            batch_number=data.batch_number,
            serial_number=data.serial_number,
            reference_doc_type="PRODUCTION_ORDER",
            reference_doc_id=order.id,
            created_by_id=created_by_id,
            notes=f"Finished goods receipt from Production Order {order.order_number}",
        )

        # 3. Create Output Record
        output = ProductionOutput(
            tenant_id=tenant_id,
            organization_id=org_id,
            production_order_id=order.id,
            product_id=order.product_id,
            target_warehouse_id=target_wh_id,
            location_id=data.location_id,
            produced_quantity=data.produced_quantity,
            unit_manufacturing_cost=unit_mfg_cost,
            total_manufacturing_cost=total_output_cost,
            stock_movement_id=movement.id,
            batch_number=data.batch_number,
            serial_number=data.serial_number,
        )

        order.produced_quantity = new_total_produced
        order.unit_cost = unit_mfg_cost
        order.total_cost = total_accumulated_cost

        if order.produced_quantity >= order.planned_quantity:
            order.status = "COMPLETED"
            order.actual_end_date = datetime.now(UTC)

        await self.order_repo.create_output(output)
        await self.session.flush()
        return output

    async def record_production_scrap(
        self,
        order_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: ProductionScrapCreate,
        recorded_by_id: uuid.UUID | None = None,
    ) -> ProductionScrap:
        """Records production waste/scrap and adjusts inventory accordingly."""
        order = await self.order_repo.get_order_by_id(order_id, tenant_id, org_id, for_update=True)
        if not order:
            raise NotFoundException(f"Production Order {order_id} not found.")

        product = await self.product_repo.get_by_id(data.product_id, tenant_id, org_id)
        unit_cost = (
            getattr(product, "cost_price", getattr(product, "standard_cost", Decimal("10.0000")))
            if product
            else Decimal("10.0000")
        )
        total_scrap_cost = data.scrap_quantity * unit_cost

        target_wh_id = data.warehouse_id or order.target_warehouse_id
        movement, _ = await self.stock_ledger.record_movement(
            tenant_id=tenant_id,
            org_id=org_id,
            product_id=data.product_id,
            warehouse_id=target_wh_id,
            movement_type="MFG_SCRAP",
            quantity=-abs(data.scrap_quantity),
            unit_cost=unit_cost,
            reference_doc_type="PRODUCTION_ORDER",
            reference_doc_id=order.id,
            created_by_id=recorded_by_id,
            notes=f"Scrap loss on Production Order {order.order_number}: {data.scrap_reason}",
        )

        scrap = ProductionScrap(
            tenant_id=tenant_id,
            organization_id=org_id,
            production_order_id=order.id,
            work_order_id=data.work_order_id,
            product_id=data.product_id,
            scrap_quantity=data.scrap_quantity,
            scrap_reason=data.scrap_reason,
            unit_cost=unit_cost,
            total_scrap_cost=total_scrap_cost,
            stock_movement_id=movement.id,
            recorded_by_id=recorded_by_id,
        )

        order.scrap_quantity += data.scrap_quantity
        await self.order_repo.create_scrap(scrap)
        await self.session.flush()
        return scrap
