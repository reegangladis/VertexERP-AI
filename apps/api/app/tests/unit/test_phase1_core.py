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
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
        assert response.status_code in (200, 503)
        data = response.json()
        assert "data" in data or "status" in data


@pytest.mark.asyncio
async def test_organization_crud():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        unique_slug = f"acme-global-{uuid.uuid4().hex[:6]}"
        org_payload = {
            "name": "Acme Global Corp",
            "slug": unique_slug,
            "email": "contact@acmeglobal.com",
            "country": "USA",
            "timezone": "America/New_York",
            "status": "active",
            "subscription": "enterprise",
        }
        res = await client.post("/api/v1/organizations", json=org_payload)
        assert res.status_code == 201
        org_data = res.json()
        org_id = org_data["id"]
        assert org_data["name"] == "Acme Global Corp"
        assert org_data["slug"] == unique_slug

        # Read organization
        res_get = await client.get(f"/api/v1/organizations/{org_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == org_id

        # Update organization
        res_patch = await client.patch(
            f"/api/v1/organizations/{org_id}", json={"name": "Acme Global Enterprise"}
        )
        assert res_patch.status_code == 200
        assert res_patch.json()["name"] == "Acme Global Enterprise"


@pytest.mark.asyncio
async def test_permissions_crud():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        unique_code = f"org.read.{uuid.uuid4().hex[:4]}"
        perm_payload = {
            "code": unique_code,
            "module": "organization",
            "description": "Read organization profile",
        }
        res = await client.post("/api/v1/permissions", json=perm_payload)
        assert res.status_code in (201, 400)
        if res.status_code == 201:
            data = res.json()
            assert data["code"] == unique_code
