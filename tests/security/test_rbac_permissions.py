"""Security test suite for RBAC & ABAC Fine-Grained Permissions."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rbac_admin_full_access(async_client: AsyncClient):
    """Verifies that TenantAdmin has full permissions across all management endpoints."""
    reg_payload = {
        "email": "rbacadmin@test.com",
        "password": "RbacAdminPassword123!",
        "full_name": "RBAC Admin",
        "tenant_name": "RBAC Corp",
        "tenant_slug": "rbac-corp",
        "organization_name": "RBAC Org",
        "tax_identifier": "RBA-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Access user list (requires identity:users:read)
    users_res = await async_client.get("/api/v1/identity/users/", headers=headers)
    assert users_res.status_code == 200
    assert len(users_res.json()) >= 1

    # 2. Access permissions list (requires identity:roles:read)
    perms_res = await async_client.get("/api/v1/identity/roles/permissions", headers=headers)
    assert perms_res.status_code == 200
    assert len(perms_res.json()) > 0

    # 3. Access organization list (requires organization:organizations:read)
    orgs_res = await async_client.get("/api/v1/organizations/", headers=headers)
    assert orgs_res.status_code == 200


@pytest.mark.asyncio
async def test_rbac_standard_user_lacks_permission_returns_403(async_client: AsyncClient):
    """Verifies that a user lacking required permission code receives 403 Forbidden."""
    # 1. Register Admin
    reg_payload = {
        "email": "owner@permtest.com",
        "password": "OwnerPassword123!",
        "full_name": "Tenant Owner",
        "tenant_name": "Perm Test Corp",
        "tenant_slug": "perm-test-corp",
        "organization_name": "Perm Test Org",
        "tax_identifier": "PERM-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_headers = {"Authorization": f"Bearer {reg_res.json()['access_token']}"}

    # 2. Admin creates a standard user with NO roles/permissions
    create_user_payload = {
        "email": "restricted@permtest.com",
        "password": "RestrictedUser123!",
        "full_name": "Restricted User",
        "role_ids": [],
    }
    create_res = await async_client.post(
        "/api/v1/identity/users/", json=create_user_payload, headers=admin_headers
    )
    assert create_res.status_code == 201

    # 3. Standard user logs in
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "restricted@permtest.com",
            "password": "RestrictedUser123!",
            "tenant_slug": "perm-test-corp",
        },
    )
    assert login_res.status_code == 200
    user_token = login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 4. Standard user accesses their own profile -> 200 OK
    me_res = await async_client.get("/api/v1/identity/users/me", headers=user_headers)
    assert me_res.status_code == 200

    # 5. Standard user attempts to list tenant users (requires identity:users:read) -> 403 Forbidden
    unauth_users_res = await async_client.get("/api/v1/identity/users/", headers=user_headers)
    assert unauth_users_res.status_code == 403
    assert "Missing required permission" in unauth_users_res.json()["detail"]

    # 6. Standard user attempts to create role (requires identity:roles:create) -> 403 Forbidden
    role_payload = {
        "name": "Hacker Role",
        "code": "HACKER_ROLE",
        "description": "Unauthorized role",
    }
    unauth_role_res = await async_client.post(
        "/api/v1/identity/roles/", json=role_payload, headers=user_headers
    )
    assert unauth_role_res.status_code == 403
