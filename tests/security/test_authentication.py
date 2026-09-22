"""Security test suite for User Authentication, Credential Verification, and Account Lockout."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_successful_login(async_client: AsyncClient):
    """Verifies that an authenticated user receives valid tokens upon login."""
    # 1. Register tenant
    reg_payload = {
        "email": "user@securelogin.com",
        "password": "CorrectPassword123!",
        "full_name": "Login User",
        "tenant_name": "Secure Login Tenant",
        "tenant_slug": "secure-login-tenant",
        "organization_name": "Secure Org",
        "tax_identifier": "SL-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # 2. Login
    login_payload = {
        "email": "user@securelogin.com",
        "password": "CorrectPassword123!",
        "tenant_slug": "secure-login-tenant",
    }
    login_res = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
    assert login_res.status_code == 200
    data = login_res.json()

    assert data["access_token"] is not None
    assert data["refresh_token"] is not None
    assert data["user_id"] is not None
    assert "TenantAdmin" in data["roles"]


@pytest.mark.asyncio
async def test_invalid_password_returns_401(async_client: AsyncClient):
    """Verifies that invalid password attempts return 401 Unauthorized."""
    reg_payload = {
        "email": "wrongpwd@company.com",
        "password": "ValidPassword123!",
        "full_name": "Wrong Password Test",
        "tenant_name": "Wrong Pwd Tenant",
        "tenant_slug": "wrong-pwd-tenant",
        "organization_name": "Wrong Pwd Org",
        "tax_identifier": "WP-001",
    }
    await async_client.post("/api/v1/identity/auth/register", json=reg_payload)

    login_payload = {
        "email": "wrongpwd@company.com",
        "password": "IncorrectPassword123!",
        "tenant_slug": "wrong-pwd-tenant",
    }
    login_res = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
    assert login_res.status_code == 401
    assert "Invalid email or password" in login_res.json()["detail"]


@pytest.mark.asyncio
async def test_account_lockout_after_five_failed_attempts(async_client: AsyncClient):
    """Verifies that 5 consecutive failed login attempts trigger an account lockout."""
    reg_payload = {
        "email": "lockout@company.com",
        "password": "ValidPassword123!",
        "full_name": "Lockout Test",
        "tenant_name": "Lockout Tenant",
        "tenant_slug": "lockout-tenant",
        "organization_name": "Lockout Org",
        "tax_identifier": "LO-001",
    }
    await async_client.post("/api/v1/identity/auth/register", json=reg_payload)

    login_payload = {
        "email": "lockout@company.com",
        "password": "WrongPasswordAttempt!",
        "tenant_slug": "lockout-tenant",
    }

    # First 4 failed attempts
    for _ in range(4):
        res = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]

    # 5th failed attempt triggers lockout
    res_5 = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
    assert res_5.status_code == 401

    # 6th attempt should return lockout message
    res_6 = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
    assert res_6.status_code == 401
    assert "Account is temporarily locked" in res_6.json()["detail"]


@pytest.mark.asyncio
async def test_nonexistent_user_returns_401(async_client: AsyncClient):
    """Verifies that non-existent email returns generic 401 to prevent user enumeration."""
    login_payload = {
        "email": "ghost@nonexistent.com",
        "password": "SomePassword123!",
    }
    res = await async_client.post("/api/v1/identity/auth/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]
