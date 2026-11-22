"""Tests for Inventory and Procurement RBAC/Permissions."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_inventory_admin_access_and_unauthorized_rejection(async_client: AsyncClient):
    """Verifies that authenticated admin can access inventory and unauthenticated requests are 401."""
    # 1. Register Admin
    reg_payload = {
        "email": f"invadmin-{uuid.uuid4().hex[:4]}@test.com",
        "password": "InvAdminPassword123!",
        "full_name": "Inventory Admin",
        "tenant_name": "Inventory Corp",
        "tenant_slug": f"inv-corp-{uuid.uuid4().hex[:6]}",
        "organization_name": "Inv Operations",
        "tax_identifier": "INV-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Unauthenticated access to products returns 401
    async_client.cookies.clear()
    unauth_res = await async_client.get("/api/v1/inventory/products/")
    assert unauth_res.status_code == 401

    # 3. Authenticated admin access to products returns 200
    auth_res = await async_client.get("/api/v1/inventory/products/", headers=admin_headers)
    assert auth_res.status_code == 200
    assert "items" in auth_res.json()

    # 4. Create UoM via API
    uom_payload = {
        "code": f"U-{uuid.uuid4().hex[:4]}",
        "name": "Carton",
        "category": "COUNT",
        "is_base_unit": True,
        "conversion_factor": "1.000000",
    }
    uom_res = await async_client.post(
        "/api/v1/inventory/uom/", json=uom_payload, headers=admin_headers
    )
    assert uom_res.status_code == 201
    uom_id = uom_res.json()["id"]

    # 5. Create Warehouse via API
    wh_payload = {
        "code": f"WH-{uuid.uuid4().hex[:4]}",
        "name": "Central Storage",
        "warehouse_type": "STANDARD",
    }
    wh_res = await async_client.post(
        "/api/v1/inventory/warehouses/", json=wh_payload, headers=admin_headers
    )
    assert wh_res.status_code == 201
    wh_id = wh_res.json()["id"]

    # 6. Create Product via API
    prod_payload = {
        "sku": f"SKU-{uuid.uuid4().hex[:4]}",
        "name": "Heavy Duty Bracket",
        "uom_id": uom_id,
        "cost_price": "25.00",
        "selling_price": "45.00",
        "allow_negative_stock": False,
    }
    prod_res = await async_client.post(
        "/api/v1/inventory/products/", json=prod_payload, headers=admin_headers
    )
    assert prod_res.status_code == 201
    prod_id = prod_res.json()["id"]

    # 7. Create Supplier via API
    supp_payload = {
        "code": f"SUP-{uuid.uuid4().hex[:4]}",
        "name": "Industrial Fasteners Co",
        "email": "sales@fasteners.com",
    }
    supp_res = await async_client.post(
        "/api/v1/procurement/suppliers/", json=supp_payload, headers=admin_headers
    )
    assert supp_res.status_code == 201
    supp_id = supp_res.json()["id"]

    # 8. Create Purchase Order via API
    po_payload = {
        "supplier_id": supp_id,
        "warehouse_id": wh_id,
        "items": [
            {
                "product_id": prod_id,
                "description": "Heavy Duty Bracket",
                "quantity_ordered": "100.0000",
                "unit_price": "25.00",
                "discount_pct": "0.00",
                "tax_pct": "0.00",
            }
        ],
    }
    po_res = await async_client.post(
        "/api/v1/procurement/purchase-orders/", json=po_payload, headers=admin_headers
    )
    assert po_res.status_code == 201
    po_id = po_res.json()["id"]
    assert po_res.json()["grand_total"] == "2500.00"

    # 9. Approve PO via API
    appr_res = await async_client.post(
        f"/api/v1/procurement/purchase-orders/{po_id}/approve", headers=admin_headers
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "CONFIRMED"

    # 10. Create & Post Goods Receipt via API
    gr_payload = {
        "supplier_id": supp_id,
        "warehouse_id": wh_id,
        "purchase_order_id": po_id,
        "items": [
            {
                "product_id": prod_id,
                "quantity_received": "100.0000",
                "quantity_accepted": "100.0000",
                "unit_cost": "25.0000",
            }
        ],
    }
    gr_res = await async_client.post(
        "/api/v1/inventory/receipts/", json=gr_payload, headers=admin_headers
    )
    assert gr_res.status_code == 201
    gr_id = gr_res.json()["id"]

    post_gr_res = await async_client.post(
        f"/api/v1/inventory/receipts/{gr_id}/post", headers=admin_headers
    )
    assert post_gr_res.status_code == 200
    assert post_gr_res.json()["status"] == "POSTED"

    # 11. Verify Stock Balances and Valuation via API
    bal_res = await async_client.get("/api/v1/inventory/balances/", headers=admin_headers)
    assert bal_res.status_code == 200
    assert len(bal_res.json()["items"]) >= 1
    assert bal_res.json()["items"][0]["quantity_on_hand"] == "100.0000"

    val_res = await async_client.get("/api/v1/inventory/balances/valuation", headers=admin_headers)
    assert val_res.status_code == 200
    assert val_res.json()["total_valuation"] == "2500.00"
