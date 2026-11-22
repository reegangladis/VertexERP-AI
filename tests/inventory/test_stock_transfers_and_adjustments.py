"""Tests for Stock Transfers and Stock Adjustments."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.schemas.stock_adjustment import (
    StockAdjustmentCreate,
    StockAdjustmentItemCreate,
)
from app.modules.inventory.schemas.stock_transfer import (
    StockTransferCreate,
    StockTransferItemCreate,
)
from app.modules.inventory.services.stock_adjustment_service import StockAdjustmentService
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.inventory.services.stock_transfer_service import StockTransferService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def transfer_fixture(db_session: AsyncSession):
    """Sets up two warehouses and stock for transfer and adjustment testing."""
    tenant = Tenant(name="Global Retail", slug=f"retail-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        tenant_id=tenant.id,
        name="Logistics HQ",
        legal_name="Global Logistics HQ Inc",
        tax_identifier=f"HQ-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org)
    await db_session.flush()

    uom = UnitOfMeasure(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="UNIT",
        name="Unit",
        category="COUNT",
    )
    db_session.add(uom)
    await db_session.flush()

    wh_source = Warehouse(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-EAST",
        name="East Warehouse",
    )
    wh_dest = Warehouse(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-WEST",
        name="West Warehouse",
    )
    prod = Product(
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="SKU-LAPTOP-X1",
        name="Laptop X1 Carbon",
        uom_id=uom.id,
        cost_price=Decimal("1200.00"),
        selling_price=Decimal("1800.00"),
        allow_negative_stock=False,
    )
    db_session.add_all([wh_source, wh_dest, prod])
    await db_session.flush()

    # Seed initial stock of 50 units in WH-EAST
    ledger_service = StockLedgerService(db_session)
    await ledger_service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh_source.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("50.0000"),
        unit_cost=Decimal("1200.0000"),
    )

    return {
        "tenant": tenant,
        "org": org,
        "wh_source": wh_source,
        "wh_dest": wh_dest,
        "product": prod,
    }


@pytest.mark.asyncio
async def test_inter_warehouse_stock_transfer_workflow(db_session: AsyncSession, transfer_fixture):
    """Verifies that an inter-warehouse transfer properly debits source and credits destination."""
    tenant = transfer_fixture["tenant"]
    org = transfer_fixture["org"]
    wh_source = transfer_fixture["wh_source"]
    wh_dest = transfer_fixture["wh_dest"]
    prod = transfer_fixture["product"]

    transfer_service = StockTransferService(db_session)
    balance_repo = StockBalanceRepository(db_session)

    # 1. Create transfer order for 20 laptops
    transfer_data = StockTransferCreate(
        from_warehouse_id=wh_source.id,
        to_warehouse_id=wh_dest.id,
        items=[
            StockTransferItemCreate(
                product_id=prod.id,
                quantity=Decimal("20.0000"),
                unit_cost=Decimal("1200.0000"),
            )
        ],
    )
    transfer = await transfer_service.create_transfer(tenant.id, org.id, transfer_data)
    assert transfer.status == "DRAFT"

    # 2. Ship the transfer (dispatches from WH-EAST)
    transfer = await transfer_service.ship_transfer(transfer.id, tenant.id, org.id)
    assert transfer.status == "IN_TRANSIT"

    # Check source balance has decreased to 30 units
    bal_source = await balance_repo.get_by_dimension(tenant.id, org.id, prod.id, wh_source.id)
    assert bal_source.quantity_on_hand == Decimal("30.0000")

    # Check destination balance is still 0
    bal_dest = await balance_repo.get_by_dimension(tenant.id, org.id, prod.id, wh_dest.id)
    assert bal_dest is None or bal_dest.quantity_on_hand == Decimal("0.0000")

    # 3. Complete the transfer (received at WH-WEST)
    transfer = await transfer_service.complete_transfer(transfer.id, tenant.id, org.id)
    assert transfer.status == "COMPLETED"

    # Check destination balance has increased to 20 units
    bal_dest = await balance_repo.get_by_dimension(tenant.id, org.id, prod.id, wh_dest.id)
    assert bal_dest.quantity_on_hand == Decimal("20.0000")
    assert bal_dest.average_cost == Decimal("1200.0000")


@pytest.mark.asyncio
async def test_stock_adjustment_approval_and_posting(db_session: AsyncSession, transfer_fixture):
    """Verifies stock adjustment lifecycle with physical inventory count reconciliation."""
    tenant = transfer_fixture["tenant"]
    org = transfer_fixture["org"]
    wh_source = transfer_fixture["wh_source"]
    prod = transfer_fixture["product"]

    adj_service = StockAdjustmentService(db_session)
    balance_repo = StockBalanceRepository(db_session)

    # Current stock in WH-EAST is 50. Physical count finds 53 (+3 variance)
    adj_data = StockAdjustmentCreate(
        warehouse_id=wh_source.id,
        reason="FOUND",
        items=[
            StockAdjustmentItemCreate(
                product_id=prod.id,
                system_quantity=Decimal("50.0000"),
                counted_quantity=Decimal("53.0000"),
                unit_cost=Decimal("1200.0000"),
            )
        ],
    )
    adj = await adj_service.create_adjustment(tenant.id, org.id, adj_data)
    assert adj.status == "DRAFT"
    assert adj.items[0].difference_quantity == Decimal("3.0000")
    assert adj.items[0].adjustment_type == "INCREASE"

    # Submit & Approve
    adj = await adj_service.submit_adjustment(adj.id, tenant.id, org.id)
    assert adj.status == "SUBMITTED"
    adj = await adj_service.approve_adjustment(adj.id, tenant.id, org.id)
    assert adj.status == "APPROVED"

    # Post adjustment
    adj = await adj_service.post_adjustment(adj.id, tenant.id, org.id)
    assert adj.status == "POSTED"

    # Verify updated stock balance is 53
    balance = await balance_repo.get_by_dimension(tenant.id, org.id, prod.id, wh_source.id)
    assert balance.quantity_on_hand == Decimal("53.0000")
