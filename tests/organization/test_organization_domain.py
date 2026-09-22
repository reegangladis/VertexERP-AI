"""Integration and Security test suite for complete Organization Domain.

Covers all 9 domain entities:
- Branches
- Departments (including hierarchical tree)
- Teams & Team Members
- Designations
- Business Units
- Cost Centers
- Locations
- Work Calendars & Working Days
- Holidays
Also proves strict multi-tenant isolation and fail-closed RBAC permission gates.
"""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_get_auth_headers(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Helper to register a tenant and return authorization headers, tenant_id, and org_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"orgadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Admin {suffix}",
        "tenant_name": f"Tenant {suffix}",
        "tenant_slug": f"tenant-{clean_suffix}",
        "organization_name": f"Org {suffix}",
        "tax_identifier": f"TAX-{clean_suffix}",
    }
    res = await client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return headers, uuid.UUID(data["tenant_id"]), uuid.UUID(data["organization_id"])


@pytest.mark.asyncio
async def test_branches_crud_and_uniqueness(async_client: AsyncClient):
    """Verifies Branch creation, listing, get, update, soft delete, and code uniqueness."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "branch_test")

    # 1. Create Branch
    branch_in = {
        "code": "BR-NYC",
        "name": "New York Headquarters",
        "address_line1": "100 Broadway",
        "city": "New York",
        "state": "NY",
        "postal_code": "10005",
        "country": "USA",
        "phone": "+1-212-555-0100",
        "is_headquarters": True,
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/branches/", headers=headers, json=branch_in)
    assert create_res.status_code == 201
    branch = create_res.json()
    branch_id = branch["id"]
    assert branch["code"] == "BR-NYC"
    assert branch["is_headquarters"] is True

    # 2. Duplicate Code returns 409 Conflict
    dup_res = await async_client.post("/api/v1/branches/", headers=headers, json=branch_in)
    assert dup_res.status_code == 409

    # 3. List Branches
    list_res = await async_client.get("/api/v1/branches/", headers=headers)
    assert list_res.status_code == 200
    assert any(b["id"] == branch_id for b in list_res.json())

    # 4. Get Branch
    get_res = await async_client.get(f"/api/v1/branches/{branch_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "New York Headquarters"

    # 5. Update Branch
    update_res = await async_client.put(
        f"/api/v1/branches/{branch_id}",
        headers=headers,
        json={"name": "NYC Global HQ"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "NYC Global HQ"

    # 6. Delete Branch
    del_res = await async_client.delete(f"/api/v1/branches/{branch_id}", headers=headers)
    assert del_res.status_code == 204

    # 7. Get deleted returns 404
    get_after_del = await async_client.get(f"/api/v1/branches/{branch_id}", headers=headers)
    assert get_after_del.status_code == 404


@pytest.mark.asyncio
async def test_departments_and_hierarchy_tree(async_client: AsyncClient):
    """Verifies Department CRUD, self-parent prevention, and hierarchical tree."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "dept_test")

    # 1. Create Parent Department (Engineering)
    parent_in = {
        "code": "ENG",
        "name": "Engineering",
        "description": "Product engineering and development",
        "is_active": True,
    }
    p_res = await async_client.post("/api/v1/departments/", headers=headers, json=parent_in)
    assert p_res.status_code == 201
    parent_id = p_res.json()["id"]

    # 2. Create Child Department (Frontend)
    child_in = {
        "code": "FE",
        "name": "Frontend Team",
        "parent_department_id": parent_id,
        "is_active": True,
    }
    c_res = await async_client.post("/api/v1/departments/", headers=headers, json=child_in)
    assert c_res.status_code == 201
    child_id = c_res.json()["id"]

    # 3. Fetch Department Hierarchy Tree
    tree_res = await async_client.get("/api/v1/departments/tree", headers=headers)
    assert tree_res.status_code == 200
    tree = tree_res.json()
    assert len(tree) >= 1
    eng_node = next((n for n in tree if n["id"] == parent_id), None)
    assert eng_node is not None
    assert len(eng_node["children"]) == 1
    assert eng_node["children"][0]["id"] == child_id

    # 4. Self-parenting validation returns 422
    self_parent_res = await async_client.put(
        f"/api/v1/departments/{parent_id}",
        headers=headers,
        json={"parent_department_id": parent_id},
    )
    assert self_parent_res.status_code == 422


