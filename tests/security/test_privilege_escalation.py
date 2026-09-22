"""Security test suite proving Privilege Escalation Prevention."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_privilege_escalation_role_assignment_blocked(async_client: AsyncClient):
    """
    CRITICAL SECURITY TEST:
    Verifies that a non-admin user cannot escalate privileges to administrative roles.
    """
    # 1. Register Tenant Admin
    admin_payload = {
        "email": "legitadmin@escalate.com",
        "password": "LegitAdminPassword123!",
        "full_name": "Legit Admin",
        "tenant_name": "Escalate Corp",
        "tenant_slug": "escalate-corp",
        "organization_name": "Escalate Org",
        "tax_identifier": "ESC-001",
    }
    admin_res = await async_client.post("/api/v1/identity/auth/register", json=admin_payload)
    assert admin_res.status_code == 201
    admin_data = admin_res.json()
    admin_headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    org_id = admin_data["organization_id"]

    # 2. Get TenantAdmin role ID
    roles_res = await async_client.get("/api/v1/identity/roles/", headers=admin_headers)
    assert roles_res.status_code == 200
    tenant_admin_role_id = next(r["id"] for r in roles_res.json() if r["code"] == "TenantAdmin")

    # 3. Admin creates standard user
    create_res = await async_client.post(
        "/api/v1/identity/users/",
        json={
            "email": "attacker@escalate.com",
            "password": "AttackerPassword123!",
            "full_name": "Attacker User",
        },
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    attacker_user_id = create_res.json()["id"]

    # 4. Standard user logs in
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "attacker@escalate.com",
            "password": "AttackerPassword123!",
            "tenant_slug": "escalate-corp",
        },
    )
    assert login_res.status_code == 200
    attacker_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 5. Attacker attempts to assign TenantAdmin role to themselves -> 403 Forbidden
    escalate_payload = {
        "user_id": attacker_user_id,
        "role_id": tenant_admin_role_id,
        "organization_id": org_id,
    }
    escalate_res = await async_client.post(
        "/api/v1/identity/roles/assign",
        json=escalate_payload,
        headers=attacker_headers,
    )
    assert escalate_res.status_code == 403
    assert "Missing required permission" in escalate_res.json()["detail"]
