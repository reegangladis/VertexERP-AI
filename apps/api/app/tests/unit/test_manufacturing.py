import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.manufacturing import (
    MRPRunCreate,
)
from app.services.manufacturing_service import ManufacturingService


@pytest.mark.asyncio
async def test_bom_cost_rollup_calculation():
    db_mock = AsyncMock()
    service = ManufacturingService(db_mock)
    org_id = uuid.uuid4()
    product_id = uuid.uuid4()

    # Mock BOM
    bom_id = uuid.uuid4()
    mock_bom = MagicMock()
    mock_bom.id = bom_id
    mock_bom.product_id = product_id
    mock_bom.base_quantity = 1.0
    mock_bom.total_cost = 0.0

    # Mock BOM items: Item 1 (qty 2 * cost 10 * scrap 1.05 = 21.0), Item 2 (qty 1 * cost 50 * scrap 1.0 = 50.0) -> total material = 71.0
    item1 = MagicMock(
        quantity=2.0,
        unit_cost=10.0,
        scrap_factor_percent=5.0,
        extended_cost=21.0,
        component_product_id=uuid.uuid4(),
    )
    item2 = MagicMock(
        quantity=1.0,
        unit_cost=50.0,
        scrap_factor_percent=0.0,
        extended_cost=50.0,
        component_product_id=uuid.uuid4(),
    )
    mock_bom.items = [item1, item2]

    service.bom_repo.get_with_items = AsyncMock(return_value=mock_bom)

    # Mock Routing query return empty list
    mock_exec = AsyncMock()
    mock_exec.scalars = MagicMock(
        return_value=MagicMock(all=MagicMock(return_value=[]))
    )
    db_mock.execute = AsyncMock(return_value=mock_exec)

    res = await service.calculate_cost_rollup(bom_id)
    assert res.material_cost == 71.0
    assert res.total_calculated_cost == 71.0


@pytest.mark.asyncio
async def test_mrp_engine_suggestion_generation():
    db_mock = AsyncMock()
    service = ManufacturingService(db_mock)
    org_id = uuid.uuid4()

    # Mock DB executions
    mock_exec_orders = MagicMock()
    mock_exec_orders.scalars = MagicMock(
        return_value=MagicMock(all=MagicMock(return_value=[]))
    )

    mock_prod = MagicMock(
        id=uuid.uuid4(),
        name="Raw Steel Plate",
        sku="RAW-STEEL-01",
        safety_stock=50,
        reorder_level=20,
    )
    mock_exec_products = MagicMock()
    mock_exec_products.scalars = MagicMock(
        return_value=MagicMock(all=MagicMock(return_value=[mock_prod]))
    )

    mock_wc = MagicMock(id=uuid.uuid4(), name="CNC Center", capacity_per_day_hours=16.0)
    mock_exec_wcs = MagicMock()
    mock_exec_wcs.scalars = MagicMock(
        return_value=MagicMock(all=MagicMock(return_value=[mock_wc]))
    )

    db_mock.execute = AsyncMock(
        side_effect=[mock_exec_orders, mock_exec_products, mock_exec_wcs]
    )
    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    data = MRPRunCreate(run_number="MRP-TEST-001")
    mrp = await service.run_mrp(org_id, data)

    assert mrp.run_number == "MRP-TEST-001"
    assert mrp.status == "COMPLETED"
    assert len(mrp.procurement_suggestions["items"]) == 1
    assert mrp.procurement_suggestions["items"][0]["sku"] == "RAW-STEEL-01"
