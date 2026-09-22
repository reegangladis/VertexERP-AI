"""Procurement Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.procurement.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.modules.procurement.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.modules.procurement.repositories.purchase_order_repository import PurchaseOrderRepository
from app.modules.procurement.repositories.purchase_request_repository import (
    PurchaseRequestRepository,
)
from app.modules.procurement.repositories.supplier_repository import SupplierRepository
from app.modules.procurement.schemas.purchase_order import PurchaseOrderCreate
from app.modules.procurement.schemas.purchase_request import PurchaseRequestCreate


class ProcurementService:
    """Domain service for Purchase Requisitions, Supplier Orders, and Pricing Engine."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.pr_repo = PurchaseRequestRepository(session)
        self.po_repo = PurchaseOrderRepository(session)
        self.supplier_repo = SupplierRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.product_repo = ProductRepository(session)

    async def create_purchase_request(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: PurchaseRequestCreate,
        requester_id: uuid.UUID | None = None,
    ) -> PurchaseRequest:
        """Create a new Purchase Request with line items."""
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        request_number = f"PR-{timestamp_str}-{suffix}"

        estimated_grand_total = Decimal("0.00")
        pr = PurchaseRequest(
            tenant_id=tenant_id,
            organization_id=org_id,
            request_number=request_number,
            requester_id=requester_id,
            department_id=data.department_id,
            required_date=data.required_date,
            status="DRAFT",
            priority=data.priority,
            estimated_total=Decimal("0.00"),
            notes=data.notes,
            is_active=data.is_active,
        )

        for item_data in data.items:
            product = await self.product_repo.get_by_id(item_data.product_id, tenant_id, org_id)
            if not product:
                raise NotFoundException(f"Product {item_data.product_id} not found.")

            line_est = (item_data.quantity * item_data.estimated_unit_price).quantize(
                Decimal("0.01")
            )
            estimated_grand_total += line_est

            item = PurchaseRequestItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=item_data.product_id,
                uom_id=item_data.uom_id or product.uom_id,
                description=item_data.description,
                quantity=item_data.quantity,
                estimated_unit_price=item_data.estimated_unit_price,
                estimated_total=line_est,
                notes=item_data.notes,
            )
            pr.items.append(item)

        pr.estimated_total = estimated_grand_total
        await self.pr_repo.create(pr)
        return pr

    async def submit_purchase_request(
        self,
        request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> PurchaseRequest:
        """Submit a purchase request for approval."""
        pr = await self.pr_repo.get_by_id(request_id, tenant_id, org_id)
        if not pr:
            raise NotFoundException(f"Purchase Request {request_id} not found.")
        if pr.status not in ("DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot submit Purchase Request in '{pr.status}' status.")

        pr.status = "SUBMITTED"
        pr.version += 1
        await self.session.flush()
        return pr

    async def approve_purchase_request(
        self,
        request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> PurchaseRequest:
        """Approve a purchase request."""
        pr = await self.pr_repo.get_by_id(request_id, tenant_id, org_id)
        if not pr:
            raise NotFoundException(f"Purchase Request {request_id} not found.")
        if pr.status not in ("DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot approve Purchase Request in '{pr.status}' status.")

        pr.status = "APPROVED"
        pr.version += 1
        await self.session.flush()
        return pr

    async def reject_purchase_request(
        self,
        request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        reason: str = "",
    ) -> PurchaseRequest:
        """Reject a purchase request."""
        pr = await self.pr_repo.get_by_id(request_id, tenant_id, org_id)
        if not pr:
            raise NotFoundException(f"Purchase Request {request_id} not found.")
        if pr.status not in ("DRAFT", "SUBMITTED"):
            raise ConflictException(f"Cannot reject Purchase Request in '{pr.status}' status.")

        pr.status = "REJECTED"
        if reason:
            pr.notes = f"{pr.notes or ''}\nRejection Reason: {reason}".strip()
        pr.version += 1
        await self.session.flush()
        return pr

    async def create_purchase_order(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: PurchaseOrderCreate,
    ) -> PurchaseOrder:
        """Create a new Purchase Order with deterministic pricing calculations."""
        supplier = await self.supplier_repo.get_by_id(data.supplier_id, tenant_id, org_id)
        if not supplier:
            raise NotFoundException(f"Supplier {data.supplier_id} not found.")

        warehouse = await self.warehouse_repo.get_by_id(data.warehouse_id, tenant_id, org_id)
        if not warehouse:
            raise NotFoundException(f"Warehouse {data.warehouse_id} not found.")

        timestamp_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        po_number = f"PO-{timestamp_str}-{suffix}"

        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")
        total_tax = Decimal("0.00")

        po = PurchaseOrder(
            tenant_id=tenant_id,
            organization_id=org_id,
            po_number=po_number,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            purchase_request_id=data.purchase_request_id,
            order_date=data.order_date,
            expected_delivery_date=data.expected_delivery_date,
            payment_terms=data.payment_terms or supplier.payment_terms,
            currency=data.currency or supplier.currency,
            status="DRAFT",
            subtotal=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            grand_total=Decimal("0.00"),
            shipping_terms=data.shipping_terms,
            notes=data.notes,
            is_active=data.is_active,
        )

        for item_data in data.items:
            product = await self.product_repo.get_by_id(item_data.product_id, tenant_id, org_id)
            if not product:
                raise NotFoundException(f"Product {item_data.product_id} not found.")

            base_line = item_data.quantity_ordered * item_data.unit_price
            line_disc = base_line * (item_data.discount_pct / Decimal("100.00"))
            after_disc = base_line - line_disc
            line_tax = after_disc * (item_data.tax_pct / Decimal("100.00"))
            line_total = (after_disc + line_tax).quantize(Decimal("0.01"))

            subtotal += base_line
            total_discount += line_disc
            total_tax += line_tax

            item = PurchaseOrderItem(
                tenant_id=tenant_id,
                organization_id=org_id,
                product_id=item_data.product_id,
                uom_id=item_data.uom_id or product.uom_id,
                description=item_data.description,
                quantity_ordered=item_data.quantity_ordered,
                quantity_received=Decimal("0.0000"),
                quantity_billed=Decimal("0.0000"),
                unit_price=item_data.unit_price,
                discount_pct=item_data.discount_pct,
                tax_pct=item_data.tax_pct,
                line_total=line_total,
            )
            po.items.append(item)

        po.subtotal = subtotal.quantize(Decimal("0.01"))
        po.discount_amount = total_discount.quantize(Decimal("0.01"))
        po.tax_amount = total_tax.quantize(Decimal("0.01"))
        po.grand_total = (subtotal - total_discount + total_tax).quantize(Decimal("0.01"))

        await self.po_repo.create(po)
        return po

    async def approve_purchase_order(
        self,
        po_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        approved_by_id: uuid.UUID | None = None,
    ) -> PurchaseOrder:
        """Approve a Purchase Order and move to CONFIRMED status."""
        po = await self.po_repo.get_by_id(po_id, tenant_id, org_id)
        if not po:
            raise NotFoundException(f"Purchase Order {po_id} not found.")
        if po.status != "DRAFT":
            raise ConflictException(f"Cannot approve Purchase Order in '{po.status}' status.")

        po.status = "CONFIRMED"
        po.approved_by_id = approved_by_id
        po.approved_at = datetime.now(UTC)
        po.version += 1
        await self.session.flush()
        return po

    async def send_purchase_order(
        self,
        po_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> PurchaseOrder:
        """Mark a Purchase Order as SENT to vendor."""
        po = await self.po_repo.get_by_id(po_id, tenant_id, org_id)
        if not po:
            raise NotFoundException(f"Purchase Order {po_id} not found.")
        if po.status not in ("DRAFT", "CONFIRMED"):
            raise ConflictException(f"Cannot send Purchase Order in '{po.status}' status.")

        po.status = "SENT"
        po.version += 1
        await self.session.flush()
        return po

    async def cancel_purchase_order(
        self,
        po_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        reason: str = "",
    ) -> PurchaseOrder:
        """Cancel a Purchase Order."""
        po = await self.po_repo.get_by_id(po_id, tenant_id, org_id)
        if not po:
            raise NotFoundException(f"Purchase Order {po_id} not found.")
        if po.status in ("RECEIVED", "BILLED", "CANCELLED"):
            raise ConflictException(f"Cannot cancel Purchase Order in '{po.status}' status.")

        po.status = "CANCELLED"
        if reason:
            po.notes = f"{po.notes or ''}\nCancellation Reason: {reason}".strip()
        po.version += 1
        await self.session.flush()
        return po