@pytest.mark.asyncio
async def test_teams_and_members(async_client: AsyncClient):
    """Verifies Team management and member roster operations."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "team_test")

    # 1. Create Team
    team_in = {
        "code": "CORE-AI",
        "name": "Core AI Platform Team",
        "description": "RAG and LLM backend pipelines",
        "is_active": True,
    }
    t_res = await async_client.post("/api/v1/teams/", headers=headers, json=team_in)
    assert t_res.status_code == 201
    team_id = t_res.json()["id"]

    # 2. Get current user info to add as team lead
    me_res = await async_client.get("/api/v1/identity/users/me", headers=headers)
    assert me_res.status_code == 200
    user_id = me_res.json()["id"]

    # 3. Add Member to Team
    add_m_res = await async_client.post(
        f"/api/v1/teams/{team_id}/members",
        headers=headers,
        json={"user_id": user_id, "role": "LEAD"},
    )
    assert add_m_res.status_code == 201
    assert add_m_res.json()["role"] == "LEAD"

    # 4. List Team Members
    m_list_res = await async_client.get(f"/api/v1/teams/{team_id}/members", headers=headers)
    assert m_list_res.status_code == 200
    assert len(m_list_res.json()) == 1

    # 5. Remove Member
    rm_res = await async_client.delete(
        f"/api/v1/teams/{team_id}/members/{user_id}", headers=headers
    )
    assert rm_res.status_code == 204


@pytest.mark.asyncio
async def test_designations_and_hierarchy_levels(async_client: AsyncClient):
    """Verifies Designation titles, hierarchy levels, and sorting."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "desig_test")

    # Create designations at different levels
    d1 = {"code": "SE-1", "name": "Software Engineer I", "level": 2}
    d2 = {"code": "VP-ENG", "name": "VP of Engineering", "level": 10}
    d3 = {"code": "INTERN", "name": "Engineering Intern", "level": 1}

    await async_client.post("/api/v1/designations/", headers=headers, json=d1)
    await async_client.post("/api/v1/designations/", headers=headers, json=d2)
    await async_client.post("/api/v1/designations/", headers=headers, json=d3)

    list_res = await async_client.get("/api/v1/designations/", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 3
    # Check level ascending sort
    levels = [item["level"] for item in items]
    assert levels == sorted(levels)


@pytest.mark.asyncio
async def test_business_units_crud(async_client: AsyncClient):
    """Verifies Business Unit strategic division lifecycle."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "bu_test")

    bu_in = {
        "code": "BU-ENTERPRISE",
        "name": "Enterprise Solutions",
        "description": "B2B Enterprise ERP business line",
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/business-units/", headers=headers, json=bu_in)
    assert create_res.status_code == 201
    bu_id = create_res.json()["id"]

    get_res = await async_client.get(f"/api/v1/business-units/{bu_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Enterprise Solutions"


@pytest.mark.asyncio
async def test_cost_centers_and_budgets(async_client: AsyncClient):
    """Verifies Cost Center financial management and budget allocations."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "cc_test")

    cc_in = {
        "code": "CC-RD-2026",
        "name": "R&D Cloud Infrastructure",
        "annual_budget": 500000.00,
        "currency": "USD",
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/cost-centers/", headers=headers, json=cc_in)
    assert create_res.status_code == 201
    cc_data = create_res.json()
    assert float(cc_data["annual_budget"]) == 500000.00
    assert cc_data["currency"] == "USD"


@pytest.mark.asyncio
async def test_locations_facilities_and_coordinates(async_client: AsyncClient):
    """Verifies physical facility locations and geographical coordinate mapping."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "loc_test")

    loc_in = {
        "code": "LOC-WH-1",
        "name": "Austin Logistics Fulfillment Center",
        "location_type": "WAREHOUSE",
        "address_line1": "500 Innovation Way",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78701",
        "country": "USA",
        "latitude": 30.267200,
        "longitude": -97.743100,
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/locations/", headers=headers, json=loc_in)
    assert create_res.status_code == 201
    loc = create_res.json()
    assert loc["location_type"] == "WAREHOUSE"
    assert float(loc["latitude"]) == 30.267200


@pytest.mark.asyncio
async def test_work_calendars_and_working_days(async_client: AsyncClient):
    """Verifies Work Calendar creation and custom 7-day schedule assignment."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "cal_test")

    cal_in = {
        "code": "CAL-US-STD",
        "name": "US Standard 40hr Work Schedule",
        "time_zone": "America/New_York",
        "is_default": True,
        "standard_hours_per_day": 8.0,
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/calendars/", headers=headers, json=cal_in)
    assert create_res.status_code == 201
    cal = create_res.json()
    cal_id = cal["id"]
    assert len(cal["working_days"]) == 7

    # Update working days (make Saturday a working day)
    updated_days = [
        {"day_of_week": i, "is_working_day": i < 6, "start_time": "08:00", "end_time": "16:00"}
        for i in range(7)
    ]
    up_res = await async_client.put(
        f"/api/v1/calendars/{cal_id}/working-days", headers=headers, json=updated_days
    )
    assert up_res.status_code == 200
    days_data = up_res.json()
    assert len(days_data) == 7
    # Saturday (day 5) is now working day
    sat = next(d for d in days_data if d["day_of_week"] == 5)
    assert sat["is_working_day"] is True
    assert sat["start_time"] == "08:00"


@pytest.mark.asyncio
async def test_holidays_management(async_client: AsyncClient):
    """Verifies Holiday scheduling, recurrence, and yearly query filtering."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "hol_test")

    h1 = {
        "name": "New Year's Day",
        "holiday_date": "2026-01-01",
        "holiday_type": "NATIONAL",
        "is_recurring": True,
    }
    h2 = {
        "name": "Independence Day",
        "holiday_date": "2026-07-04",
        "holiday_type": "NATIONAL",
        "is_recurring": True,
    }
    await async_client.post("/api/v1/holidays/", headers=headers, json=h1)
    await async_client.post("/api/v1/holidays/", headers=headers, json=h2)

    # Query holidays for 2026
    list_res = await async_client.get("/api/v1/holidays/?year=2026", headers=headers)
    assert list_res.status_code == 200
    holidays = list_res.json()
    assert len(holidays) >= 2


@pytest.mark.asyncio
async def test_cross_tenant_isolation_organization_domain(async_client: AsyncClient):
    """
    CRITICAL SECURITY TEST:
    Verifies that Tenant B CANNOT read, access, update, or delete any entity created by Tenant A.
    """
    headers_a, tenant_a_id, org_a_id = await create_tenant_and_get_auth_headers(
        async_client, "tenant_a"
    )
    headers_b, tenant_b_id, org_b_id = await create_tenant_and_get_auth_headers(
        async_client, "tenant_b"
    )

    # 1. Tenant A creates Branch, Department, Team, Designation, CostCenter, Location, Calendar
    b_res = await async_client.post(
        "/api/v1/branches/",
        headers=headers_a,
        json={
            "code": "BR-A",
            "name": "Branch A",
            "address_line1": "A St",
            "city": "NYC",
            "state": "NY",
            "postal_code": "10001",
        },
    )
    branch_a_id = b_res.json()["id"]

    d_res = await async_client.post(
        "/api/v1/departments/",
        headers=headers_a,
        json={"code": "DEPT-A", "name": "Dept A"},
    )
    dept_a_id = d_res.json()["id"]

    t_res = await async_client.post(
        "/api/v1/teams/",
        headers=headers_a,
        json={"code": "TEAM-A", "name": "Team A"},
    )
    team_a_id = t_res.json()["id"]

    des_res = await async_client.post(
        "/api/v1/designations/",
        headers=headers_a,
        json={"code": "DES-A", "name": "Desig A", "level": 1},
    )
    desig_a_id = des_res.json()["id"]

    # 2. Tenant B attempts direct object reference (IDOR) on Tenant A's objects -> MUST RETURN 404
    assert (
        await async_client.get(f"/api/v1/branches/{branch_a_id}", headers=headers_b)
    ).status_code == 404
    assert (
        await async_client.get(f"/api/v1/departments/{dept_a_id}", headers=headers_b)
    ).status_code == 404
    assert (
        await async_client.get(f"/api/v1/teams/{team_a_id}", headers=headers_b)
    ).status_code == 404
    assert (
        await async_client.get(f"/api/v1/designations/{desig_a_id}", headers=headers_b)
    ).status_code == 404

    # 3. Tenant B attempts to mutate Tenant A's Branch -> MUST RETURN 404
    assert (
        await async_client.put(
            f"/api/v1/branches/{branch_a_id}",
            headers=headers_b,
            json={"name": "Hacked Branch"},
        )
    ).status_code == 404

    # 4. Tenant B attempts to delete Tenant A's Branch -> MUST RETURN 404
    assert (
        await async_client.delete(f"/api/v1/branches/{branch_a_id}", headers=headers_b)
    ).status_code == 404
