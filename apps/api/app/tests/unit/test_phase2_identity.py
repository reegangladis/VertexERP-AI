import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.database.base import Base
from app.database.connection import set_fallback_sqlite_engine
from app.main import app


@pytest.fixture(autouse=True, scope="module")
async def setup_test_db():
    set_fallback_sqlite_engine()
    from app.database.connection import engine as test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_auth_registration_and_login():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        uid = uuid.uuid4().hex[:6]
        username = f"user_{uid}"
        email = f"user_{uid}@vertexerp.ai"

        # Register user
        reg_payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        reg_data = res_reg.json()
        assert reg_data["email"] == email

        # Login user
        login_payload = {
            "username_or_email": email,
            "password": "SecurePassword123!",
        }
        res_login = await client.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        token_data = res_login.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]

        # Fetch current user profile (/auth/me)
        headers = {"Authorization": f"Bearer {access_token}"}
        res_me = await client.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["username"] == username

        # Test Refresh Token Rotation
        res_ref = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res_ref.status_code == 200
        new_token_data = res_ref.json()
        assert "access_token" in new_token_data
        assert new_token_data["refresh_token"] != refresh_token

        # Test Active Sessions List
        new_headers = {"Authorization": f"Bearer {new_token_data['access_token']}"}
        res_sessions = await client.get("/api/v1/sessions", headers=new_headers)
        assert res_sessions.status_code == 200
        sessions_list = res_sessions.json()
        assert len(sessions_list) >= 1

        # Test Forgot Password Token Generation
        res_forgot = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        assert res_forgot.status_code == 200
        forgot_data = res_forgot.json()
        assert "token" in forgot_data

        # Test Reset Password
        reset_token = forgot_data["token"]
        res_reset = await client.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": "NewSecurePassword123!",
        })
        assert res_reset.status_code == 200

        # Test MFA Secret Generation
        res_mfa_sec = await client.post("/api/v1/mfa/generate-secret", headers=new_headers)
        assert res_mfa_sec.status_code == 200
        mfa_info = res_mfa_sec.json()
        assert "totp_secret" in mfa_info
        assert "qr_code_url" in mfa_info
