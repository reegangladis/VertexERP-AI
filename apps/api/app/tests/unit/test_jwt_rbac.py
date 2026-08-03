import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.database.base import Base
from app.database.connection import set_fallback_sqlite_engine
from app.main import app


@pytest.fixture(autouse=True, scope="module")
async def setup_test_db():
    set_fallback_sqlite_engine()
    from app.database.connection import engine as test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_jwt_and_rbac_permissions():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test unauthorized request (missing token)
        res = await client.get("/api/v1/users")
        assert res.status_code == 401

        # Test invalid token format
        res_invalid = await client.get("/api/v1/users", headers={"Authorization": "Bearer invalidtoken123"})
        assert res_invalid.status_code == 401
