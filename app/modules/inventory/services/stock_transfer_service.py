"""Stock Transfer Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.inventory.models.stock_transfer import StockTransfer, StockTransferItem
from app.modules.inventory.repositories.stock_transfer_repository import StockTransferRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_transfer import StockTransferCreate
from app.modules.inventory.services.stock_ledger_service import StockLedgerService


class StockTransferService:
    """Domain service for Inter-Warehouse and Bin-to-Bin stock transfers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.transfer_repo = StockTransferRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.ledger_service = StockLedgerService(session)

    async def create_transfer(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: StockTransferCreate,
        created_by_id: uuid.UUID | None = None,
    ) -> StockTransfer:
        """Create a new stock transfer order in DRAFT status."""
        if data.from_warehouse_id == data.to_warehouse_id:
            # Transfer within same warehouse is allowed if from_location != to_location
            pass

        from_wh = await self.warehouse_repo.get_by_id(data.from_warehouse_id, tenant_id, org_id)
        if not from_wh:
            raise NotFoundException(f"Source Warehouse {data.from_warehouse_id} not found.")

        to_wh = await self.warehouse_repo.get_by_id(data.to_warehouse_id, tenant_id, org_id)
        if not to_wh:
            raise NotFoundException(f"Destination Warehouse {data.to_warehouse_id} not found.")

        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        transfer_number = f"TRF-{timestamp_str}-{suffix}"

        transfer = StockTransfer(
            tenant_id=tenant_id,
            organization_id=org_id,
            transfer_number=transfer_number,
            from_warehouse_id=data.from_warehouse_id,
            to_warehouse_id=data.to_warehouse_id,
            status="DRAFT",
            transfer_date=data.transfer_date,
            expected_arrival_date=data.expected_arrival_date,
            created_by_id=created_by_id,
            notes=data.notes,
            is_active=data.is_active,
        )

        for item_data in data.items:
            total_cost = (item_data.quantity * item_data.unit_cost).quantize(Decimal("0.01"))
            item = StockTransferItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=item_data.product_id,
                from_location_id=item_data.from_location_id,
                to_location_id=item_data.to_location_id,
                quantity=item_data.quantity,
                unit_cost=item_data.unit_cost,
                total_cost=total_cost,
                batch_number=item_data.batch_number,
            )
            transfer.items.append(item)

        await self.transfer_repo.create(transfer)
        return transfer

    async def ship_transfer(
        self,
        transfer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> StockTransfer:
        """Ship the transfer: deducts stock from source warehouse and marks IN_TRANSIT."""
        transfer = await self.transfer_repo.get_by_id(transfer_id, tenant_id, org_id)
        if not transfer:
            raise NotFoundException(f"Stock Transfer {transfer_id} not found.")

        if transfer.status != "DRAFT":
            raise ConflictException(
                f"Cannot ship transfer in '{transfer.status}' status (must be 'DRAFT')."
            )

        # Record TRANSFER_OUT movement from source warehouse
        for item in transfer.items:
            await self.ledger_service.record_movement(
                tenant_id=tenant_id,
                org_id=org_id,
                product_id=item.product_id,
                warehouse_id=transfer.from_warehouse_id,
                location_id=item.from_location_id,
                movement_type="TRANSFER_OUT",
                quantity=-item.quantity,
                unit_cost=item.unit_cost,
                batch_number=item.batch_number,
                reference_doc_type="STOCK_TRANSFER",
                reference_doc_id=transfer.id,
                reference_doc_line_id=item.id,
                created_by_id=user_id,
                notes=f"Ship transfer {transfer.transfer_number}",
            )

        transfer.status = "IN_TRANSIT"
        transfer.shipped_at = datetime.now(UTC)
        transfer.version += 1
        await self.session.flush()
        return transfer

    async def complete_transfer(
        self,
        transfer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> StockTransfer:
        """Complete the transfer: receives stock into destination warehouse and marks COMPLETED."""
        transfer = await self.transfer_repo.get_by_id(transfer_id, tenant_id, org_id)
        if not transfer:
            raise NotFoundException(f"Stock Transfer {transfer_id} not found.")

        if transfer.status != "IN_TRANSIT":
            raise ConflictException(
                f"Cannot complete transfer in '{transfer.status}' status (must be 'IN_TRANSIT')."
            )

        # Record TRANSFER_IN movement into destination warehouse
        for item in transfer.items:
            await self.ledger_service.record_movement(
                tenant_id=tenant_id,
                org_id=org_id,
                product_id=item.product_id,
                warehouse_id=transfer.to_warehouse_id,
                location_id=item.to_location_id,
                movement_type="TRANSFER_IN",
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                batch_number=item.batch_number,
                reference_doc_type="STOCK_TRANSFER",
                reference_doc_id=transfer.id,
                reference_doc_line_id=item.id,
                created_by_id=user_id,
                notes=f"Receive transfer {transfer.transfer_number}",
            )

        transfer.status = "COMPLETED"
        transfer.received_at = datetime.now(UTC)
        transfer.version += 1
        await self.session.flush()
        return transfer
