"""Comprehensive Tests for Manufacturing & Material Requirements Planning (MRP) Domain.

Covers:
1. Work Centers and Machines setup
2. Manufacturing Routings and Operation Sequences
3. Multi-Level Bills of Materials (BOM), Versions, Components, and Theoretical Costing
4. Production Orders lifecycle (PLANNED -> CONFIRMED -> IN_PROGRESS -> COMPLETED) and Work Order dispatching
5. Auditable Raw Material Consumption using the immutable Inventory Ledger (MFG_CONSUMPTION)
6. Negative Stock Prevention during consumption
7. Finished Goods Production Output with Unit Manufacturing Cost calculation and Inventory Ledger Inflow (MFG_OUTPUT)
8. Production Scrap Recording (MFG_SCRAP)
9. MRP Calculation Engine (Gross/Net requirements, Scheduled Receipts, Planned Order Conversion)
10. Quality Inspections (In-Process / Final Assembly QC)
11. Multi-Tenant Isolation & RBAC Security
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.core.permissions import PermissionCode
from app.modules.identity.services.jwt_service import JwtService
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.repositories.stock_movement_repository import StockMovementRepository
from app.modules.inventory.services.stock_ledger_service import StockLedgerService
from app.modules.manufacturing.models.work_center import Machine, WorkCenter
from app.modules.manufacturing.repositories.work_center_repository import WorkCenterRepository
from app.modules.manufacturing.schemas.bom import (
    BillOfMaterialCreate,
    BOMComponentCreate,
    BOMVersionCreate,
)
from app.modules.manufacturing.schemas.production_order import (
    MaterialConsumptionCreate,
    ProductionOrderCreate,
    ProductionOutputCreate,
    ProductionScrapCreate,
    WorkOrderUpdateStatus,
)
from app.modules.manufacturing.schemas.quality import QualityInspectionCreate
from app.modules.manufacturing.schemas.routing import RoutingCreate, RoutingOperationCreate
from app.modules.manufacturing.services.bom_service import BOMService
from app.modules.manufacturing.services.mrp_service import MRPService
from app.modules.manufacturing.services.production_service import ProductionService
from app.modules.manufacturing.services.quality_service import QualityService
from app.modules.manufacturing.services.routing_service import RoutingService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def mfg_environment(db_session: AsyncSession):
    """Sets up a tenant, organization, warehouses, UOM, and inventory products for manufacturing testing."""
    tenant = Tenant(id=uuid.uuid4(), name="Tesla Motors Corp", slug=f"tesla-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Gigafactory Nevada",
        legal_name="Tesla Gigafactory Nevada LLC",
        tax_identifier="US-987654321",
        base_currency="USD",
    )
    db_session.add(org)
    await db_session.flush()

    # UOM
    uom = UnitOfMeasure(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="PCS",
        name="Pieces",
        category="UNIT",
    )
    db_session.add(uom)
    await db_session.flush()

    # Warehouses
    raw_wh = Warehouse(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-RAW",
        name="Raw Materials Warehouse",
    )
    fg_wh = Warehouse(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-FG",
        name="Finished Goods Warehouse",
    )
    db_session.add_all([raw_wh, fg_wh])
    await db_session.flush()

    # Products: Finished Battery Pack, Raw Lithium Cell, Raw Battery Enclosure
    prod_battery = Product(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="EV-BATTERY-PACK-100",
        name="100kWh EV Battery Assembly",
        uom_id=uom.id,
        is_stockable=True,
        cost_price=Decimal("5000.00"),
        selling_price=Decimal("9500.00"),
        lead_time_days=4,
    )
    prod_cell = Product(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="RAW-CELL-2170",
        name="Lithium 2170 Battery Cell",
        uom_id=uom.id,
        is_stockable=True,
        cost_price=Decimal("4.50"),
        selling_price=Decimal("6.00"),
        lead_time_days=5,
        reorder_point=Decimal("2000.0000"),
    )
    prod_enclosure = Product(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="RAW-ENCLOSURE-ALUM",
        name="Aluminum Battery Pack Enclosure",
        uom_id=uom.id,
        is_stockable=True,
        cost_price=Decimal("450.00"),
        selling_price=Decimal("600.00"),
        lead_time_days=7,
        reorder_point=Decimal("20.0000"),
    )
    db_session.add_all([prod_battery, prod_cell, prod_enclosure])
    await db_session.flush()

    # Populate Initial Raw Materials Stock via StockLedgerService
    stock_service = StockLedgerService(db_session)
    await stock_service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod_cell.id,
        warehouse_id=raw_wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("5000.0000"),
        unit_cost=Decimal("4.5000"),
        notes="Initial Cell Inventory",
    )
    await stock_service.record_movement(
        tenant_id=tenant.id,
        org_id=org.id,
        product_id=prod_enclosure.id,
        warehouse_id=raw_wh.id,
        movement_type="PURCHASE_RECEIPT",
        quantity=Decimal("50.0000"),
        unit_cost=Decimal("450.0000"),
        notes="Initial Enclosure Inventory",
    )

    return {
        "tenant": tenant,
        "org": org,
        "uom": uom,
        "raw_wh": raw_wh,
        "fg_wh": fg_wh,
        "battery": prod_battery,
        "cell": prod_cell,
        "enclosure": prod_enclosure,
    }


@pytest.mark.asyncio
async def test_work_center_and_machine_setup(db_session: AsyncSession, mfg_environment):
    """Tests creating Work Centers and Machines with hourly rates and capacity limits."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]

    wc_repo = WorkCenterRepository(db_session)

    # 1. Create Machining / Welding Work Center
    wc = WorkCenter(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WC-CELL-WELD",
        name="Automated Laser Cell Welding Station",
        work_center_type="MACHINING",
        capacity_per_day_hours=Decimal("16.00"),
        cost_per_hour=Decimal("75.0000"),
        overhead_cost_per_hour=Decimal("25.0000"),
        status="ACTIVE",
    )
    await wc_repo.create_work_center(wc)

    # 2. Add Precision Laser Machine
    machine = Machine(
        tenant_id=tenant.id,
        organization_id=org.id,
        work_center_id=wc.id,
        code="MCH-LASER-01",
        name="Trumpf TruLaser Cell 7040",
        serial_number="TRU-99210-NV",
        hourly_cost=Decimal("40.0000"),
        status="OPERATIONAL",
    )
    await wc_repo.create_machine(machine)

    # Verify retrieval
    retrieved = await wc_repo.get_work_center_by_id(wc.id, tenant.id, org.id)
    assert retrieved is not None
    assert retrieved.name == "Automated Laser Cell Welding Station"
    assert len(retrieved.machines) == 1
    assert retrieved.machines[0].code == "MCH-LASER-01"


