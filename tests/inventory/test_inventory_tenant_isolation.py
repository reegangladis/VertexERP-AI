"""Tests for Multi-Tenant Data Isolation in Inventory & Procurement."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def multi_tenant_fixture(db_session: AsyncSession):
    """Creates two distinct tenants with isolated organizations."""
    # Tenant A
    tenant_a = Tenant(name="Tenant Alpha", slug=f"alpha-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant_a)
    await db_session.flush()

    org_a = Organization(
        tenant_id=tenant_a.id,
        name="Alpha HQ",
        legal_name="Alpha Global Corp",
        tax_identifier=f"A-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org_a)
    await db_session.flush()

    # Tenant B
    tenant_b = Tenant(name="Tenant Beta", slug=f"beta-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant_b)
    await db_session.flush()

    org_b = Organization(
        tenant_id=tenant_b.id,
        name="Beta HQ",
        legal_name="Beta Global Corp",
        tax_identifier=f"B-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org_b)
    await db_session.flush()

    return {
        "tenant_a": tenant_a,
        "org_a": org_a,
        "tenant_b": tenant_b,
        "org_b": org_b,
    }


@pytest.mark.asyncio
async def test_cross_tenant_inventory_isolation(db_session: AsyncSession, multi_tenant_fixture):
    """Verifies that inventory entities and balances created in Tenant A are invisible to Tenant B."""
    tenant_a = multi_tenant_fixture["tenant_a"]
    org_a = multi_tenant_fixture["org_a"]
    tenant_b = multi_tenant_fixture["tenant_b"]
    org_b = multi_tenant_fixture["org_b"]

    uom_repo = StockLedgerService(db_session)
    prod_repo = ProductRepository(db_session)
    wh_repo = WarehouseRepository(db_session)
    bal_repo = StockBalanceRepository(db_session)

    # 1. Create UoM, Warehouse, and Product in Tenant A
    uom_a = UnitOfMeasure(
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        code="KG",
        name="Kilograms",
    )
    wh_a = Warehouse(
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        code="WH-ALPHA",
        name="Alpha Storage",
    )
    db_session.add_all([uom_a, wh_a])
    await db_session.flush()

    prod_a = Product(
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        sku="SKU-SECRET-A",
        name="Alpha Secret Material",
        uom_id=uom_a.id,
        cost_price=Decimal("500.00"),
        selling_price=Decimal("1000.00"),
    )
    await prod_repo.create(prod_a)

    # Record stock inflow in Tenant A
    await uom_repo.record_movement(
        tenant_id=tenant_a.id,
        org_id=org_a.id,
        product_id=prod_a.id,
        warehouse_id=wh_a.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("100.0000"),
        unit_cost=Decimal("500.0000"),
    )

    # 2. Query from Tenant B perspective:
    # Warehouse lookup with Tenant B should return None
    wh_from_b = await wh_repo.get_by_id(wh_a.id, tenant_b.id, org_b.id)
    assert wh_from_b is None

    # Product lookup with Tenant B should return None
    prod_from_b = await prod_repo.get_by_id(prod_a.id, tenant_b.id, org_b.id)
    assert prod_from_b is None

    # Product listing in Tenant B should return 0 items
    prods_in_b = await prod_repo.list_by_org(tenant_b.id, org_b.id)
    assert len(prods_in_b) == 0

    # Stock balance lookup with Tenant B should return None
    bal_from_b = await bal_repo.get_by_dimension(tenant_b.id, org_b.id, prod_a.id, wh_a.id)
    assert bal_from_b is None

    # Total valuation in Tenant B should be 0
    val_b = await bal_repo.get_total_valuation(tenant_b.id, org_b.id)
    assert val_b["total_items"] == 0
    assert val_b["total_valuation"] == Decimal("0")
