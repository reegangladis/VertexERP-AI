"""Goods Receipt Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.inventory.models.goods_receipt import GoodsReceipt, GoodsReceiptItem
from app.modules.inventory.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.goods_receipt import GoodsReceiptCreate
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.procurement.repositories.purchase_order_repository import PurchaseOrderRepository
from app.modules.procurement.repositories.supplier_repository import SupplierRepository


class GoodsReceiptService:
    """Domain service for Goods Receipt Note (GRN) lifecycle and inbound stock intake."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.gr_repo = GoodsReceiptRepository(session)
        self.po_repo = PurchaseOrderRepository(session)
        self.supplier_repo = SupplierRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.ledger_service = StockLedgerService(session)

    async def create_goods_receipt(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: GoodsReceiptCreate,
        received_by_id: uuid.UUID | None = None,
    ) -> GoodsReceipt:
        """Create a new Goods Receipt in DRAFT status."""
        # 1. Validate Supplier & Warehouse
        supplier = await self.supplier_repo.get_by_id(data.supplier_id, tenant_id, org_id)
        if not supplier:
            raise NotFoundException(f"Supplier {data.supplier_id} not found.")

        warehouse = await self.warehouse_repo.get_by_id(data.warehouse_id, tenant_id, org_id)
        if not warehouse:
            raise NotFoundException(f"Warehouse {data.warehouse_id} not found.")

        # 2. If PO reference is supplied, validate PO exists
        if data.purchase_order_id:
            po = await self.po_repo.get_by_id(data.purchase_order_id, tenant_id, org_id)
            if not po:
                raise NotFoundException(f"Purchase Order {data.purchase_order_id} not found.")
            if po.status in ("DRAFT", "CANCELLED", "CLOSED"):
                raise ValidationException(
                    f"Cannot receive goods against Purchase Order in '{po.status}' status."
                )

        # 3. Generate receipt number
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        receipt_number = f"GRN-{timestamp_str}-{suffix}"

        gr = GoodsReceipt(
            tenant_id=tenant_id,
            organization_id=org_id,
            receipt_number=receipt_number,
            purchase_order_id=data.purchase_order_id,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            receipt_date=data.receipt_date,
            vendor_delivery_note=data.vendor_delivery_note,
            status="DRAFT",
            notes=data.notes,
            received_by_id=received_by_id,
            is_active=data.is_active,
        )

        for item_data in data.items:
            total_item_cost = (item_data.quantity_accepted * item_data.unit_cost).quantize(
                Decimal("0.01")
            )
            gr_item = GoodsReceiptItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                po_item_id=item_data.po_item_id,
                product_id=item_data.product_id,
                location_id=item_data.location_id,
                quantity_received=item_data.quantity_received,
                quantity_accepted=item_data.quantity_accepted,
                quantity_rejected=item_data.quantity_rejected,
                rejection_reason=item_data.rejection_reason,
                unit_cost=item_data.unit_cost,
                total_cost=total_item_cost,
                batch_number=item_data.batch_number,
                serial_number=item_data.serial_number,
                expiry_date=item_data.expiry_date,
            )
            gr.items.append(gr_item)

        await self.gr_repo.create(gr)
        return gr

    async def post_goods_receipt(
        self,
        receipt_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        posted_by_id: uuid.UUID | None = None,
    ) -> GoodsReceipt:
        """Atomically post a Goods Receipt, record stock movements, and update PO received quantities.

        Strict Invariants:
        1. Prevents double-posting / idempotent execution.
        2. Prevents double-receiving or over-receiving on Purchase Orders.
        3. Transactionally records stock ledger inflows and updates balances.
        """
        gr = await self.gr_repo.get_by_id(receipt_id, tenant_id, org_id)
        if not gr:
            raise NotFoundException(f"Goods Receipt {receipt_id} not found.")

        if gr.status != "DRAFT":
            raise ConflictException(
                f"Goods Receipt {gr.receipt_number} is already '{gr.status}' and cannot be posted again."
            )

        # If linked to Purchase Order, validate PO and line receiving limits
        po = None
        if gr.purchase_order_id:
            po = await self.po_repo.get_by_id(gr.purchase_order_id, tenant_id, org_id)
            if not po:
                raise NotFoundException(f"Linked Purchase Order {gr.purchase_order_id} not found.")

            po_items_map = {item.id: item for item in po.items}
            for gr_item in gr.items:
                if gr_item.po_item_id and gr_item.po_item_id in po_items_map:
                    po_item = po_items_map[gr_item.po_item_id]
                    potential_received = po_item.quantity_received + gr_item.quantity_accepted
                    if potential_received > po_item.quantity_ordered:
                        raise ValidationException(
                            f"Over-receiving prevented for product on PO {po.po_number}. "
                            f"Ordered: {po_item.quantity_ordered}, Already Received: {po_item.quantity_received}, "
                            f"Attempting to accept: {gr_item.quantity_accepted}."
                        )
                    # Update PO item received quantity
                    po_item.quantity_received = potential_received

        # Record stock movement for each accepted item in the receipt
        for gr_item in gr.items:
            if gr_item.quantity_accepted > 0:
                await self.ledger_service.record_movement(
                    tenant_id=tenant_id,
                    org_id=org_id,
                    product_id=gr_item.product_id,
                    warehouse_id=gr.warehouse_id,
                    location_id=gr_item.location_id,
                    movement_type="PURCHASE_RECEIPT",
                    quantity=gr_item.quantity_accepted,
                    unit_cost=gr_item.unit_cost,
                    batch_number=gr_item.batch_number,
                    serial_number=gr_item.serial_number,
                    expiry_date=gr_item.expiry_date,
                    reference_doc_type="GOODS_RECEIPT",
                    reference_doc_id=gr.id,
                    reference_doc_line_id=gr_item.id,
                    created_by_id=posted_by_id,
                    notes=f"GRN receipt {gr.receipt_number}",
                )

        # Update PO Status if all lines fully received
        if po:
            all_received = all(item.quantity_received >= item.quantity_ordered for item in po.items)
            any_received = any(item.quantity_received > 0 for item in po.items)
            if all_received:
                po.status = "RECEIVED"
            elif any_received:
                po.status = "PARTIALLY_RECEIVED"

        # Mark Goods Receipt as POSTED
        gr.status = "POSTED"
        gr.posted_by_id = posted_by_id
        gr.posted_at = datetime.now(UTC)
        gr.version += 1

        await self.session.flush()
        return gr
