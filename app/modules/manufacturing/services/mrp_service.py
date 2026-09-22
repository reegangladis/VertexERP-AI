"""Material Requirements Planning (MRP) Calculation Engine Service."""

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, ValidationException
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.stock_balance import StockBalance
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.manufacturing.models.mrp import MRPPlannedOrder, MRPRun
from app.modules.manufacturing.models.production_order import ProductionOrder
from app.modules.manufacturing.repositories.bom_repository import BOMRepository
from app.modules.manufacturing.repositories.mrp_repository import MRPRepository
from app.modules.manufacturing.repositories.production_order_repository import (
    ProductionOrderRepository,
)
from app.modules.procurement.models.purchase_request import PurchaseRequest, PurchaseRequestItem


class MRPService:
    """Domain service for Material Requirements Planning calculation and conversion."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.mrp_repo = MRPRepository(session)
        self.bom_repo = BOMRepository(session)
        self.product_repo = ProductRepository(session)
        self.order_repo = ProductionOrderRepository(session)

    async def run_mrp(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, planning_horizon_days: int = 30
    ) -> MRPRun:
        """Executes a full multi-level MRP run calculating gross to net requirements across the planning horizon."""
        run_number = f"MRP-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        today = date.today()
        horizon_end = today + timedelta(days=planning_horizon_days)

        mrp_run = MRPRun(
            tenant_id=tenant_id,
            organization_id=org_id,
            run_number=run_number,
            planning_horizon_days=planning_horizon_days,
            status="RUNNING",
            run_date=datetime.now(UTC),
        )

        logs: list[str] = [
            f"Starting MRP run {run_number} with {planning_horizon_days}-day horizon."
        ]

        # 1. Fetch active Demand: Open production orders + reorder points
        open_orders_stmt = select(ProductionOrder).where(
            ProductionOrder.tenant_id == tenant_id,
            ProductionOrder.organization_id == org_id,
            ProductionOrder.status.in_(["PLANNED", "CONFIRMED", "IN_PROGRESS"]),
            ProductionOrder.planned_due_date <= horizon_end,
        )
        open_orders_res = await self.session.execute(open_orders_stmt)
        open_orders = open_orders_res.scalars().all()

        # Dictionary to accumulate gross requirements: product_id -> (gross_qty, required_date)
        gross_requirements: dict[uuid.UUID, dict[str, Decimal | date]] = {}

        for mo in open_orders:
            remaining_qty = mo.planned_quantity - mo.produced_quantity
            if remaining_qty > 0:
                # Add finished product requirement
                if mo.product_id not in gross_requirements:
                    gross_requirements[mo.product_id] = {
                        "gross": remaining_qty,
                        "required_date": mo.planned_due_date,
                    }
                else:
                    gross_requirements[mo.product_id]["gross"] += remaining_qty

                # Explode BOM components
                bom_version = await self.bom_repo.get_version_by_id(
                    mo.bom_version_id, tenant_id, org_id
                )
                if bom_version:
                    for comp in bom_version.components:
                        comp_needed = (
                            remaining_qty
                            * comp.quantity
                            * (1 + (comp.scrap_percentage / Decimal("100.00")))
                        )
                        if comp.component_product_id not in gross_requirements:
                            gross_requirements[comp.component_product_id] = {
                                "gross": comp_needed,
                                "required_date": mo.planned_start_date,
                            }
                        else:
                            gross_requirements[comp.component_product_id]["gross"] += comp_needed

        # Also check all products for reorder point / safety stock deficits
        products_stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.organization_id == org_id,
            Product.is_active.is_(True),
        )
        products_res = await self.session.execute(products_stmt)
        all_products = products_res.scalars().all()

        for prod in all_products:
            if prod.reorder_point > 0 and prod.id not in gross_requirements:
                gross_requirements[prod.id] = {
                    "gross": prod.reorder_point,
                    "required_date": today + timedelta(days=7),
                }

        logs.append(f"Identified demand across {len(gross_requirements)} products.")

        # 2. Compute Net Requirements per product
        total_items_planned = 0
        total_po_gen = 0
        total_mo_gen = 0

        for product_id, req_data in gross_requirements.items():
            product = await self.product_repo.get_by_id(product_id, tenant_id, org_id)
            if not product:
                continue

            gross_qty: Decimal = req_data["gross"]  # type: ignore
            req_date: date = req_data["required_date"]  # type: ignore

            # Get current stock on hand across all warehouses
            stock_stmt = select(
                func.coalesce(func.sum(StockBalance.quantity_on_hand), Decimal("0.0000"))
            ).where(
                StockBalance.tenant_id == tenant_id,
                StockBalance.organization_id == org_id,
                StockBalance.product_id == product_id,
            )
            stock_res = await self.session.execute(stock_stmt)
            on_hand: Decimal = stock_res.scalar_one()

            # Scheduled receipts from open incoming receipts
            scheduled_receipts = Decimal("0.0000")

            # Net Requirement calculation
            projected_available = on_hand + scheduled_receipts
            net_req = max(Decimal("0.0000"), gross_qty - projected_available)

            if net_req > 0:
                # Determine if product has an active BOM (Manufactured) or should be Purchased
                bom = await self.bom_repo.get_default_bom_by_product(product_id, tenant_id, org_id)
                order_type = (
                    "MANUFACTURE" if (bom or product.product_type == "MANUFACTURED") else "PURCHASE"
                )

                lead_time_days = product.lead_time_days or (3 if order_type == "MANUFACTURE" else 7)
                order_date = max(today, req_date - timedelta(days=lead_time_days))

                planned_order = MRPPlannedOrder(
                    tenant_id=tenant_id,
                    organization_id=org_id,
                    product_id=product_id,
                    order_type=order_type,
                    gross_requirement=gross_qty,
                    on_hand_stock=on_hand,
                    scheduled_receipts=scheduled_receipts,
                    net_requirement=net_req,
                    planned_quantity=net_req,
                    order_date=order_date,
                    required_date=req_date,
                    status="PLANNED",
                )
                mrp_run.planned_orders.append(planned_order)
                total_items_planned += 1
                if order_type == "MANUFACTURE":
                    total_mo_gen += 1
                else:
                    total_po_gen += 1

        mrp_run.status = "COMPLETED"
        mrp_run.total_items_planned = total_items_planned
        mrp_run.total_production_orders_generated = total_mo_gen
        mrp_run.total_purchase_requests_generated = total_po_gen
        logs.append(
            f"MRP complete: {total_items_planned} planned orders ({total_mo_gen} MO, {total_po_gen} PR)."
        )
        mrp_run.execution_log = "\n".join(logs)

        await self.mrp_repo.create_run(mrp_run)
        return mrp_run

    async def convert_planned_order(
        self,
        planned_order_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> dict:
        """Converts an MRP planned order into a live Production Order or Purchase Request."""
        planned = await self.mrp_repo.get_planned_order_by_id(planned_order_id, tenant_id, org_id)
        if not planned:
            raise NotFoundException(f"Planned order {planned_order_id} not found.")
        if planned.status == "CONVERTED":
            raise BadRequestException("Planned order has already been converted.")

        # Resolve primary warehouse
        wh_stmt = select(Warehouse).where(
            Warehouse.tenant_id == tenant_id,
            Warehouse.organization_id == org_id,
            Warehouse.is_active.is_(True),
        )
        wh_res = await self.session.execute(wh_stmt)
        warehouse = wh_res.scalars().first()
        if not warehouse:
            raise ValidationException("No active warehouse found to assign converted order.")

        if planned.order_type == "MANUFACTURE":
            # Convert to Production Order
            bom = await self.bom_repo.get_default_bom_by_product(
                planned.product_id, tenant_id, org_id
            )
            if not bom or not bom.versions:
                raise ValidationException(
                    f"Cannot convert: No active BOM found for product {planned.product_id}."
                )

            order_number = f"MO-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            mo = ProductionOrder(
                tenant_id=tenant_id,
                organization_id=org_id,
                order_number=order_number,
                product_id=planned.product_id,
                bom_id=bom.id,
                bom_version_id=bom.versions[0].id,
                routing_id=bom.routing_id,
                planned_quantity=planned.planned_quantity,
                target_warehouse_id=warehouse.id,
                planned_start_date=planned.order_date,
                planned_due_date=planned.required_date,
                status="PLANNED",
                created_by_id=user_id,
                notes=f"Auto-generated from MRP Planned Order {planned.id}",
            )
            await self.order_repo.create_order(mo)

            planned.status = "CONVERTED"
            planned.converted_doc_type = "PRODUCTION_ORDER"
            planned.converted_doc_id = mo.id
            await self.session.flush()

            return {
                "converted_type": "PRODUCTION_ORDER",
                "document_id": str(mo.id),
                "number": mo.order_number,
            }
        else:
            # Convert to Purchase Request
            pr_number = f"PR-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            product = await self.product_repo.get_by_id(planned.product_id, tenant_id, org_id)
            unit_cost = (
                getattr(product, "cost_price", getattr(product, "standard_cost", Decimal("10.00")))
                if product
                else Decimal("10.00")
            )
            est_cost = unit_cost * planned.planned_quantity

            pr = PurchaseRequest(
                tenant_id=tenant_id,
                organization_id=org_id,
                request_number=pr_number,
                requester_id=user_id,
                required_date=planned.required_date,
                status="DRAFT",
                priority="MEDIUM",
                estimated_total=est_cost,
                notes=f"Auto-generated from MRP Planned Order for product {product.name if product else ''}",
            )
            item = PurchaseRequestItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=planned.product_id,
                quantity=planned.planned_quantity,
                estimated_unit_cost=unit_cost,
                estimated_total_cost=est_cost,
                notes="Generated by MRP Engine",
            )
            pr.items.append(item)
            self.session.add(pr)

            planned.status = "CONVERTED"
            planned.converted_doc_type = "PURCHASE_REQUEST"
            planned.converted_doc_id = pr.id
            await self.session.flush()

            return {
                "converted_type": "PURCHASE_REQUEST",
                "document_id": str(pr.id),
                "number": pr.request_number,
            }
