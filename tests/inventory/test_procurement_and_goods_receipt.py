"""Tests for Procurement, Purchase Orders, Goods Receipts, and Double-Receiving Prevention."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ValidationException
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.schemas.goods_receipt import GoodsReceiptCreate, GoodsReceiptItemCreate
from app.modules.inventory.services.goods_receipt_service import GoodsReceiptService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant
from app.modules.procurement.models.supplier import Supplier
from app.modules.procurement.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderItemCreate,
)
from app.modules.procurement.schemas.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestItemCreate,
)
from app.modules.procurement.services.procurement_service import ProcurementService


@pytest.fixture
async def procurement_fixture(db_session: AsyncSession):
    """Sets up prerequisite master data for procurement and receiving."""
    tenant = Tenant(name="Global Supply", slug=f"supply-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        tenant_id=tenant.id,
        name="Procurement Division",
        legal_name="Global Procurement Corp",
        tax_identifier=f"PROC-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org)
    await db_session.flush()

    uom = UnitOfMeasure(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="BOX",
        name="Box of 10",
        category="COUNT",
    )
    db_session.add(uom)
    await db_session.flush()

    wh = Warehouse(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-NORTH",
        name="North Receiving Hub",
    )
    db_session.add(wh)
    await db_session.flush()

    prod = Product(
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="SKU-WIDGET-PRO",
        name="Widget Professional Edition",
        uom_id=uom.id,
        cost_price=Decimal("100.00"),
        selling_price=Decimal("200.00"),
        allow_negative_stock=False,
    )
    supplier = Supplier(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="SUPP-TECH-01",
        name="TechComponents Ltd",
        email="orders@techcomponents.com",
    )
    db_session.add_all([prod, supplier])
    await db_session.flush()

    return {
        "tenant": tenant,
        "org": org,
        "uom": uom,
        "warehouse": wh,
        "product": prod,
        "supplier": supplier,
    }


@pytest.mark.asyncio
async def test_full_procurement_and_goods_receipt_workflow(
    db_session: AsyncSession, procurement_fixture
):
    """Verifies end-to-end PR -> PO -> GR workflow and stock inflow."""
    tenant = procurement_fixture["tenant"]
    org = procurement_fixture["org"]
    wh = procurement_fixture["warehouse"]
    prod = procurement_fixture["product"]
    supplier = procurement_fixture["supplier"]

    proc_service = ProcurementService(db_session)
    gr_service = GoodsReceiptService(db_session)
    balance_repo = StockBalanceRepository(db_session)

    # 1. Create Purchase Request
    pr_data = PurchaseRequestCreate(
        required_date="2026-10-01",
        priority="HIGH",
        notes="Urgent inventory replenishment",
        items=[
            PurchaseRequestItemCreate(
                product_id=prod.id,
                description="Widget Pro box",
                quantity=Decimal("50.0000"),
                estimated_unit_price=Decimal("100.00"),
            )
        ],
    )
    pr = await proc_service.create_purchase_request(tenant.id, org.id, pr_data)
    assert pr.status == "DRAFT"
    assert pr.estimated_total == Decimal("5000.00")

    # 2. Approve Purchase Request
    pr = await proc_service.approve_purchase_request(pr.id, tenant.id, org.id)
    assert pr.status == "APPROVED"

    # 3. Create Purchase Order with 10% discount and 5% tax
    po_data = PurchaseOrderCreate(
        supplier_id=supplier.id,
        warehouse_id=wh.id,
        purchase_request_id=pr.id,
        order_date="2026-09-08",
        expected_delivery_date="2026-09-15",
        items=[
            PurchaseOrderItemCreate(
                product_id=prod.id,
                description="Widget Pro box",
                quantity_ordered=Decimal("50.0000"),
                unit_price=Decimal("100.00"),
                discount_pct=Decimal("10.00"),  # $500 discount
                tax_pct=Decimal("5.00"),  # $225 tax on $4500
            )
        ],
    )
    po = await proc_service.create_purchase_order(tenant.id, org.id, po_data)
    assert po.subtotal == Decimal("5000.00")
    assert po.discount_amount == Decimal("500.00")
    assert po.tax_amount == Decimal("225.00")
    assert po.grand_total == Decimal("4725.00")

    # 4. Approve and Send PO
    po = await proc_service.approve_purchase_order(po.id, tenant.id, org.id)
    assert po.status == "CONFIRMED"
    po = await proc_service.send_purchase_order(po.id, tenant.id, org.id)
    assert po.status == "SENT"

    # 5. Create Goods Receipt for full quantity
    po_item = po.items[0]
    gr_data = GoodsReceiptCreate(
        supplier_id=supplier.id,
        warehouse_id=wh.id,
        purchase_order_id=po.id,
        receipt_date="2026-09-10",
        items=[
            GoodsReceiptItemCreate(
                product_id=prod.id,
                po_item_id=po_item.id,
                quantity_received=Decimal("50.0000"),
                quantity_accepted=Decimal("50.0000"),
                quantity_rejected=Decimal("0.0000"),
                unit_cost=Decimal("94.50"),  # Net cost per box (4725 / 50)
            )
        ],
    )
    gr = await gr_service.create_goods_receipt(tenant.id, org.id, gr_data)
    assert gr.status == "DRAFT"

    # 6. Post Goods Receipt
    gr_posted = await gr_service.post_goods_receipt(gr.id, tenant.id, org.id)
    assert gr_posted.status == "POSTED"
    assert po.status == "RECEIVED"
    assert po_item.quantity_received == Decimal("50.0000")

    # Verify StockBalance was updated
    balance = await balance_repo.get_by_dimension(tenant.id, org.id, prod.id, wh.id)
    assert balance is not None
    assert balance.quantity_on_hand == Decimal("50.0000")
    assert balance.average_cost == Decimal("94.5000")
    assert balance.total_value == Decimal("4725.00")


@pytest.mark.asyncio
async def test_over_receiving_and_double_receiving_prevention(
    db_session: AsyncSession, procurement_fixture
):
    """Verifies that over-receiving beyond PO quantity is rejected."""
    tenant = procurement_fixture["tenant"]
    org = procurement_fixture["org"]
    wh = procurement_fixture["warehouse"]
    prod = procurement_fixture["product"]
    supplier = procurement_fixture["supplier"]

    proc_service = ProcurementService(db_session)
    gr_service = GoodsReceiptService(db_session)

    # Create PO for 20 units
    po_data = PurchaseOrderCreate(
        supplier_id=supplier.id,
        warehouse_id=wh.id,
        items=[
            PurchaseOrderItemCreate(
                product_id=prod.id,
                description="Widget Pro",
                quantity_ordered=Decimal("20.0000"),
                unit_price=Decimal("100.00"),
            )
        ],
    )
    po = await proc_service.create_purchase_order(tenant.id, org.id, po_data)
    await proc_service.approve_purchase_order(po.id, tenant.id, org.id)
    po_item = po.items[0]

    # Attempt to receive 25 units (exceeds ordered quantity of 20)
    gr_data = GoodsReceiptCreate(
        supplier_id=supplier.id,
        warehouse_id=wh.id,
        purchase_order_id=po.id,
        items=[
            GoodsReceiptItemCreate(
                product_id=prod.id,
                po_item_id=po_item.id,
                quantity_received=Decimal("25.0000"),
                quantity_accepted=Decimal("25.0000"),
                unit_cost=Decimal("100.00"),
            )
        ],
    )
    gr = await gr_service.create_goods_receipt(tenant.id, org.id, gr_data)

    with pytest.raises(ValidationException) as exc_info:
        await gr_service.post_goods_receipt(gr.id, tenant.id, org.id)
    assert "Over-receiving prevented" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_double_posting_goods_receipt_rejected(db_session: AsyncSession, procurement_fixture):
    """Verifies that posting an already-posted Goods Receipt raises ConflictException."""
    tenant = procurement_fixture["tenant"]
    org = procurement_fixture["org"]
    wh = procurement_fixture["warehouse"]
    prod = procurement_fixture["product"]
    supplier = procurement_fixture["supplier"]

    gr_service = GoodsReceiptService(db_session)

    gr_data = GoodsReceiptCreate(
        supplier_id=supplier.id,
        warehouse_id=wh.id,
        items=[
            GoodsReceiptItemCreate(
                product_id=prod.id,
                quantity_received=Decimal("10.0000"),
                quantity_accepted=Decimal("10.0000"),
                unit_cost=Decimal("50.00"),
            )
        ],
    )
    gr = await gr_service.create_goods_receipt(tenant.id, org.id, gr_data)
    await gr_service.post_goods_receipt(gr.id, tenant.id, org.id)

    # Attempt to post a second time
    with pytest.raises(ConflictException) as exc_info:
        await gr_service.post_goods_receipt(gr.id, tenant.id, org.id)
    assert "cannot be posted again" in str(exc_info.value.detail)
