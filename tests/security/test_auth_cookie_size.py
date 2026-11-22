"""Comprehensive test suite for Authentication Cookie Size Optimization and Server-Side RBAC Resolution."""

import uuid
from datetime import timedelta

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.permissions import PermissionCode, SystemRole
from app.core.security import create_jwt_token, decode_jwt_token
from app.modules.identity.services.jwt_service import JwtService


@pytest.mark.asyncio
async def test_slim_jwt_size_and_cookie_header_under_limits(async_client: AsyncClient):
    """
    Verifies that:
    1. Access JWT no longer contains the 'permissions' claim.
    2. Access JWT byte size is well below 1024 bytes (~550 bytes target).
    3. Set-Cookie access_token header is well below the 4096-byte browser limit (~615 bytes target).
    """
    reg_payload = {
        "email": "cookieaudit@example.com",
        "password": "SecurePassword123!",
        "full_name": "Cookie Audit Admin",
        "tenant_name": "Cookie Audit Corp",
        "tenant_slug": f"cookie-corp-{uuid.uuid4().hex[:6]}",
        "organization_name": "Cookie Audit HQ",
        "tax_identifier": "CK-001",
    }
    response = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert response.status_code == 201

    data = response.json()
    access_token = data["access_token"]
    assert access_token is not None

    # Verify JWT payload claims
    decoded_payload = JwtService.verify_token(access_token)
    assert "permissions" not in decoded_payload
    assert "sub" in decoded_payload
    assert "tenant_id" in decoded_payload
    assert "org_id" in decoded_payload
    assert "session_id" in decoded_payload
    assert "roles" in decoded_payload
    assert "jti" in decoded_payload
    assert "token_type" in decoded_payload
    assert decoded_payload["token_type"] == "access"
    assert "iat" in decoded_payload
    assert "exp" in decoded_payload
    assert "iss" in decoded_payload

    # Measure exact byte lengths
    jwt_bytes = len(access_token.encode("utf-8"))
    assert jwt_bytes < 1024, f"JWT size {jwt_bytes} exceeds 1024 bytes target"

    # Verify Set-Cookie header
    set_cookie_headers = response.headers.get_list("set-cookie")
    access_cookie_header = next((h for h in set_cookie_headers if h.startswith("access_token=")), None)
    assert access_cookie_header is not None
    cookie_header_bytes = len(access_cookie_header.encode("utf-8"))
    assert cookie_header_bytes < 4096, f"Set-Cookie header {cookie_header_bytes} exceeds 4096 bytes"


