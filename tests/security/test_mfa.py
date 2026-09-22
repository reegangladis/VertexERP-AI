"""Security test suite for Multi-Factor Authentication (RFC 6238 TOTP and Recovery Codes)."""

import pytest
from httpx import AsyncClient

from app.core.security import compute_totp_code


@pytest.mark.asyncio
async def test_mfa_setup_activation_and_login_flow(async_client: AsyncClient):
    """Verifies complete MFA lifecycle: setup, activation, challenge, TOTP, and recovery."""
    # 1. Register user
    reg_payload = {
        "email": "mfauser@test.com",
        "password": "MfaTestPassword123!",
        "full_name": "MFA User",
        "tenant_name": "MFA Corp",
        "tenant_slug": "mfa-corp",
        "organization_name": "MFA Org",
        "tax_identifier": "MFA-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    access_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Setup MFA enrollment
    setup_res = await async_client.post("/api/v1/identity/mfa/setup", headers=headers)
    assert setup_res.status_code == 200
    setup_data = setup_res.json()
    totp_secret = setup_data["secret"]
    recovery_codes = setup_data["recovery_codes"]
    assert len(recovery_codes) == 8
    assert "otpauth://" in setup_data["otpauth_url"]

    # 3. Verify and activate MFA
    valid_code = compute_totp_code(totp_secret)
    verify_res = await async_client.post(
        "/api/v1/identity/mfa/verify",
        json={"code": valid_code},
        headers=headers,
    )
    assert verify_res.status_code == 200
    assert "successfully activated" in verify_res.json()["message"]

    # 4. Login without MFA code -> returns MFA challenge
    challenge_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "mfauser@test.com",
            "password": "MfaTestPassword123!",
            "tenant_slug": "mfa-corp",
        },
    )
    assert challenge_res.status_code == 200
    challenge_data = challenge_res.json()
    assert challenge_data["mfa_required"] is True
    assert challenge_data["mfa_challenge_token"] is not None

    # 5. Login with valid TOTP code -> returns full access token
    totp_login_code = compute_totp_code(totp_secret)
    mfa_login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "mfauser@test.com",
            "password": "MfaTestPassword123!",
            "tenant_slug": "mfa-corp",
            "mfa_code": totp_login_code,
        },
    )
    assert mfa_login_res.status_code == 200
    mfa_token_data = mfa_login_res.json()
    assert mfa_token_data["access_token"] is not None
    assert mfa_token_data["mfa_required"] is False

    # 6. Login with Recovery Code -> burns code and returns token
    recovery_code_to_use = recovery_codes[0]
    recovery_login_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "mfauser@test.com",
            "password": "MfaTestPassword123!",
            "tenant_slug": "mfa-corp",
            "mfa_code": recovery_code_to_use,
        },
    )
    assert recovery_login_res.status_code == 200
    assert recovery_login_res.json()["access_token"] is not None

    # 7. Reusing same burned recovery code fails with 401
    reuse_recovery_res = await async_client.post(
        "/api/v1/identity/auth/login",
        json={
            "email": "mfauser@test.com",
            "password": "MfaTestPassword123!",
            "tenant_slug": "mfa-corp",
            "mfa_code": recovery_code_to_use,
        },
    )
    assert reuse_recovery_res.status_code == 401
