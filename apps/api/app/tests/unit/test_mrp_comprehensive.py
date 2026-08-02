import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.manufacturing import (
    BillOfMaterial,
    ProductionOrder,
    QualityInspection,
)
from app.schemas.manufacturing import (
    BOMCreate,
    BOMItemCreate,
    ProductionOrderCreate,
    QualityInspectionCreate,
    QualityResultCreate,
    WorkCenterCreate,
)
from app.services.manufacturing_service import ManufacturingService


@pytest.mark.asyncio
async def test_bom_crud_and_approval():
    mock_db = AsyncMock()
    service = ManufacturingService(mock_db)

    org_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    comp_id = uuid.uuid4()

    # 1. Create BOM
    bom_data = BOMCreate(
        product_id=prod_id,
        code="BOM-TEST-100",
        version="1.0",
        base_quantity=1.0,
        notes="Test BOM creation",
        items=[
            BOMItemCreate(
                component_product_id=comp_id,
                quantity=4.0,
                unit_name="PCS",
                scrap_factor_percent=5.0,
                unit_cost=20.0,
            )
        ],
    )

    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()

    created_bom = BillOfMaterial(
        id=uuid.uuid4(),
        organization_id=org_id,
        product_id=prod_id,
        code="BOM-TEST-100",
        version="1.0",
        status="DRAFT",
        is_active=True,
        total_cost=84.0,
    )
    service.bom_repo.get_with_items = AsyncMock(return_value=created_bom)

    bom_res = await service.create_bom(org_id, bom_data)
    assert bom_res.code == "BOM-TEST-100"
    assert bom_res.status == "DRAFT"

    # 2. Approve BOM
    approved_bom = await service.approve_bom(created_bom.id, uuid.uuid4())
    assert approved_bom.status == "APPROVED"


@pytest.mark.asyncio
async def test_routing_and_work_center():
    mock_db = AsyncMock()
    service = ManufacturingService(mock_db)

    org_id = uuid.uuid4()
    wc_data = WorkCenterCreate(
        code="WC-101",
        name="CNC Milling Center",
        category="MACHINING",
        capacity_per_day_hours=16.0,
        hourly_cost=75.0,
    )

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    wc = await service.create_work_center(org_id, wc_data)
    assert wc.code == "WC-101"
    assert wc.category == "MACHINING"


@pytest.mark.asyncio
async def test_production_order_and_costs():
    mock_db = AsyncMock()
    service = ManufacturingService(mock_db)

    org_id = uuid.uuid4()
    prod_id = uuid.uuid4()

    order_data = ProductionOrderCreate(
        product_id=prod_id,
        order_number="PO-2026-TEST",
        planned_quantity=100.0,
        priority="HIGH",
        planned_start_date=date.today(),
        planned_end_date=date.today(),
    )

    po = ProductionOrder(
        id=uuid.uuid4(),
        organization_id=org_id,
        order_number="PO-2026-TEST",
        product_id=prod_id,
        planned_quantity=100.0,
        completed_quantity=100.0,
        status="COMPLETED",
        priority="HIGH",
        planned_start_date=date.today(),
        planned_end_date=date.today(),
        items=[],
    )
    service.order_repo.get_with_items = AsyncMock(return_value=po)
    service.order_repo.get_material_consumptions = AsyncMock(return_value=[])

    cost_summary = await service.calculate_production_order_costs(po.id)
    assert cost_summary.order_number == "PO-2026-TEST"
    assert cost_summary.planned_quantity == 100.0


@pytest.mark.asyncio
async def test_quality_and_maintenance():
    mock_db = AsyncMock()
    service = ManufacturingService(mock_db)

    org_id = uuid.uuid4()
    insp_data = QualityInspectionCreate(
        inspection_number="QC-TEST-001",
        product_id=uuid.uuid4(),
        inspector_name="Inspector Test",
        sample_size=5,
        results=[
            QualityResultCreate(
                parameter_name="Tolerance",
                expected_value="10mm",
                actual_value="10mm",
                is_passed=True,
            )
        ],
    )

    created_insp = QualityInspection(
        id=uuid.uuid4(),
        organization_id=org_id,
        inspection_number="QC-TEST-001",
        product_id=uuid.uuid4(),
        status="COMPLETED",
        decision="APPROVED",
        passed_count=1,
        failed_count=0,
    )
    service.inspection_repo.get_with_results = AsyncMock(return_value=created_insp)

    insp = await service.create_quality_inspection(org_id, insp_data)
    assert insp.decision == "APPROVED"
