"""Security test suite proving Strict Multi-Tenant Boundary Isolation and IDOR Immunity."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cross_tenant_data_isolation(async_client: AsyncClient):
    """
    CRITICAL MULTI-TENANCY TEST:
    Verifies that Tenant A cannot access, read, or mutate Tenant B entities (Users, Orgs, Roles)
    even when Tenant A has full TenantAdmin permissions within their own tenant.
    """
    # 1. Provision Tenant Alpha
    alpha_payload = {
        "email": "admin@alpha.com",
        "password": "AlphaPassword123!",
        "full_name": "Alpha Admin",
        "tenant_name": "Tenant Alpha",
        "tenant_slug": "tenant-alpha",
        "organization_name": "Alpha HQ",
        "tax_identifier": "ALPHA-001",
    }
    alpha_res = await async_client.post("/api/v1/identity/auth/register", json=alpha_payload)
    assert alpha_res.status_code == 201
    alpha_data = alpha_res.json()
    alpha_headers = {"Authorization": f"Bearer {alpha_data['access_token']}"}
    alpha_org_id = alpha_data["organization_id"]

    # 2. Provision Tenant Beta
    beta_payload = {
        "email": "admin@beta.com",
        "password": "BetaPassword123!",
        "full_name": "Beta Admin",
        "tenant_name": "Tenant Beta",
        "tenant_slug": "tenant-beta",
        "organization_name": "Beta HQ",
        "tax_identifier": "BETA-001",
    }
    beta_res = await async_client.post("/api/v1/identity/auth/register", json=beta_payload)
    assert beta_res.status_code == 201
    beta_data = beta_res.json()
    beta_user_id = beta_data["user_id"]
    beta_org_id = beta_data["organization_id"]

    # 3. Alpha Admin attempts to fetch Beta Admin user by ID -> 404 Not Found (zero IDOR)
    cross_user_res = await async_client.get(
        f"/api/v1/identity/users/{beta_user_id}", headers=alpha_headers
    )
    assert cross_user_res.status_code == 404
    assert "not found" in cross_user_res.json()["detail"].lower()

    # 4. Alpha Admin attempts to fetch Beta Organization by ID -> 404 Not Found
    cross_org_res = await async_client.get(
        f"/api/v1/organizations/{beta_org_id}", headers=alpha_headers
    )
    assert cross_org_res.status_code == 404
    assert "not found" in cross_org_res.json()["detail"].lower()

    # 5. Alpha Admin attempts to assign role to Beta user -> 404 Not Found
    # First get an Alpha role
    roles_res = await async_client.get("/api/v1/identity/roles/", headers=alpha_headers)
    assert roles_res.status_code == 200
    alpha_role_id = roles_res.json()[0]["id"]

    assign_payload = {
        "user_id": beta_user_id,
        "role_id": alpha_role_id,
        "organization_id": alpha_org_id,
    }
    cross_assign_res = await async_client.post(
        "/api/v1/identity/roles/assign", json=assign_payload, headers=alpha_headers
    )
    assert cross_assign_res.status_code == 404
