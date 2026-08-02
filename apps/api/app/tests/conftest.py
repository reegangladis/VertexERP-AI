from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.main import app


# Create a mock database session
@pytest.fixture
def mock_db_session() -> MagicMock:
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.merge = AsyncMock(side_effect=lambda x: x)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest_asyncio.fixture
async def client(mock_db_session: MagicMock) -> AsyncGenerator[AsyncClient]:
    """Provides a test client with overridden dependencies."""

    # Override get_db to return our mock database session
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Clean up overrides
    app.dependency_overrides.clear()
