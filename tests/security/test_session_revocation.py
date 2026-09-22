"""Security test suite for Session Management, Logout, Redis JTI Blacklisting, and Revocation."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logout_and_jti_blacklisting(async_client: AsyncClient):
    """Verifies that logout immediately blacklists the JWT access token and revokes session."""
    # 1. Register
    reg_payload = {
        "email": "logout@test.com",
        "password": "LogoutPassword123!",
        "full_name": "Logout User",
        "tenant_name": "Logout Corp",
        "tenant_slug": "logout-corp",
        "organization_name": "Logout Org",
        "tax_identifier": "LOG-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    access_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Access protected endpoint before logout
    me_res = await async_client.get("/api/v1/identity/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "logout@test.com"

    # 3. Logout
    logout_res = await async_client.post("/api/v1/identity/auth/logout", headers=headers)
    assert logout_res.status_code == 204

    # 4. Attempt to access protected endpoint with the revoked access token
    post_logout_res = await async_client.get("/api/v1/identity/users/me", headers=headers)
    assert post_logout_res.status_code == 401
    assert "revoked" in post_logout_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_and_revoke_specific_session(async_client: AsyncClient):
    """Verifies listing active sessions and revoking a specific session."""
    reg_payload = {
        "email": "sessionmgr@test.com",
        "password": "SessionMgrPassword123!",
        "full_name": "Session User",
        "tenant_name": "Session Corp",
        "tenant_slug": "session-corp",
        "organization_name": "Session Org",
        "tax_identifier": "SES-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    access_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # List active sessions
    sessions_res = await async_client.get("/api/v1/identity/auth/sessions", headers=headers)
    assert sessions_res.status_code == 200
    sessions = sessions_res.json()
    assert len(sessions) == 1
    session_id = sessions[0]["id"]

    # Revoke specific session
    del_res = await async_client.delete(
        f"/api/v1/identity/auth/sessions/{session_id}", headers=headers
    )
    assert del_res.status_code == 204

    # Token should now be blacklisted
    me_res = await async_client.get("/api/v1/identity/users/me", headers=headers)
    assert me_res.status_code == 401


@pytest.mark.asyncio
async def test_password_change_invalidates_active_sessions(async_client: AsyncClient):
    """Verifies that changing password revokes all active sessions across devices."""
    reg_payload = {
        "email": "pwdchange@test.com",
        "password": "InitialPassword123!",
        "full_name": "Pwd Change User",
        "tenant_name": "Pwd Corp",
        "tenant_slug": "pwd-corp",
        "organization_name": "Pwd Org",
        "tax_identifier": "PWD-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    old_access_token = reg_res.json()["access_token"]
    old_headers = {"Authorization": f"Bearer {old_access_token}"}

    # Change password
    change_res = await async_client.post(
        "/api/v1/identity/auth/change-password",
        json={"current_password": "InitialPassword123!", "new_password": "NewSuperPassword123!"},
        headers=old_headers,
    )
    assert change_res.status_code == 204

    # Old token is now revoked
    old_access_res = await async_client.get("/api/v1/identity/users/me", headers=old_headers)
    assert old_access_res.status_code == 401

    # Login with new password succeeds
    login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "pwdchange@test.com",
            "password": "NewSuperPassword123!",
            "tenant_slug": "pwd-corp",
        },
    )
    assert login_res.status_code == 200
