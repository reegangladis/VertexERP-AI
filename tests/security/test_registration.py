"""Security and functional test suite for Tenant and Admin User Registration."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_successful_registration(async_client: AsyncClient):
    """Verifies complete registration flow: tenant, org, user, credentials, and token."""
    payload = {
        "email": "admin@acmecorp.com",
        "password": "SuperSecretPassword123!",
        "full_name": "Acme Admin",
        "tenant_name": "Acme Corporation",
        "tenant_slug": "acme-corp",
        "organization_name": "Acme Global HQ",
        "tax_identifier": "US-EIN-998877",
    }
    response = await async_client.post("/api/v1/identity/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert "refresh_token" in data
    assert data["user_id"] is not None
    assert data["tenant_id"] is not None
    assert data["organization_id"] is not None
    assert "TenantAdmin" in data["roles"]
    assert len(data["permissions"]) > 0

    # Verify cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies


@pytest.mark.asyncio
async def test_registration_weak_passwords(async_client: AsyncClient):
    """Verifies that weak passwords violating complexity policy are rejected."""
    weak_passwords = [
        "short1!",  # < 12 chars
        "alllowercase123!",  # no uppercase
        "ALLUPPERCASE123!",  # no lowercase
        "NoNumbersInHere!",  # no numbers
        "NoSpecialChar123",  # no special char
    ]

    for pwd in weak_passwords:
        payload = {
            "email": f"user_{pwd[:4]}@example.com",
            "password": pwd,
            "full_name": "Test User",
            "tenant_name": "Test Tenant",
            "tenant_slug": f"slug-{pwd[:4].lower()}",
            "organization_name": "Test Org",
            "tax_identifier": "TX-12345",
        }
        response = await async_client.post("/api/v1/identity/auth/register", json=payload)
        assert response.status_code in (422, 400), f"Failed to reject weak password: {pwd}"


@pytest.mark.asyncio
async def test_registration_duplicate_slug_conflict(async_client: AsyncClient):
    """Verifies that registering a duplicate tenant slug returns 409 Conflict."""
    payload = {
        "email": "owner@duplicatecorp.com",
        "password": "ValidPassword123#",
        "full_name": "Corp Owner",
        "tenant_name": "Duplicate Corp",
        "tenant_slug": "duplicate-corp",
        "organization_name": "Duplicate HQ",
        "tax_identifier": "US-TAX-111",
    }
    first_res = await async_client.post("/api/v1/identity/auth/register", json=payload)
    assert first_res.status_code == 201

    # Attempt second registration with same slug
    second_res = await async_client.post("/api/v1/identity/auth/register", json=payload)
    assert second_res.status_code == 409
    error_data = second_res.json()
    assert "already registered" in error_data["detail"]
