"""API tests for HTTP security headers injection."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_security_headers_present(async_client: AsyncClient):
    """Verifies that security headers are injected into HTTP responses."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("Permissions-Policy", "")