@pytest.mark.asyncio
async def test_routing_creation_and_operation_sequence(db_session: AsyncSession, mfg_environment):
    """Tests defining Manufacturing Routings with multi-step operations."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    battery = mfg_environment["battery"]

    wc_repo = WorkCenterRepository(db_session)
    routing_service = RoutingService(db_session)

    wc_weld = await wc_repo.create_work_center(
        WorkCenter(
            tenant_id=tenant.id,
            organization_id=org.id,
            code="WC-WELD-01",
            name="Welding Station",
            cost_per_hour=Decimal("60.00"),
            overhead_cost_per_hour=Decimal("20.00"),
        )
    )
    wc_test = await wc_repo.create_work_center(
        WorkCenter(
            tenant_id=tenant.id,
            organization_id=org.id,
            code="WC-TEST-01",
            name="High Voltage Testing Bay",
            cost_per_hour=Decimal("80.00"),
            overhead_cost_per_hour=Decimal("30.00"),
        )
    )

    routing_data = RoutingCreate(
        code="RT-BATTERY-100",
        name="Standard 100kWh Assembly Routing",
        product_id=battery.id,
        operations=[
            RoutingOperationCreate(
                sequence=10,
                operation_name="Cell Module Laser Welding",
                work_center_id=wc_weld.id,
                setup_time_hours=Decimal("1.00"),
                run_time_per_unit_hours=Decimal("2.00"),
            ),
            RoutingOperationCreate(
                sequence=20,
                operation_name="HV Insulation & Load Testing",
                work_center_id=wc_test.id,
                setup_time_hours=Decimal("0.50"),
                run_time_per_unit_hours=Decimal("0.50"),
            ),
        ],
    )

    routing = await routing_service.create_routing(tenant.id, org.id, routing_data)
    assert routing.id is not None
    assert len(routing.operations) == 2

    # Verify time and cost estimation for 5 units:
    # Op 10: 1.0 + (2.0 * 5) = 11.0 hrs @ $80/hr = $880
    # Op 20: 0.5 + (0.5 * 5) = 3.0 hrs @ $110/hr = $330
    # Total Hours = 14.0 hrs, Total Cost = $1210.00
    hours, cost = await routing_service.estimate_routing_time_and_cost(
        routing.id, Decimal("5.00"), tenant.id, org.id
    )
    assert hours == Decimal("14.00")
    assert cost == Decimal("1210.0000")


@pytest.mark.asyncio
async def test_bom_creation_versioning_and_costing(db_session: AsyncSession, mfg_environment):
    """Tests creating Bills of Materials, versioning, component scrap, and theoretical material costing."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    enclosure = mfg_environment["enclosure"]

    bom_service = BOMService(db_session)

    # 1. Create BOM with Components: 100 Cells @ $4.50 + 1 Enclosure @ $450 = $450 + $450 = $900
    bom_data = BillOfMaterialCreate(
        code="BOM-BATTERY-100",
        name="100kWh Battery Pack Master BOM",
        product_id=battery.id,
        quantity=Decimal("1.0000"),
        uom_id=uom.id,
        is_default=True,
        components=[
            BOMComponentCreate(
                component_product_id=cell.id,
                quantity=Decimal("100.0000"),
                uom_id=uom.id,
                scrap_percentage=Decimal("2.00"),  # 2% scrap
                position=1,
            ),
            BOMComponentCreate(
                component_product_id=enclosure.id,
                quantity=Decimal("1.0000"),
                uom_id=uom.id,
                scrap_percentage=Decimal("0.00"),
                position=2,
            ),
        ],
    )

    bom = await bom_service.create_bom(tenant.id, org.id, bom_data)
    assert bom.id is not None
    assert len(bom.versions) == 1
    v1 = bom.versions[0]
    assert v1.version_number == 1
    assert len(v1.components) == 2

    # Theoretical cost: (100 * 1.02 * $4.50) + (1 * $450) = $459.00 + $450.00 = $909.00
    theo_cost = await bom_service.calculate_bom_theoretical_cost(v1.id, tenant.id, org.id)
    assert theo_cost == Decimal("909.0000")

    # 2. Create BOM Version 2 with upgraded cell count
    v2_data = BOMVersionCreate(
        version_number=2,
        revision_notes="Upgraded to high-density cell architecture",
        status="ACTIVE",
        components=[
            BOMComponentCreate(
                component_product_id=cell.id,
                quantity=Decimal("110.0000"),
                uom_id=uom.id,
                scrap_percentage=Decimal("0.00"),
                position=1,
            ),
            BOMComponentCreate(
                component_product_id=enclosure.id,
                quantity=Decimal("1.0000"),
                uom_id=uom.id,
                scrap_percentage=Decimal("0.00"),
                position=2,
            ),
        ],
    )
    v2 = await bom_service.add_version(bom.id, tenant.id, org.id, v2_data)
    assert v2.version_number == 2
    assert len(v2.components) == 2


