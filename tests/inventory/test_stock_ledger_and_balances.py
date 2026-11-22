"""Tests for Auditable Stock Ledger, Movements, Balances, Valuation, and Invariants."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def inventory_fixture(db_session: AsyncSession):
    """Sets up a tenant, organization, warehouse, UoM, and products for testing."""
    tenant = Tenant(name="Acme Corp", slug=f"acme-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        tenant_id=tenant.id,
        name="Acme Logistics",
        legal_name="Acme Logistics LLC",
        tax_identifier=f"LOG-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org)
    await db_session.flush()

    uom = UnitOfMeasure(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="PCS",
        name="Pieces",
        category="COUNT",
    )
    db_session.add(uom)
    await db_session.flush()

    wh = Warehouse(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-MAIN",
        name="Main Distribution Center",
        is_primary=True,
    )
    db_session.add(wh)
    await db_session.flush()

    # Product with negative stock disallowed
    prod_standard = Product(
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="SKU-STEEL-BOLT",
        name="Steel Bolt 10mm",
        uom_id=uom.id,
        cost_price=Decimal("2.50"),
        selling_price=Decimal("5.00"),
        allow_negative_stock=False,
    )
    # Product with negative stock allowed
    prod_negative_allowed = Product(
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="SKU-DIGITAL-SVC",
        name="Consulting Token",
        uom_id=uom.id,
        cost_price=Decimal("50.00"),
        selling_price=Decimal("100.00"),
        allow_negative_stock=True,
    )
    db_session.add_all([prod_standard, prod_negative_allowed])
    await db_session.flush()

    return {
        "tenant": tenant,
        "org": org,
        "uom": uom,
        "warehouse": wh,
        "prod_standard": prod_standard,
        "prod_negative_allowed": prod_negative_allowed,
    }


@pytest.mark.asyncio
async def test_stock_inflow_creates_immutable_movement_and_updates_balance(
    db_session: AsyncSession, inventory_fixture
):
    """Verifies that an inflow movement creates a ledger record and updates stock balance."""
    tenant = inventory_fixture["tenant"]
    org = inventory_fixture["org"]
    wh = inventory_fixture["warehouse"]
    prod = inventory_fixture["prod_standard"]

    service = StockLedgerService(db_session)

    # 1. Record initial inflow of 100 units @ $10.00
    movement, balance = await service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("100.0000"),
        unit_cost=Decimal("10.0000"),
        notes="Initial receipt",
    )

    assert movement.id is not None
    assert movement.movement_number.startswith("MOV-")
    assert movement.quantity == Decimal("100.0000")
    assert movement.unit_cost == Decimal("10.0000")
    assert movement.total_cost == Decimal("1000.00")
    assert movement.running_balance_qty == Decimal("100.0000")

    assert balance.quantity_on_hand == Decimal("100.0000")
    assert balance.quantity_available == Decimal("100.0000")
    assert balance.average_cost == Decimal("10.0000")
    assert balance.total_value == Decimal("1000.00")
    assert balance.version >= 1


@pytest.mark.asyncio
async def test_moving_average_cost_calculation(db_session: AsyncSession, inventory_fixture):
    """Verifies that subsequent inflows recalculate the moving average cost correctly."""
    tenant = inventory_fixture["tenant"]
    org = inventory_fixture["org"]
    wh = inventory_fixture["warehouse"]
    prod = inventory_fixture["prod_standard"]

    service = StockLedgerService(db_session)

    # Inflow 1: 100 units @ $10.00 ($1,000 total)
    await service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("100.0000"),
        unit_cost=Decimal("10.0000"),
    )

    # Inflow 2: 50 units @ $16.00 ($800 total)
    # Total units: 150, Total value: $1,800 => New Avg Cost: 1800 / 150 = $12.00
    movement2, balance2 = await service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("50.0000"),
        unit_cost=Decimal("16.0000"),
    )

    assert balance2.quantity_on_hand == Decimal("150.0000")
    assert balance2.average_cost == Decimal("12.0000")
    assert balance2.total_value == Decimal("1800.00")
    assert movement2.running_balance_qty == Decimal("150.0000")
    assert movement2.running_balance_cost == Decimal("12.0000")


@pytest.mark.asyncio
async def test_negative_stock_prevention_where_disallowed(
    db_session: AsyncSession, inventory_fixture
):
    """Verifies that an outflow resulting in negative stock raises ValidationException when allow_negative_stock=False."""
    tenant = inventory_fixture["tenant"]
    org = inventory_fixture["org"]
    wh = inventory_fixture["warehouse"]
    prod = inventory_fixture["prod_standard"]

    service = StockLedgerService(db_session)

    # Inflow 10 units
    await service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("10.0000"),
        unit_cost=Decimal("5.0000"),
    )

    # Attempt to deduct 15 units -> should raise ValidationException
    with pytest.raises(ValidationException) as exc_info:
        await service.record_movement(
            tenant_id=tenant.id,
            org_id=org.id,
            product_id=prod.id,
            warehouse_id=wh.id,
            movement_type="GOODS_ISSUE",
            quantity=Decimal("-15.0000"),
        )
    assert "Negative stock violation" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_negative_stock_allowed_when_configured(db_session: AsyncSession, inventory_fixture):
    """Verifies that an outflow resulting in negative stock succeeds when allow_negative_stock=True."""
    tenant = inventory_fixture["tenant"]
    org = inventory_fixture["org"]
    wh = inventory_fixture["warehouse"]
    prod = inventory_fixture["prod_negative_allowed"]

    service = StockLedgerService(db_session)

    # Deduct 5 units with zero initial stock
    movement, balance = await service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod.id,
        warehouse_id=wh.id,
        movement_type="GOODS_ISSUE",
        quantity=Decimal("-5.0000"),
        unit_cost=Decimal("50.0000"),
    )

    assert balance.quantity_on_hand == Decimal("-5.0000")
    assert movement.quantity == Decimal("-5.0000")
    assert movement.running_balance_qty == Decimal("-5.0000")
