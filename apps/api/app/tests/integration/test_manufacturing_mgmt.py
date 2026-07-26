import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.core.dependencies import get_current_user, get_db_session


@pytest.mark.asyncio
async def test_get_manufacturing_dashboard(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_user():
        return current_u

    async def override_db():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db_session] = override_db

    try:
        mock_scalar = MagicMock()
        mock_scalar.scalar_one.return_value = 5
        mock_db_session.execute.return_value = mock_scalar

        response = await client.get("/api/v1/manufacturing/dashboard")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["overall_equipment_efficiency_percent"] == 88.5
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_list_boms_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_user():
        return current_u

    async def override_db():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db_session] = override_db

    try:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        response = await client.get("/api/v1/manufacturing/boms")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_list_work_centers_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_user():
        return current_u

    async def override_db():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db_session] = override_db

    try:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        response = await client.get("/api/v1/manufacturing/work-centers")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_list_production_orders_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_user():
        return current_u

    async def override_db():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db_session] = override_db

    try:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        response = await client.get("/api/v1/manufacturing/production-orders")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_execute_mrp_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_user():
        return current_u

    async def override_db():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db_session] = override_db

    try:
        mock_exec = MagicMock()
        mock_exec.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_exec
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        response = await client.post("/api/v1/manufacturing/mrp/runs", json={"run_number": "MRP-INT-001"})
        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["run_number"] == "MRP-INT-001"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db_session, None)