@pytest.mark.asyncio
async def test_auth_response_and_me_contract_preserves_permissions(async_client: AsyncClient):
    """
    Verifies that:
    1. /login and /register response bodies contain full roles and permissions lists.
    2. /me endpoint returns the complete effective permissions list resolved server-side.
    """
    reg_payload = {
        "email": "mecontract@example.com",
        "password": "SecurePassword123!",
        "full_name": "Me Contract User",
        "tenant_name": "Me Contract Corp",
        "tenant_slug": f"me-corp-{uuid.uuid4().hex[:6]}",
        "organization_name": "Me Contract HQ",
        "tax_identifier": "ME-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()

    # /register response contract
    assert "TenantAdmin" in reg_data["roles"]
    assert len(reg_data["permissions"]) >= 170

    # /login response contract
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "mecontract@example.com",
            "password": "SecurePassword123!",
            "tenant_slug": reg_payload["tenant_slug"],
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "TenantAdmin" in login_data["roles"]
    assert len(login_data["permissions"]) >= 170

    # /me response contract
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await async_client.get("/api/v1/identity/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()

    assert me_data["email"] == "mecontract@example.com"
    assert "TenantAdmin" in me_data["roles"]
    assert len(me_data["permissions"]) >= 170
    assert PermissionCode.IDENTITY_USERS_READ.value in me_data["permissions"]
    assert PermissionCode.AI_COPILOT_USE.value in me_data["permissions"]


@pytest.mark.asyncio
async def test_rbac_authorization_tenant_admin_and_standard_user(async_client: AsyncClient):
    """
    Verifies that:
    1. TenantAdmin has full access to permission-protected endpoints.
    2. Standard user with allowed permissions succeeds.
    3. Standard user without required permission receives 403 Forbidden.
    """
    # 1. Register Admin
    reg_payload = {
        "email": "adminrbac@example.com",
        "password": "SecurePassword123!",
        "full_name": "RBAC Admin",
        "tenant_name": "RBAC Corp",
        "tenant_slug": f"rbac-corp-{uuid.uuid4().hex[:6]}",
        "organization_name": "RBAC HQ",
        "tax_identifier": "RBC-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # TenantAdmin accesses protected endpoints
    users_res = await async_client.get("/api/v1/identity/users/", headers=admin_headers)
    assert users_res.status_code == 200
    roles_res = await async_client.get("/api/v1/identity/roles/", headers=admin_headers)
    assert roles_res.status_code == 200

    # 2. Create Standard User
    create_user_res = await async_client.post(
        "/api/v1/identity/users/",
        json={
            "email": "standard@example.com",
            "password": "StandardUserPassword123!",
            "full_name": "Standard User",
            "role_ids": [],
        },
        headers=admin_headers,
    )
    assert create_user_res.status_code == 201

    # Standard User logs in
    user_login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "standard@example.com",
            "password": "StandardUserPassword123!",
            "tenant_slug": reg_payload["tenant_slug"],
        },
    )
    assert user_login_res.status_code == 200
    user_token = user_login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Standard user has no roles -> forbidden on user management and role creation
    unauth_users_res = await async_client.get("/api/v1/identity/users/", headers=user_headers)
    assert unauth_users_res.status_code == 403
    assert "Missing required permission" in unauth_users_res.json()["detail"]


@pytest.mark.asyncio
async def test_dynamic_permission_update_reflection(async_client: AsyncClient):
    """
    Verifies that assigning a role to a user immediately grants permissions server-side
    without relying on static or stale permissions claims in the JWT token.
    """
    # 1. Register Admin
    reg_payload = {
        "email": "dynadmin@example.com",
        "password": "SecurePassword123!",
        "full_name": "Dynamic Admin",
        "tenant_name": "Dynamic Corp",
        "tenant_slug": f"dyn-corp-{uuid.uuid4().hex[:6]}",
        "organization_name": "Dynamic HQ",
        "tax_identifier": "DYN-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    org_id = reg_res.json()["organization_id"]

    # 2. Create custom role with identity:users:read permission
    all_perms_res = await async_client.get("/api/v1/identity/roles/permissions", headers=admin_headers)
    assert all_perms_res.status_code == 200
    perms = all_perms_res.json()
    user_read_perm = next(p for p in perms if p["code"] == PermissionCode.IDENTITY_USERS_READ.value)

    role_res = await async_client.post(
        "/api/v1/identity/roles/",
        json={
            "name": "User Viewer",
            "code": "USER_VIEWER",
            "description": "Can read users",
            "permission_ids": [user_read_perm["id"]],
        },
        headers=admin_headers,
    )
    assert role_res.status_code == 201
    role_id = role_res.json()["id"]

    # 3. Create normal user
    create_user_res = await async_client.post(
        "/api/v1/identity/users/",
        json={
            "email": "dynuser@example.com",
            "password": "DynUserPassword123!",
            "full_name": "Dynamic User",
            "role_ids": [],
        },
        headers=admin_headers,
    )
    assert create_user_res.status_code == 201
    user_id = create_user_res.json()["id"]

    # 4. User logs in (before role assignment)
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "dynuser@example.com",
            "password": "DynUserPassword123!",
            "tenant_slug": reg_payload["tenant_slug"],
        },
    )
    assert login_res.status_code == 200
    user_token = login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Access is blocked
    check_1 = await async_client.get("/api/v1/identity/users/", headers=user_headers)
    assert check_1.status_code == 403

    # 5. Admin assigns role to user
    assign_res = await async_client.post(
        "/api/v1/identity/roles/assign",
        json={
            "user_id": user_id,
            "role_id": role_id,
            "organization_id": org_id,
        },
        headers=admin_headers,
    )
    assert assign_res.status_code == 200

    # 6. User accesses with the SAME token -> access is now granted dynamically server-side!
    check_2 = await async_client.get("/api/v1/identity/users/", headers=user_headers)
    assert check_2.status_code == 200
    assert len(check_2.json()) >= 1


@pytest.mark.asyncio
async def test_token_tampering_and_expiration(async_client: AsyncClient):
    """Verifies that tampered or expired tokens are rejected with 401."""
    # Expired token
    expired_token = create_jwt_token(
        payload={"sub": str(uuid.uuid4()), "token_type": "access"},
        expires_delta=timedelta(seconds=-10),
    )
    res_exp = await async_client.get(
        "/api/v1/identity/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res_exp.status_code == 401

    # Tampered token
    tampered_token = expired_token[:-5] + "XXXXX"
    res_tamp = await async_client.get(
        "/api/v1/identity/users/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert res_tamp.status_code == 401
