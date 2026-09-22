"""Stock Ledger Domain Service (Auditable Inventory Movement Engine)."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.inventory.models.stock_balance import StockBalance
from app.modules.inventory.models.stock_movement import StockMovement
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.repositories.stock_movement_repository import StockMovementRepository


class StockLedgerService:
    """Core domain service for all auditable inventory movements and real-time ledger accounting.

    Invariants:
    1. Stock is NEVER mutated directly without an immutable StockMovement entry.
    2. Atomic transaction boundaries prevent orphaned ledger lines.
    3. Prevents negative stock where disallowed by product configuration.
    4. Computes moving average cost on inflows and reduces total value on outflows.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.product_repo = ProductRepository(session)
        self.balance_repo = StockBalanceRepository(session)
        self.movement_repo = StockMovementRepository(session)

    async def record_movement(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID,
        movement_type: str,
        quantity: Decimal,  # Positive for inflow, negative for outflow
        unit_cost: Decimal = Decimal("0.0000"),
        location_id: uuid.UUID | None = None,
        batch_number: str | None = None,
        serial_number: str | None = None,
        expiry_date: date | None = None,
        reference_doc_type: str | None = None,
        reference_doc_id: uuid.UUID | None = None,
        reference_doc_line_id: uuid.UUID | None = None,
        created_by_id: uuid.UUID | None = None,
        notes: str | None = None,
    ) -> tuple[StockMovement, StockBalance]:
        """Atomically record an immutable stock movement and update the stock balance."""
        if quantity == 0:
            raise ValidationException("Movement quantity cannot be zero.")

        # 1. Fetch & validate Product
        product = await self.product_repo.get_by_id(product_id, tenant_id, org_id)
        if not product:
            raise NotFoundException(f"Product {product_id} not found in current organization.")
        if not product.is_stockable:
            raise ValidationException(
                f"Product '{product.sku}' is not configured as a stockable item."
            )

        # 2. Acquire StockBalance with row-level lock
        balance = await self.balance_repo.get_or_create(
            tenant_id=tenant_id,
            org_id=org_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            for_update=True,
        )

        current_qty = balance.quantity_on_hand
        current_avg_cost = balance.average_cost
        new_qty = current_qty + quantity

        # 3. Prevent negative stock where disallowed
        if new_qty < 0 and not product.allow_negative_stock:
            raise ValidationException(
                f"Negative stock violation for product '{product.sku}'. "
                f"Current on hand: {current_qty}, requested deduction: {abs(quantity)}, resulting stock: {new_qty}."
            )

        # 4. Valuation / Moving Average Cost computation
        if quantity > 0:
            # Inflow: update moving average cost
            if new_qty > 0:
                current_total_value = current_qty * current_avg_cost
                inflow_total_cost = quantity * unit_cost
                new_avg_cost = (current_total_value + inflow_total_cost) / new_qty
            else:
                new_avg_cost = unit_cost
            new_total_value = new_qty * new_avg_cost
        else:
            # Outflow: retain current average cost, reduce total value
            new_avg_cost = current_avg_cost
            new_total_value = max(Decimal("0.00"), new_qty * new_avg_cost)
            # Use current average cost if unit_cost is not provided
            if unit_cost == 0:
                unit_cost = current_avg_cost

        total_movement_cost = abs(quantity) * unit_cost

        # 5. Update StockBalance
        balance.quantity_on_hand = new_qty
        balance.quantity_available = max(
            Decimal("0.0000"), new_qty - balance.quantity_reserved - balance.quantity_allocated
        )
        balance.average_cost = new_avg_cost.quantize(Decimal("0.0001"))
        balance.total_value = new_total_value.quantize(Decimal("0.01"))
        balance.last_movement_at = datetime.now(UTC)
        balance.version += 1

        # 6. Generate movement number and insert immutable StockMovement
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        movement_number = f"MOV-{timestamp_str}-{suffix}"

        movement = StockMovement(
            tenant_id=tenant_id,
            organization_id=org_id,
            movement_number=movement_number,
            movement_type=movement_type,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            batch_number=batch_number,
            serial_number=serial_number,
            expiry_date=expiry_date,
            quantity=quantity,
            unit_cost=unit_cost.quantize(Decimal("0.0001")),
            total_cost=total_movement_cost.quantize(Decimal("0.01")),
            reference_doc_type=reference_doc_type,
            reference_doc_id=reference_doc_id,
            reference_doc_line_id=reference_doc_line_id,
            running_balance_qty=new_qty,
            running_balance_cost=new_avg_cost.quantize(Decimal("0.0001")),
            created_by_id=created_by_id,
            notes=notes,
        )
        await self.movement_repo.create(movement)
        await self.session.flush()

        return movement, balance
