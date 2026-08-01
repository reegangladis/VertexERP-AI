import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register_password_strength_validation(client: AsyncClient):
    # Password misses special character and digit
    payload = {
        "first_name": "Dave",
        "last_name": "Grohl",
        "username": "davegrohl",
        "email": "dave@grohl.com",
        "password": "JustPassword",
        "org_name": "Foo Fighters",
        "org_slug": "foo-fighters"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "Password must contain at least one digit" in response.text or "Password must contain" in response.text

@pytest.mark.anyio
async def test_login_missing_fields(client: AsyncClient):
    # Missing password
    payload = {
        "email": "user@example.com"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 422
    assert "Email/username and password are required" in response.text

from unittest.mock import MagicMock
from app.main import app
from app.core.dependencies import get_db_session

@pytest.mark.anyio
async def test_refresh_invalid_token(client: AsyncClient, mock_db_session: MagicMock):
    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    try:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        payload = {
            "refresh_token": "invalid.jwt.token"
        }
        response = await client.post("/api/v1/auth/refresh", json=payload)
        assert response.status_code == 401
    finally:
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]
