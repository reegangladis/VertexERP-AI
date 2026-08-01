import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from httpx import AsyncClient
import uuid
from app.main import app
from app.core.dependencies import get_current_user, get_db_session

@pytest.mark.asyncio
async def test_list_branches(client: AsyncClient, mock_db_session: MagicMock):
    # Setup test mock user
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
        # Mock database response to return an empty list or scalar list
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        response = await client.get("/api/v1/branches")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        # Clean up dependency overrides
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]

@pytest.mark.asyncio
async def test_create_branch_validation(client: AsyncClient, mock_db_session: MagicMock):
    # Setup test mock user
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
        # Test validator with missing required properties
        payload = {
            "slug": "invalid"
        }
        response = await client.post("/api/v1/branches", json=payload)
        assert response.status_code == 422
    finally:
        # Clean up dependency overrides
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]

@pytest.mark.asyncio
async def test_list_business_units(client: AsyncClient, mock_db_session: MagicMock):
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
        
        response = await client.get("/api/v1/business-units")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]

