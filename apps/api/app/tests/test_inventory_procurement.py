import uuid
from datetime import date
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, status

from app.models.inventory_procurement_v11 import (
    GoodsReceipt,
    Product,
    PurchaseOrder,
    StockLevel,
    Supplier,
    Warehouse,
)
from app.services.inventory_procurement import (
    InventoryReportService,
    ProductService,
    PurchaseService,
    StockService,
    SupplierService,
    WarehouseService,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_product_creation_and_duplicate_sku_validation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = ProductService(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.inventory_procurement import ProductCreate
    payload = ProductCreate(
        organization_id=org_id,
        sku="SKU-SERVER-X1",
        barcode="1234567890123",
        product_name="Enterprise Rack Server X1",
        cost_price=1500.0,
        selling_price=2500.0,
    )

    prod_obj = Product(
        id=uuid.uuid4(),
        organization_id=org_id,
        sku=payload.sku,
        barcode=payload.barcode,
        product_name=payload.product_name,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        status="Active",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # sku check
        create_mock_execute_result(None),  # barcode check
    ]
    prod = await service.create_product(payload)
    assert prod is not None

    # Duplicate SKU validation check
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(prod_obj)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_product(payload)
    assert exc_info.value.status_code == 400
    assert "already exists in this organization" in exc_info.value.detail


@pytest.mark.asyncio
async def test_warehouse_and_stock_adjustment(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    wh_service = WarehouseService(mock_db_session)
    stock_service = StockService(mock_db_session)
    org_id = uuid.uuid4()
    wh_id = uuid.uuid4()
    prod_id = uuid.uuid4()

    from app.schemas.inventory_procurement import StockAdjustmentPayload, WarehouseCreate
    wh_payload = WarehouseCreate(
        organization_id=org_id,
        warehouse_name="Central Distribution Center",
        warehouse_code="WH-CENTRAL-01",
    )

    wh_obj = Warehouse(
        id=wh_id,
        organization_id=org_id,
        warehouse_name=wh_payload.warehouse_name,
        warehouse_code=wh_payload.warehouse_code,
        status="Active",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
    ]
    wh = await wh_service.create_warehouse(wh_payload)
    assert wh is not None

    # Stock Adjustment
    stock_obj = StockLevel(
        id=uuid.uuid4(),
        warehouse_id=wh_id,
        product_id=prod_id,
        available_quantity=100.0,
        reserved_quantity=0.0,
        damaged_quantity=0.0,
        reorder_quantity=10.0,
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # get stock
        create_mock_execute_result(stock_obj),  # get updated stock
    ]
    updated_stock = await stock_service.adjust_stock(
        StockAdjustmentPayload(
            warehouse_id=wh_id,
            product_id=prod_id,
            new_quantity=100.0,
            adjustment_reason="Initial Stock Audit",
        )
    )
    assert updated_stock is not None
    assert updated_stock.available_quantity == 100.0


@pytest.mark.asyncio
async def test_purchase_order_and_goods_receipt(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    p_service = PurchaseService(mock_db_session)
    supp_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    wh_id = uuid.uuid4()

    from app.schemas.inventory_procurement import (
        GoodsReceiptCreate,
        GoodsReceiptItemCreate,
        PurchaseOrderCreate,
        PurchaseOrderItemCreate,
    )

    po_payload = PurchaseOrderCreate(
        supplier_id=supp_id,
        purchase_order_number="PO-2026-0001",
        order_date=date(2026, 8, 1),
        expected_delivery=date(2026, 8, 15),
        discount=100.0,
        items=[
            PurchaseOrderItemCreate(
                product_id=prod_id,
                quantity=50.0,
                unit_price=200.0,
                tax_amount=50.0,
            )
        ],
    )

    supp_obj = Supplier(id=supp_id, organization_id=uuid.uuid4(), supplier_code="SUPP-01", company_name="Tech Supplier Inc", email="supp@tech.com")
    po_obj = PurchaseOrder(
        id=uuid.uuid4(),
        supplier_id=supp_id,
        purchase_order_number="PO-2026-0001",
        order_date=po_payload.order_date,
        expected_delivery=po_payload.expected_delivery,
        subtotal=10000.0,
        tax=50.0,
        discount=100.0,
        grand_total=9950.0,
        status="Draft",
        items=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(supp_obj),
        create_mock_execute_result(None),
        create_mock_execute_result(po_obj),
    ]
    po = await p_service.create_purchase_order(po_payload)
    assert po is not None
    assert po.purchase_order_number == "PO-2026-0001"

    # Goods Receipt
    gr_obj = GoodsReceipt(
        id=uuid.uuid4(),
        purchase_order_id=po_obj.id,
        receipt_number="GR-2026-0001",
        receipt_date=date(2026, 8, 10),
        status="Received",
        items=[],
    )

    gr_payload = GoodsReceiptCreate(
        purchase_order_id=po_obj.id,
        receipt_number="GR-2026-0001",
        receipt_date=date(2026, 8, 10),
        items=[
            GoodsReceiptItemCreate(
                product_id=prod_id,
                received_quantity=50.0,
                warehouse_id=wh_id,
            )
        ],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(po_obj),
        create_mock_execute_result(None),  # stock check
        create_mock_execute_result(po_obj),  # update PO status
        create_mock_execute_result(gr_obj),  # get gr with items
    ]
    gr = await p_service.receive_goods(gr_payload)
    assert gr is not None
    assert gr.status == "Received"


@pytest.mark.asyncio
async def test_inventory_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = InventoryReportService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_products == 0
    assert summary.total_warehouses == 0
    assert summary.total_stock_value == 0.0
