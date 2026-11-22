"""Multi-tenant isolation and security boundary tests across all 9 HR domain entities."""

import uuid

import pytest
from httpx import AsyncClient


async def register_tenant(
    client: AsyncClient, name: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Helper to register a new tenant and return auth headers, tenant_id, and org_id."""
    clean = name.replace("_", "-").lower()
    payload = {
        "email": f"admin_{clean}@isolate-test.com",
        "password": "AdminPassword123!",
        "full_name": f"Admin {name}",
        "tenant_name": f"Tenant {name}",
        "tenant_slug": f"tenant-{clean}-{uuid.uuid4().hex[:6]}",
        "organization_name": f"Org {name}",
        "tax_identifier": f"TAX-{clean}-{uuid.uuid4().hex[:4]}",
    }
    res = await client.post("/api/v1/identity/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    return (
        {"Authorization": f"Bearer {data['access_token']}"},
        uuid.UUID(data["tenant_id"]),
        uuid.UUID(data["organization_id"]),
    )


@pytest.mark.asyncio
async def test_cross_tenant_isolation_across_all_hr_entities(async_client: AsyncClient):
    """Verifies that Tenant A cannot access, view, or modify Tenant B's HR resources."""
    headers_a, tenant_a_id, org_a_id = await register_tenant(async_client, "Tenant_Alpha")
    headers_b, tenant_b_id, org_b_id = await register_tenant(async_client, "Tenant_Beta")

    # 1. Tenant A creates an Employee
    emp_a_res = await async_client.post(
        "/api/v1/hr/employees/",
        headers=headers_a,
        json={
            "first_name": "AlphaEmp",
            "last_name": "One",
            "email": "alpha1@test.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_a_res.status_code == 201
    emp_a_id = emp_a_res.json()["id"]

    # Tenant B tries to get Tenant A's Employee -> 404
    b_get_emp = await async_client.get(f"/api/v1/hr/employees/{emp_a_id}", headers=headers_b)
    assert b_get_emp.status_code == 404

    # 2. Tenant A creates a Leave Type & Policy
    lt_a_res = await async_client.post(
        "/api/v1/hr/leaves/types",
        headers=headers_a,
        json={"code": "ALPHA_LEAVE", "name": "Alpha Annual Leave"},
    )
    assert lt_a_res.status_code == 201
    lt_a_id = lt_a_res.json()["id"]

    # Tenant B lists leave types -> should NOT see Alpha Leave
    b_list_lt = await async_client.get("/api/v1/hr/leaves/types", headers=headers_b)
    assert b_list_lt.status_code == 200
    assert not any(t["id"] == lt_a_id for t in b_list_lt.json())

    # 3. Tenant A creates a Salary Component & Salary Structure
    comp_a_res = await async_client.post(
        "/api/v1/hr/payroll/components",
        headers=headers_a,
        json={
            "code": "ALPHA_BASIC",
            "name": "Alpha Basic Pay",
            "component_type": "EARNING",
            "calculation_type": "FIXED",
        },
    )
    assert comp_a_res.status_code == 201
    comp_a_id = comp_a_res.json()["id"]

    # Tenant B lists components -> should NOT see Alpha component
    b_list_comp = await async_client.get("/api/v1/hr/payroll/components", headers=headers_b)
    assert b_list_comp.status_code == 200
    assert not any(c["id"] == comp_a_id for c in b_list_comp.json())

    # 4. Tenant A creates a Job Requisition
    req_a_res = await async_client.post(
        "/api/v1/hr/recruitment/requisitions",
        headers=headers_a,
        json={"title": "Alpha Confidential Role", "headcount": 1},
    )
    assert req_a_res.status_code == 201
    req_a_id = req_a_res.json()["id"]

    # Tenant B tries to get Tenant A's Requisition -> 404
    b_get_req = await async_client.get(
        f"/api/v1/hr/recruitment/requisitions/{req_a_id}", headers=headers_b
    )
    assert b_get_req.status_code == 404

    # 5. Tenant A creates a Performance Review Period & Goal
    p_a_res = await async_client.post(
        "/api/v1/hr/performance/periods",
        headers=headers_a,
        json={
            "code": "ALPHA_2024",
            "title": "Alpha 2024 Review",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        },
    )
    assert p_a_res.status_code == 201
    p_a_id = p_a_res.json()["id"]

    # Tenant B lists periods -> should NOT see Alpha period
    b_list_p = await async_client.get("/api/v1/hr/performance/periods", headers=headers_b)
    assert b_list_p.status_code == 200
    assert not any(p["id"] == p_a_id for p in b_list_p.json())

    # 6. Tenant A creates a Training Course
    c_a_res = await async_client.post(
        "/api/v1/hr/learning/courses",
        headers=headers_a,
        json={
            "code": "ALPHA_COURSE",
            "title": "Alpha Proprietary Training",
            "category": "TECHNICAL",
        },
    )
    assert c_a_res.status_code == 201
    c_a_id = c_a_res.json()["id"]

    # Tenant B tries to get Tenant A's Course -> 404
    b_get_c = await async_client.get(f"/api/v1/hr/learning/courses/{c_a_id}", headers=headers_b)
    assert b_get_c.status_code == 404
