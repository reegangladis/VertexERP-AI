"""Security test suite for Multi-Organization Memberships and Organization Switching."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_organization_creation_and_context_switching(async_client: AsyncClient):
    """Verifies creating secondary organizations and switching active organization context."""
    # 1. Register Tenant Admin
    reg_payload = {
        "email": "admin@multiorg.com",
        "password": "MultiOrgPassword123!",
        "full_name": "MultiOrg Admin",
        "tenant_name": "MultiOrg Corp",
        "tenant_slug": "multiorg-corp",
        "organization_name": "Primary Org",
        "tax_identifier": "MO-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_data = reg_res.json()
    admin_headers = {"Authorization": f"Bearer {admin_data['access_token']}"}

    # 2. Admin creates Secondary Organization
    new_org_payload = {
        "name": "European Subsidiary Ltd",
        "legal_name": "European Subsidiary Ltd",
        "tax_identifier": "EU-VAT-999888",
        "base_currency": "EUR",
        "fiscal_year_start_month": 1,
    }
    create_org_res = await async_client.post(
        "/api/v1/organizations/", json=new_org_payload, headers=admin_headers
    )
    assert create_org_res.status_code == 201
    secondary_org_id = create_org_res.json()["id"]

    # 3. Admin switches to Secondary Organization -> receives scoped token
    switch_res = await async_client.post(
        f"/api/v1/organizations/{secondary_org_id}/switch", headers=admin_headers
    )
    assert switch_res.status_code == 200
    switched_data = switch_res.json()
    assert switched_data["organization_id"] == secondary_org_id
    assert switched_data["access_token"] is not None


@pytest.mark.asyncio
async def test_unauthorized_organization_switch_blocked(async_client: AsyncClient):
    """Verifies that a user cannot switch to an organization where they lack active membership."""
    # 1. Register Tenant Admin
    admin_payload = {
        "email": "boss@orgisolation.com",
        "password": "BossPassword123!",
        "full_name": "Boss Admin",
        "tenant_name": "Org Isolation Corp",
        "tenant_slug": "org-isolation-corp",
        "organization_name": "Main Org",
        "tax_identifier": "OI-001",
    }
    admin_res = await async_client.post("/api/v1/identity/auth/register", json=admin_payload)
    assert admin_res.status_code == 201
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # 2. Admin creates Private Organization
    private_org_payload = {
        "name": "Classified Branch",
        "legal_name": "Classified Branch LLC",
        "tax_identifier": "OI-CLASS-99",
    }
    private_org_res = await async_client.post(
        "/api/v1/organizations/", json=private_org_payload, headers=admin_headers
    )
    assert private_org_res.status_code == 201
    private_org_id = private_org_res.json()["id"]

    # 3. Admin creates standard user (member only of Main Org)
    user_payload = {
        "email": "employee@orgisolation.com",
        "password": "EmployeePassword123!",
        "full_name": "Regular Employee",
    }
    create_user_res = await async_client.post(
        "/api/v1/identity/users/", json=user_payload, headers=admin_headers
    )
    assert create_user_res.status_code == 201

    # 4. Standard user logs in
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "employee@orgisolation.com",
            "password": "EmployeePassword123!",
            "tenant_slug": "org-isolation-corp",
        },
    )
    assert login_res.status_code == 200
    employee_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 5. Non-member switch attempt -> 403 Forbidden
    switch_res = await async_client.post(
        f"/api/v1/organizations/{private_org_id}/switch", headers=employee_headers
    )
    assert switch_res.status_code == 403
    assert "does not have access" in switch_res.json()["detail"].lower()
