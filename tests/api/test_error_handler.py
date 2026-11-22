"""API tests for RFC 7807 Problem Details error handling."""

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.core.constants import HEADER_CORRELATION_ID, MEDIA_TYPE_PROBLEM_JSON
from app.core.exceptions import ConflictException, NotFoundException
from app.main import create_app

# Create a router with endpoints that raise specific exceptions
custom_error_router = APIRouter(prefix="/test-errors")


@custom_error_router.get("/not-found")
async def trigger_not_found():
    raise NotFoundException("Customer account with specified ID was not found.")


@custom_error_router.get("/conflict")
async def trigger_conflict():
    raise ConflictException("Product SKU already exists in warehouse.")


@custom_error_router.get("/uncaught")
async def trigger_uncaught():
    raise RuntimeError("Unexpected simulated hardware failure!")


@pytest.fixture
def app_with_error_routes():
    app = create_app()
    app.include_router(custom_error_router)
    return app


@pytest.fixture
async def error_client(app_with_error_routes):
    transport = ASGITransport(app=app_with_error_routes)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_rfc7807_not_found_error(error_client: AsyncClient):
    """Verifies RFC 7807 problem details structure on 404."""
    response = await error_client.get("/test-errors/not-found")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith(MEDIA_TYPE_PROBLEM_JSON)
    assert HEADER_CORRELATION_ID in response.headers

    data = response.json()
    assert data["type"] == "https://api.vertexerp.io/errors/not-found"
    assert data["title"] == "Resource Not Found"
    assert data["status"] == 404
    assert data["detail"] == "Customer account with specified ID was not found."
    assert data["instance"] == "/test-errors/not-found"
    assert "correlation_id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_rfc7807_conflict_error(error_client: AsyncClient):
    """Verifies RFC 7807 problem details structure on 409."""
    response = await error_client.get("/test-errors/conflict")
    assert response.status_code == 409
    assert response.headers["content-type"].startswith(MEDIA_TYPE_PROBLEM_JSON)

    data = response.json()
    assert data["type"] == "https://api.vertexerp.io/errors/conflict"
    assert data["status"] == 409


@pytest.mark.asyncio
async def test_rfc7807_uncaught_server_error(error_client: AsyncClient):
    """Verifies RFC 7807 problem details structure on 500 without leaking stack traces."""
    response = await error_client.get("/test-errors/uncaught")
    assert response.status_code == 500
    assert response.headers["content-type"].startswith(MEDIA_TYPE_PROBLEM_JSON)

    data = response.json()
    assert data["type"] == "https://api.vertexerp.io/errors/internal-server-error"
    assert data["title"] == "Internal Server Error"
    assert data["status"] == 500
    assert "Unexpected simulated hardware failure" not in data["detail"]
    assert "correlation_id" in data
