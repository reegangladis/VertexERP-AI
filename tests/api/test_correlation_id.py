"""API tests for Correlation ID propagation."""

import pytest
from httpx import AsyncClient

from app.core.constants import HEADER_CORRELATION_ID


@pytest.mark.asyncio
async def test_correlation_id_auto_generated(async_client: AsyncClient):
    """Verifies that requests without X-Correlation-ID receive an auto-generated one."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    assert HEADER_CORRELATION_ID in response.headers
    corr_id = response.headers[HEADER_CORRELATION_ID]
    assert corr_id.startswith("req_")


@pytest.mark.asyncio
async def test_correlation_id_custom_passed(async_client: AsyncClient):
    """Verifies that client-supplied X-Correlation-ID is preserved and echoed back."""
    custom_id = "custom_trace_999888777"
    response = await async_client.get("/health/live", headers={HEADER_CORRELATION_ID: custom_id})
    assert response.status_code == 200
    assert response.headers[HEADER_CORRELATION_ID] == custom_id