@pytest.mark.asyncio
async def test_production_order_lifecycle_and_work_orders(
    db_session: AsyncSession, mfg_environment
):
    """Tests Production Order lifecycle (PLANNED -> CONFIRMED -> IN_PROGRESS -> COMPLETED) and work order progression."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    enclosure = mfg_environment["enclosure"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    routing_service = RoutingService(db_session)
    prod_service = ProductionService(db_session)
    wc_repo = WorkCenterRepository(db_session)

    # Setup BOM and Routing
    wc = await wc_repo.create_work_center(
        WorkCenter(
            tenant_id=tenant.id, organization_id=org.id, code="WC-PACK", name="Pack Assembly"
        )
    )
    routing = await routing_service.create_routing(
        tenant.id,
        org.id,
        RoutingCreate(
            code="RT-PACK",
            name="Pack Routing",
            product_id=battery.id,
            operations=[
                RoutingOperationCreate(
                    sequence=10,
                    operation_name="Assembly",
                    work_center_id=wc.id,
                    run_time_per_unit_hours=Decimal("1.0"),
                )
            ],
        ),
    )
    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-BAT-MO",
            name="Battery Pack BOM",
            product_id=battery.id,
            routing_id=routing.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("100"), uom_id=uom.id
                ),
                BOMComponentCreate(
                    component_product_id=enclosure.id, quantity=Decimal("1"), uom_id=uom.id
                ),
            ],
        ),
    )

    # 1. Create Production Order for 2 units
    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            routing_id=routing.id,
            planned_quantity=Decimal("2.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=3),
        ),
    )
    assert mo.status == "PLANNED"
    assert mo.order_number.startswith("MO-")

    # 2. Confirm Order -> Dispatches Work Order
    mo = await prod_service.confirm_production_order(mo.id, tenant.id, org.id)
    assert mo.status == "CONFIRMED"
    assert len(mo.work_orders) == 1
    wo = mo.work_orders[0]
    assert wo.operation_name == "Assembly"
    assert wo.status == "PENDING"

    # 3. Start Shop-Floor Work Order
    wo = await prod_service.update_work_order_status(
        wo.id, tenant.id, org.id, WorkOrderUpdateStatus(status="IN_PROGRESS")
    )
    assert wo.status == "IN_PROGRESS"
    assert wo.started_at is not None

    # Complete Work Order
    wo = await prod_service.update_work_order_status(
        wo.id,
        tenant.id,
        org.id,
        WorkOrderUpdateStatus(status="COMPLETED", actual_duration_hours=Decimal("2.5")),
    )
    assert wo.status == "COMPLETED"
    assert wo.total_labor_cost == Decimal("2.5") * wo.hourly_rate


@pytest.mark.asyncio
async def test_material_consumption_inventory_impact(db_session: AsyncSession, mfg_environment):
    """Tests that material consumption atomically deducts stock via the immutable inventory ledger (MFG_CONSUMPTION)."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    enclosure = mfg_environment["enclosure"]
    raw_wh = mfg_environment["raw_wh"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)
    balance_repo = StockBalanceRepository(db_session)
    movement_repo = StockMovementRepository(db_session)

    # Initial raw stock: 5000 Cells, 50 Enclosures
    cell_bal = await balance_repo.get_by_dimension(
        tenant_id=tenant.id, org_id=org.id, warehouse_id=raw_wh.id, product_id=cell.id
    )
    assert cell_bal.quantity_on_hand == Decimal("5000.0000")

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-BAT-CONS",
            name="Battery BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("100"), uom_id=uom.id
                ),
                BOMComponentCreate(
                    component_product_id=enclosure.id, quantity=Decimal("1"), uom_id=uom.id
                ),
            ],
        ),
    )

    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("10.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=2),
        ),
    )
    await prod_service.confirm_production_order(mo.id, tenant.id, org.id)

    # Consume 1000 Cells
    cons = await prod_service.record_material_consumption(
        mo.id,
        tenant.id,
        org.id,
        MaterialConsumptionCreate(
            product_id=cell.id,
            warehouse_id=raw_wh.id,
            consumed_quantity=Decimal("1000.0000"),
            batch_number="BATCH-CELL-NV01",
        ),
    )

    assert cons.id is not None
    assert cons.stock_movement_id is not None

    # Verify StockBalance was decremented by 1000
    cell_bal_after = await balance_repo.get_by_dimension(
        tenant_id=tenant.id, org_id=org.id, warehouse_id=raw_wh.id, product_id=cell.id
    )
    assert cell_bal_after.quantity_on_hand == Decimal("4000.0000")

    # Verify immutable StockMovement was recorded
    movement = await movement_repo.get_by_id(cons.stock_movement_id, tenant.id, org.id)
    assert movement is not None
    assert movement.movement_type == "MFG_CONSUMPTION"
    assert movement.quantity == Decimal("-1000.0000")


