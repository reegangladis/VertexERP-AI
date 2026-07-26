import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from httpx import AsyncClient
import uuid
from app.main import app
from app.core.dependencies import get_current_user, get_db_session

@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, mock_db_session: MagicMock):
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
async def test_create_product_validation(client: AsyncClient, mock_db_session: MagicMock):
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
        # Invalid payload: missing sku, category_id, unit_id
        payload = {
            "name": "Invalid Test SKU"
        }
        response = await client.post("/api/v1/inventory/products", json=payload)
        assert response.status_code == 422
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]

@pytest.mark.asyncio
async def test_stock_transfer_processing(client: AsyncClient, mock_db_session: MagicMock):
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
        # Mock stock transfer database levels
        mock_stock = MagicMock()
        mock_stock.available = 100
        mock_stock.on_hand = 100

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_stock
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        payload = {
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(uuid.uuid4()),
            "from_bin_id": str(uuid.uuid4()),
            "to_bin_id": str(uuid.uuid4()),
            "quantity": 10
        }
        response = await client.post("/api/v1/inventory/transfers", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]
