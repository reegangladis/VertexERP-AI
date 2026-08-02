import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.dependencies import get_current_user, get_db_session
from app.main import app


@pytest.mark.asyncio
async def test_list_leads(client: AsyncClient, mock_db_session: MagicMock):
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

        response = await client.get("/api/v1/crm/leads")
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
async def test_create_lead_validation(client: AsyncClient, mock_db_session: MagicMock):
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
        # Check invalid payload missing required fields like first_name, last_name and email
        payload = {"status": "new"}
        response = await client.post("/api/v1/crm/leads", json=payload)
        assert response.status_code == 422
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]


@pytest.mark.asyncio
async def test_close_deal_result(client: AsyncClient, mock_db_session: MagicMock):
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
        # Mock deal lookup
        mock_deal = MagicMock()
        mock_deal.id = uuid.uuid4()
        mock_deal.status = "pipeline"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_deal
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        payload = {"status": "won", "won_lost_reason": "Price agreed."}
        response = await client.put(
            f"/api/v1/crm/deals/{uuid.uuid4()}/result", json=payload
        )
        assert response.status_code == status.HTTP_200_OK
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]