@pytest.mark.asyncio
async def test_negative_stock_prevention_on_consumption(db_session: AsyncSession, mfg_environment):
    """Ensures inventory validation prevents over-consumption when stock is insufficient."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    raw_wh = mfg_environment["raw_wh"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-BAT-OVERSHOT",
            name="Battery BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("100"), uom_id=uom.id
                )
            ],
        ),
    )

    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("100.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=2),
        ),
    )
    await prod_service.confirm_production_order(mo.id, tenant.id, org.id)

    # Try consuming 10,000 cells when only 5,000 are in inventory
    with pytest.raises(ValidationException) as exc:
        await prod_service.record_material_consumption(
            mo.id,
            tenant.id,
            org.id,
            MaterialConsumptionCreate(
                product_id=cell.id,
                warehouse_id=raw_wh.id,
                consumed_quantity=Decimal("10000.0000"),
            ),
        )
    assert "Negative stock violation" in str(exc.value)


@pytest.mark.asyncio
async def test_production_output_finished_goods_inventory_ledger(
    db_session: AsyncSession, mfg_environment
):
    """Tests production output recording with cost accumulation and finished goods stock ledger entry (MFG_OUTPUT)."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    enclosure = mfg_environment["enclosure"]
    raw_wh = mfg_environment["raw_wh"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)
    balance_repo = StockBalanceRepository(db_session)
    movement_repo = StockMovementRepository(db_session)

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-BAT-OUT",
            name="Battery BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("100"), uom_id=uom.id
                ),
                BOMComponentCreate(
                    component_product_id=enclosure.id, quantity=Decimal("1"), uom_id=uom.id
                ),
            ],
        ),
    )

    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("5.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=2),
        ),
    )
    await prod_service.confirm_production_order(mo.id, tenant.id, org.id)

    # Consume materials: 500 cells ($2,250) + 5 enclosures ($2,250) = $4,500
    await prod_service.record_material_consumption(
        mo.id,
        tenant.id,
        org.id,
        MaterialConsumptionCreate(
            product_id=cell.id, warehouse_id=raw_wh.id, consumed_quantity=Decimal("500.0000")
        ),
    )
    await prod_service.record_material_consumption(
        mo.id,
        tenant.id,
        org.id,
        MaterialConsumptionCreate(
            product_id=enclosure.id, warehouse_id=raw_wh.id, consumed_quantity=Decimal("5.0000")
        ),
    )

    # Produce 5 Finished Battery Packs
    output = await prod_service.record_production_output(
        mo.id,
        tenant.id,
        org.id,
        ProductionOutputCreate(
            target_warehouse_id=fg_wh.id,
            produced_quantity=Decimal("5.0000"),
            batch_number="BATCH-BAT-2026-A1",
            serial_number="SN-BAT-0001",
        ),
    )

    assert output.id is not None
    assert output.produced_quantity == Decimal("5.0000")
    # Unit mfg cost = $4,500 / 5 = $900.00
    assert output.unit_manufacturing_cost == Decimal("900.0000")

    # Verify FG Inventory Stock Balance was updated
    fg_bal = await balance_repo.get_by_dimension(
        tenant_id=tenant.id, org_id=org.id, warehouse_id=fg_wh.id, product_id=battery.id
    )
    assert fg_bal is not None
    assert fg_bal.quantity_on_hand == Decimal("5.0000")

    # Verify Stock Movement
    mov = await movement_repo.get_by_id(output.stock_movement_id, tenant.id, org.id)
    assert mov is not None
    assert mov.movement_type == "MFG_OUTPUT"
    assert mov.quantity == Decimal("5.0000")


