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
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


async def get_auth_headers_and_org(client: AsyncClient):
    uid = uuid.uuid4().hex[:6]
    user_email = f"org_admin_{uid}@vertexerp.ai"
    username = f"admin_{uid}"
    password = "Password123!"

    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": user_email,
            "password": password,
            "first_name": "Org",
            "last_name": "Admin",
            "organization_name": f"Vertex Corp {uid}",
        },
    )
    assert reg_res.status_code == 201
    user_info = reg_res.json()
    org_id = user_info["organization_id"]

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": password},
    )
    assert login_res.status_code == 200
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers, org_id, user_info["id"]


@pytest.mark.asyncio
async def test_business_units_crud_and_hierarchy():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, _ = await get_auth_headers_and_org(client)

        bu1_res = await client.post(
            "/api/v1/business-units",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "North America BU",
                "code": f"BU_NA_{uuid.uuid4().hex[:4]}",
                "description": "North America Operations Business Unit",
            },
        )
        assert bu1_res.status_code == 201
        bu1 = bu1_res.json()

        bu2_res = await client.post(
            "/api/v1/business-units",
            headers=headers,
            json={
                "organization_id": org_id,
                "parent_business_unit_id": bu1["id"],
                "name": "East Coast Region",
                "code": f"BU_EC_{uuid.uuid4().hex[:4]}",
                "description": "Sub business unit under NA",
            },
        )
        assert bu2_res.status_code == 201
        bu2 = bu2_res.json()

        bu_list = await client.get("/api/v1/business-units", headers=headers)
        assert bu_list.status_code == 200
        assert len(bu_list.json()) >= 2

        bu_tree = await client.get("/api/v1/business-units/tree", headers=headers)
        assert bu_tree.status_code == 200
        assert len(bu_tree.json()) >= 1

        # Cycle prevention
        bu_cycle_res = await client.patch(
            f"/api/v1/business-units/{bu1['id']}",
            headers=headers,
            json={"parent_business_unit_id": bu2["id"]},
        )
        assert bu_cycle_res.status_code == 400
        assert "Circular hierarchy error" in bu_cycle_res.json()["message"]


@pytest.mark.asyncio
async def test_departments_crud_and_hierarchy():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, _ = await get_auth_headers_and_org(client)

        dept1_res = await client.post(
            "/api/v1/departments",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Global Engineering",
                "code": f"DEPT_ENG_{uuid.uuid4().hex[:4]}",
                "description": "Core Product Engineering",
                "email": "engineering@vertexerp.ai",
                "phone": "+1-800-555-0199",
                "budget": 500000.0,
                "cost_center": "CC-ENG-100",
            },
        )
        assert dept1_res.status_code == 201
        dept1 = dept1_res.json()

        dept2_res = await client.post(
            "/api/v1/departments",
            headers=headers,
            json={
                "organization_id": org_id,
                "parent_department_id": dept1["id"],
                "name": "AI & Machine Learning",
                "code": f"DEPT_AI_{uuid.uuid4().hex[:4]}",
                "description": "AI Research Team",
                "budget": 150000.0,
                "cost_center": "CC-AI-200",
            },
        )
        assert dept2_res.status_code == 201
        dept2 = dept2_res.json()

        dept_list = await client.get("/api/v1/departments", headers=headers)
        assert dept_list.status_code == 200
        assert len(dept_list.json()) >= 2

        dept_tree = await client.get("/api/v1/departments/tree", headers=headers)
        assert dept_tree.status_code == 200
        assert len(dept_tree.json()) >= 1

        # Cycle prevention
        dept_cycle = await client.patch(
            f"/api/v1/departments/{dept1['id']}",
            headers=headers,
            json={"parent_department_id": dept2["id"]},
        )
        assert dept_cycle.status_code == 400
        assert "Circular hierarchy error" in dept_cycle.json()["message"]


@pytest.mark.asyncio
async def test_designations():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, _ = await get_auth_headers_and_org(client)

        desig_res = await client.post(
            "/api/v1/designations",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Principal Software Engineer",
                "title": "Principal Architect",
                "code": f"DESIG_PSE_{uuid.uuid4().hex[:4]}",
                "job_level": "L7",
                "grade": "E7",
                "reporting_level": 2,
                "description": "Lead Technical Architect for Enterprise ERP",
            },
        )
        assert desig_res.status_code == 201
        desig = desig_res.json()
        assert desig["job_level"] == "L7"

        desig_list = await client.get("/api/v1/designations", headers=headers)
        assert desig_list.status_code == 200
        assert len(desig_list.json()) >= 1


@pytest.mark.asyncio
async def test_teams_and_members():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)

        team_res = await client.post(
            "/api/v1/teams",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Core Backend Architecture",
                "code": f"TEAM_BACKEND_{uuid.uuid4().hex[:4]}",
                "description": "High Performance Microservices Team",
                "team_type": "Cross-Functional",
            },
        )
        assert team_res.status_code == 201
        team = team_res.json()

        member_res = await client.post(
            "/api/v1/team-members",
            headers=headers,
            json={
                "team_id": team["id"],
                "user_id": user_id,
                "role": "Team Lead",
            },
        )
        assert member_res.status_code == 201
        member = member_res.json()

        # Duplicate team member check
        dup_member = await client.post(
            "/api/v1/team-members",
            headers=headers,
            json={
                "team_id": team["id"],
                "user_id": user_id,
                "role": "Senior Engineer",
            },
        )
        assert dup_member.status_code == 400
        assert "already a member" in dup_member.json()["message"]

        members_list = await client.get(
            f"/api/v1/team-members?team_id={team['id']}", headers=headers
        )
        assert members_list.status_code == 200
        assert len(members_list.json()) >= 1

        del_member = await client.delete(
            f"/api/v1/team-members/{member['id']}", headers=headers
        )
        assert del_member.status_code == 200
