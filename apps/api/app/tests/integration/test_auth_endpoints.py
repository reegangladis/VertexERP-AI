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