@pytest.mark.asyncio
async def test_production_scrap_recording(db_session: AsyncSession, mfg_environment):
    """Tests recording scrap during production with inventory ledger loss tracking."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    raw_wh = mfg_environment["raw_wh"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-SCRAP",
            name="Scrap Test BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("10"), uom_id=uom.id
                )
            ],
        ),
    )
    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("1.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=1),
        ),
    )
    await prod_service.confirm_production_order(mo.id, tenant.id, org.id)

    # Record Scrap
    scrap = await prod_service.record_production_scrap(
        mo.id,
        tenant.id,
        org.id,
        ProductionScrapCreate(
            product_id=cell.id,
            scrap_quantity=Decimal("3.0000"),
            scrap_reason="MACHINE_MALFUNCTION",
            warehouse_id=raw_wh.id,
        ),
    )

    assert scrap.id is not None
    assert scrap.scrap_quantity == Decimal("3.0000")
    assert scrap.stock_movement_id is not None


@pytest.mark.asyncio
async def test_mrp_calculation_and_planned_orders(db_session: AsyncSession, mfg_environment):
    """Tests MRP Engine gross-to-net calculation and planned order generation for raw materials and assemblies."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    enclosure = mfg_environment["enclosure"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)
    mrp_service = MRPService(db_session)

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-MRP-BAT",
            name="MRP Battery BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("100"), uom_id=uom.id
                ),
                BOMComponentCreate(
                    component_product_id=enclosure.id, quantity=Decimal("1"), uom_id=uom.id
                ),
            ],
        ),
    )

    # Create Open Demand: 50 Battery Packs planned due in 15 days
    # Needs: 50 * 100 = 5000 Cells (currently on hand: 5000, but with reorder point 2000 => net requirement of 2000 cells)
    # Needs: 50 * 1 = 50 Enclosures (currently on hand: 50, but with reorder point 20 => net requirement of 20 enclosures)
    await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("50.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today() + timedelta(days=5),
            planned_due_date=date.today() + timedelta(days=15),
        ),
    )

    # Run MRP
    mrp_run = await mrp_service.run_mrp(tenant.id, org.id, planning_horizon_days=30)
    assert mrp_run.status == "COMPLETED"
    assert mrp_run.total_items_planned >= 1

    # Check planned orders
    planned_orders = mrp_run.planned_orders
    assert len(planned_orders) > 0

    # Convert a planned purchase order
    purchase_planned = next((p for p in planned_orders if p.order_type == "PURCHASE"), None)
    if purchase_planned:
        conv_res = await mrp_service.convert_planned_order(purchase_planned.id, tenant.id, org.id)
        assert conv_res["converted_type"] == "PURCHASE_REQUEST"
        assert purchase_planned.status == "CONVERTED"


