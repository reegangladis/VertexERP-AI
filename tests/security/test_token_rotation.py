"""Security test suite for Single-Use Refresh Token Rotation and Replay Attack Reuse Detection."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_token_rotation(async_client: AsyncClient):
    """Verifies that refreshing a token invalidates the old token and issues a new pair."""
    # 1. Register
    reg_payload = {
        "email": "rotation@acme.com",
        "password": "RotationPassword123!",
        "full_name": "Rotation User",
        "tenant_name": "Rotation Corp",
        "tenant_slug": "rotation-corp",
        "organization_name": "Rotation Org",
        "tax_identifier": "ROT-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    initial_tokens = reg_res.json()
    first_refresh_token = initial_tokens["refresh_token"]

    # 2. Refresh token rotation (1st time)
    refresh_res_1 = await async_client.post(
        "/api/v1/identity/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert refresh_res_1.status_code == 200
    rotated_tokens_1 = refresh_res_1.json()
    second_refresh_token = rotated_tokens_1["refresh_token"]
    assert second_refresh_token != first_refresh_token
    assert rotated_tokens_1["access_token"] is not None

    # 3. Refresh token rotation (2nd time with newly issued token)
    refresh_res_2 = await async_client.post(
        "/api/v1/identity/auth/refresh",
        json={"refresh_token": second_refresh_token},
    )
    assert refresh_res_2.status_code == 200
    rotated_tokens_2 = refresh_res_2.json()
    assert rotated_tokens_2["refresh_token"] != second_refresh_token


@pytest.mark.asyncio
async def test_replay_attack_reuse_revokes_all_sessions(async_client: AsyncClient):
    """
    CRITICAL SECURITY TEST:
    Verifies that presenting an already-rotated refresh token (replay attack)
    triggers full session revocation for that user across all devices.
    """
    # 1. Register user
    reg_payload = {
        "email": "victim@replaycorp.com",
        "password": "ReplayPassword123!",
        "full_name": "Replay Victim",
        "tenant_name": "Replay Corp",
        "tenant_slug": "replay-corp",
        "organization_name": "Replay Org",
        "tax_identifier": "REP-001",
    }
    reg_res = await async_client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    initial_refresh_token = reg_res.json()["refresh_token"]

    # 2. Normal rotation: User rotates token
    legit_refresh_res = await async_client.post(
        "/api/v1/identity/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert legit_refresh_res.status_code == 200
    new_valid_token = legit_refresh_res.json()["refresh_token"]

    # 3. Attacker uses stolen/old `initial_refresh_token` (Replay Attack)
    attacker_res = await async_client.post(
        "/api/v1/identity/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert attacker_res.status_code == 401
    assert "Invalid or expired refresh token" in attacker_res.json()["detail"]

    # 4. Legit user's active session is now also revoked due to replay attack mitigation
    subsequent_legit_res = await async_client.post(
        "/api/v1/identity/auth/refresh",
        json={"refresh_token": new_valid_token},
    )
    assert subsequent_legit_res.status_code == 401
