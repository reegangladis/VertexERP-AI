"""Stock Adjustment Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.inventory.models.stock_adjustment import StockAdjustment, StockAdjustmentItem
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.stock_adjustment_repository import StockAdjustmentRepository
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_adjustment import StockAdjustmentCreate
from app.modules.inventory.services.stock_ledger_service import StockLedgerService


class StockAdjustmentService:
    """Domain service for physical count variance adjustments and write-offs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.adjustment_repo = StockAdjustmentRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.product_repo = ProductRepository(session)
        self.balance_repo = StockBalanceRepository(session)
        self.ledger_service = StockLedgerService(session)

    async def create_adjustment(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: StockAdjustmentCreate,
        requested_by_id: uuid.UUID | None = None,
    ) -> StockAdjustment:
        """Create a new stock adjustment draft."""
        warehouse = await self.warehouse_repo.get_by_id(data.warehouse_id, tenant_id, org_id)
        if not warehouse:
            raise NotFoundException(f"Warehouse {data.warehouse_id} not found.")

        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        adjustment_number = f"ADJ-{timestamp_str}-{suffix}"

        adj = StockAdjustment(
            tenant_id=tenant_id,
            organization_id=org_id,
            adjustment_number=adjustment_number,
            warehouse_id=data.warehouse_id,
            reason=data.reason,
            status="DRAFT",
            adjustment_date=data.adjustment_date,
            requested_by_id=requested_by_id,
            notes=data.notes,
            is_active=data.is_active,
        )

        for item_data in data.items:
            # If system_quantity wasn't provided, auto-fetch current on-hand
            balance = await self.balance_repo.get_by_dimension(
                tenant_id=tenant_id,
                org_id=org_id,
                product_id=item_data.product_id,
                warehouse_id=data.warehouse_id,
                location_id=item_data.location_id,
            )
            sys_qty = balance.quantity_on_hand if balance else item_data.system_quantity
            diff_qty = item_data.counted_quantity - sys_qty
            adj_type = "INCREASE" if diff_qty >= 0 else "DECREASE"
            total_val = (abs(diff_qty) * item_data.unit_cost).quantize(Decimal("0.01"))

            item = StockAdjustmentItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=item_data.product_id,
                location_id=item_data.location_id,
                system_quantity=sys_qty,
                counted_quantity=item_data.counted_quantity,
                difference_quantity=diff_qty,
                unit_cost=item_data.unit_cost,
                total_adjustment_value=total_val,
                adjustment_type=adj_type,
                batch_number=item_data.batch_number,
            )
            adj.items.append(item)

        await self.adjustment_repo.create(adj)
        return adj

    async def submit_adjustment(
        self,
        adjustment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> StockAdjustment:
        """Submit a draft adjustment for managerial review."""
        adj = await self.adjustment_repo.get_by_id(adjustment_id, tenant_id, org_id)
        if not adj:
            raise NotFoundException(f"Stock Adjustment {adjustment_id} not found.")
        if adj.status != "DRAFT":
            raise ConflictException(f"Cannot submit adjustment in '{adj.status}' status.")

        adj.status = "SUBMITTED"
        adj.version += 1
        await self.session.flush()
        return adj

    async def approve_adjustment(
        self,
        adjustment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        approved_by_id: uuid.UUID | None = None,
    ) -> StockAdjustment:
        """Approve a submitted adjustment."""
        adj = await self.adjustment_repo.get_by_id(adjustment_id, tenant_id, org_id)
        if not adj:
            raise NotFoundException(f"Stock Adjustment {adjustment_id} not found.")
        if adj.status not in ("DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot approve adjustment in '{adj.status}' status.")

        adj.status = "APPROVED"
        adj.approved_by_id = approved_by_id
        adj.version += 1
        await self.session.flush()
        return adj

    async def reject_adjustment(
        self,
        adjustment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        rejected_by_id: uuid.UUID | None = None,
        reason: str | None = None,
    ) -> StockAdjustment:
        """Reject a draft or submitted adjustment."""
        adj = await self.adjustment_repo.get_by_id(adjustment_id, tenant_id, org_id)
        if not adj:
            raise NotFoundException(f"Stock Adjustment {adjustment_id} not found.")
        if adj.status not in ("DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot reject adjustment in '{adj.status}' status.")

        adj.status = "REJECTED"
        if reason:
            adj.notes = f"{adj.notes or ''} [Rejected: {reason}]".strip()
        adj.version += 1
        await self.session.flush()
        return adj

    async def post_adjustment(
        self,
        adjustment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        posted_by_id: uuid.UUID | None = None,
    ) -> StockAdjustment:
        """Atomically post approved adjustment into stock ledger."""
        adj = await self.adjustment_repo.get_by_id(adjustment_id, tenant_id, org_id)
        if not adj:
            raise NotFoundException(f"Stock Adjustment {adjustment_id} not found.")
        if adj.status not in ("APPROVED", "DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot post adjustment in '{adj.status}' status.")

        for item in adj.items:
            if item.difference_quantity == 0:
                continue

            movement_type = "ADJUSTMENT_IN" if item.difference_quantity > 0 else "ADJUSTMENT_OUT"
            await self.ledger_service.record_movement(
                tenant_id=tenant_id,
                org_id=org_id,
                product_id=item.product_id,
                warehouse_id=adj.warehouse_id,
                location_id=item.location_id,
                movement_type=movement_type,
                quantity=item.difference_quantity,
                unit_cost=item.unit_cost,
                batch_number=item.batch_number,
                reference_doc_type="STOCK_ADJUSTMENT",
                reference_doc_id=adj.id,
                reference_doc_line_id=item.id,
                created_by_id=posted_by_id,
                notes=f"Stock adjustment {adj.adjustment_number} ({adj.reason})",
            )

        adj.status = "POSTED"
        adj.posted_at = datetime.now(UTC)
        if not adj.approved_by_id:
            adj.approved_by_id = posted_by_id
        adj.version += 1
        await self.session.flush()
        return adj