@pytest.mark.asyncio
async def test_quality_inspection_workflow(db_session: AsyncSession, mfg_environment):
    """Tests creating Quality Inspections on production orders with pass/fail dispositions."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]
    uom = mfg_environment["uom"]
    battery = mfg_environment["battery"]
    cell = mfg_environment["cell"]
    fg_wh = mfg_environment["fg_wh"]

    bom_service = BOMService(db_session)
    prod_service = ProductionService(db_session)
    quality_service = QualityService(db_session)

    bom = await bom_service.create_bom(
        tenant.id,
        org.id,
        BillOfMaterialCreate(
            code="BOM-QC",
            name="QC BOM",
            product_id=battery.id,
            uom_id=uom.id,
            components=[
                BOMComponentCreate(
                    component_product_id=cell.id, quantity=Decimal("10"), uom_id=uom.id
                )
            ],
        ),
    )
    mo = await prod_service.create_production_order(
        tenant.id,
        org.id,
        ProductionOrderCreate(
            product_id=battery.id,
            bom_id=bom.id,
            bom_version_id=bom.versions[0].id,
            planned_quantity=Decimal("10.0000"),
            target_warehouse_id=fg_wh.id,
            planned_start_date=date.today(),
            planned_due_date=date.today() + timedelta(days=2),
        ),
    )
    await prod_service.confirm_production_order(mo.id, tenant.id, org.id)

    # Perform Final Assembly QC Inspection on 10 units: 9 Passed, 1 Failed
    qc = await quality_service.create_inspection(
        tenant.id,
        org.id,
        QualityInspectionCreate(
            production_order_id=mo.id,
            product_id=battery.id,
            inspection_type="FINAL_ASSEMBLY",
            inspected_quantity=Decimal("10.0000"),
            passed_quantity=Decimal("9.0000"),
            failed_quantity=Decimal("1.0000"),
            defect_reason="Cell voltage imbalance in Module 3",
        ),
    )

    assert qc.id is not None
    assert qc.result == "CONDITIONALLY_PASSED"
    assert qc.inspection_number.startswith("QC-")
    assert mo.rejected_quantity == Decimal("1.0000")


@pytest.mark.asyncio
async def test_manufacturing_api_and_tenant_isolation(
    async_client: AsyncClient, db_session: AsyncSession, mfg_environment
):
    """Tests API endpoints and enforces strict multi-tenant boundary isolation."""
    tenant = mfg_environment["tenant"]
    org = mfg_environment["org"]

    all_permissions = [p.value for p in PermissionCode]
    token_a, _, _ = JwtService.create_access_token(
        user_id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        roles=["PlantManager"],
        permissions=all_permissions,
        session_id=uuid.uuid4(),
    )

    # 1. Create a work center via API with appropriate headers
    headers = {
        "Authorization": f"Bearer {token_a}",
        "X-Tenant-ID": str(tenant.id),
        "X-Organization-ID": str(org.id),
    }

    wc_payload = {
        "code": "WC-API-TEST",
        "name": "API Automated Work Station",
        "work_center_type": "ASSEMBLY",
        "capacity_per_day_hours": "10.00",
        "cost_per_hour": "55.0000",
        "overhead_cost_per_hour": "15.0000",
        "status": "ACTIVE",
    }

    resp = await async_client.post(
        "/api/v1/manufacturing/work-centers", json=wc_payload, headers=headers
    )
    assert resp.status_code == 201
    wc_data = resp.json()
    assert wc_data["code"] == "WC-API-TEST"

    # 2. List work centers under Tenant A
    list_resp = await async_client.get("/api/v1/manufacturing/work-centers", headers=headers)
    assert list_resp.status_code == 200
    assert any(w["code"] == "WC-API-TEST" for w in list_resp.json()["items"])

    # 3. List work centers under another Tenant B -> Should return 0 results (Tenant Isolation)
    other_tenant_id = uuid.uuid4()
    other_org_id = uuid.uuid4()
    token_b, _, _ = JwtService.create_access_token(
        user_id=uuid.uuid4(),
        tenant_id=other_tenant_id,
        organization_id=other_org_id,
        roles=["PlantManager"],
        permissions=all_permissions,
        session_id=uuid.uuid4(),
    )
    other_headers = {
        "Authorization": f"Bearer {token_b}",
        "X-Tenant-ID": str(other_tenant_id),
        "X-Organization-ID": str(other_org_id),
    }

    other_list_resp = await async_client.get(
        "/api/v1/manufacturing/work-centers", headers=other_headers
    )
    assert other_list_resp.status_code == 200
    assert len(other_list_resp.json()["items"]) == 0
