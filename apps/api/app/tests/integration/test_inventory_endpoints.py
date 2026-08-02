import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.dependencies import get_current_user, get_db_session
from app.main import app


@pytest.mark.asyncio
async def test_list_inventory_products(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_get_current_user():
        return current_u

    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        response = await client.get("/api/v1/inventory/products")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]


@pytest.mark.asyncio
async def test_inventory_summary_telemetry(
    client: AsyncClient, mock_db_session: MagicMock
):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_get_current_user():
        return current_u

    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        response = await client.get("/api/v1/inventory/products/summary")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert "total_products" in payload["data"]
        assert "total_warehouses" in payload["data"]
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]


@pytest.mark.asyncio
async def test_create_product_validation(
    client: AsyncClient, mock_db_session: MagicMock
):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_get_current_user():
        return current_u

    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        # Missing required category_id and sku
        response = await client.post(
            "/api/v1/inventory/products", json={"name": "Widget Alpha"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]
