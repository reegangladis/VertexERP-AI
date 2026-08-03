import uuid
from datetime import date
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.models.inventory_procurement_v11 import Product
from app.models.manufacturing_mrp_v13 import (
    BillOfMaterial,
    Machine,
    MRPRun,
    ProductionOrder,
    WorkCenter,
)
from app.services.manufacturing_mrp import (
    BOMEngine,
    ManufacturingAnalyticsService,
    MRPEngine,
    ProductionPlanningEngine,
    WorkCenterService,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_bom_creation_and_circular_validation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    bom_engine = BOMEngine(mock_db_session)
    prod_id = uuid.uuid4()
    raw_material_id = uuid.uuid4()

    from app.schemas.manufacturing_mrp import BOMCreate, BOMItemCreate

    # Circular BOM validation check
    circular_payload = BOMCreate(
        product_id=prod_id,
        bom_code="BOM-CIRCULAR",
        items=[BOMItemCreate(raw_material_id=prod_id, quantity=1.0)],
    )

    with pytest.raises(HTTPException) as exc_info:
        await bom_engine.create_bom(circular_payload)
    assert exc_info.value.status_code == 400
    assert "Circular BOM dependency detected" in exc_info.value.detail

    # Valid BOM creation
    valid_payload = BOMCreate(
        product_id=prod_id,
        bom_code="BOM-PRO-100",
        revision="Rev A",
        description="BOM for Assembly Product",
        items=[BOMItemCreate(raw_material_id=raw_material_id, quantity=4.0)],
    )

    bom_obj = BillOfMaterial(
        id=uuid.uuid4(),
        product_id=prod_id,
        bom_code="BOM-PRO-100",
        revision="Rev A",
        description=valid_payload.description,
        status="Active",
        items=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # duplicate check
        create_mock_execute_result(None),  # item insert
        create_mock_execute_result(bom_obj),  # get_with_items
    ]

    bom = await bom_engine.create_bom(valid_payload)
    assert bom is not None
    assert bom.bom_code == "BOM-PRO-100"


@pytest.mark.asyncio
async def test_production_order_lifecycle(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    prod_engine = ProductionPlanningEngine(mock_db_session)
    org_id = uuid.uuid4()
    prod_id = uuid.uuid4()

    from app.schemas.manufacturing_mrp import ProductionOrderCreate
    payload = ProductionOrderCreate(
        organization_id=org_id,
        production_number="PO-2026-0001",
        product_id=prod_id,
        planned_quantity=100.0,
        scheduled_start=date(2026, 8, 1),
        scheduled_end=date(2026, 8, 10),
        priority="High",
    )

    po_obj = ProductionOrder(
        id=uuid.uuid4(),
        organization_id=org_id,
        production_number="PO-2026-0001",
        product_id=prod_id,
        planned_quantity=100.0,
        completed_quantity=0.0,
        scheduled_start=payload.scheduled_start,
        scheduled_end=payload.scheduled_end,
        priority="High",
        status="Draft",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
    ]
    po = await prod_engine.create_production_order(payload)
    assert po is not None

    # Start production
    mock_db_session.execute.side_effect = [
        create_mock_execute_result(po_obj),  # get order
        create_mock_execute_result(po_obj),  # update
        create_mock_execute_result(po_obj),  # get order after start
    ]
    started_po = await prod_engine.start_production_order(po_obj.id)
    assert started_po is not None

    # Complete production
    mock_db_session.execute.side_effect = [
        create_mock_execute_result(po_obj),  # get order
        create_mock_execute_result(po_obj),  # update status
        create_mock_execute_result(None),  # insert finished goods
        create_mock_execute_result(po_obj),  # get order after complete
    ]
    completed_po = await prod_engine.complete_production_order(po_obj.id)
    assert completed_po is not None


@pytest.mark.asyncio
async def test_mrp_planning_run(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    mrp_engine = MRPEngine(mock_db_session)
    org_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    raw_material_id = uuid.uuid4()

    po_obj = ProductionOrder(
        id=uuid.uuid4(),
        organization_id=org_id,
        production_number="PO-2026-0001",
        product_id=prod_id,
        planned_quantity=10.0,
        status="Planned",
    )

    raw_prod = Product(
        id=raw_material_id,
        sku="RAW-STEEL-01",
        product_name="High-Grade Steel Sheet",
        cost_price=50.0,
        selling_price=80.0,
    )

    bom_obj = BillOfMaterial(
        id=uuid.uuid4(),
        product_id=prod_id,
        bom_code="BOM-STEEL",
        items=[
            MagicMock(raw_material_id=raw_material_id, quantity=10.0)
        ],
    )

    from app.schemas.manufacturing_mrp import MRPRunCreate
    mrp_payload = MRPRunCreate(organization_id=org_id, planning_period="Q3-2026")

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None, [po_obj]),  # get active orders
        create_mock_execute_result(bom_obj),  # get BOM for product
        create_mock_execute_result(raw_prod),  # get raw material product
    ]

    mrp_result = await mrp_engine.run_mrp_planning(mrp_payload)
    assert mrp_result is not None
    assert mrp_result.planning_period == "Q3-2026"
    assert len(mrp_result.recommendations) > 0
    assert mrp_result.recommendations[0].action_type == "Purchase Requisition"


@pytest.mark.asyncio
async def test_manufacturing_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = ManufacturingAnalyticsService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.active_production_orders >= 0
    assert summary.machine_utilization_rate > 0.0
    assert summary.production_efficiency_percentage > 0.0
