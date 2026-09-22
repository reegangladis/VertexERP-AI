"""Integration and Security tests for HR Employee Domain (Feature 1)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_get_auth_headers(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Helper to register a tenant and return authorization headers, tenant_id, and org_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"hradmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"HR Admin {suffix}",
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
async def test_employee_crud_and_auto_numbering(async_client: AsyncClient):
    """Verifies Employee creation, auto employee numbering, update, retrieval, and soft delete."""
    headers, _, _ = await create_tenant_and_get_auth_headers(async_client, "emp_crud")

    # 1. Create Department & Designation first
    dept_res = await async_client.post(
        "/api/v1/departments/",
        headers=headers,
        json={"code": "ENG", "name": "Engineering", "is_active": True},
    )
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["id"]

    desig_res = await async_client.post(
        "/api/v1/designations/",
        headers=headers,
        json={"code": "SWE", "name": "Software Engineer", "level": 3, "is_active": True},
    )
    assert desig_res.status_code == 201

    desig_id = desig_res.json()["id"]

    # 2. Create Employee without manual employee_number (auto-generation test)
    emp_payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "phone": "+1-555-0199",
        "date_of_birth": "1992-05-15",
        "gender": "FEMALE",
        "hire_date": "2024-01-10",
        "employment_status": "ACTIVE",
        "department_id": dept_id,
        "designation_id": desig_id,
        "is_active": True,
    }
    create_res = await async_client.post("/api/v1/hr/employees/", headers=headers, json=emp_payload)
    assert create_res.status_code == 201
    emp = create_res.json()
    emp_id = emp["id"]
    assert emp["employee_number"] == "EMP-0001"
    assert emp["first_name"] == "Alice"
    assert emp["last_name"] == "Smith"
    assert emp["email"] == "alice.smith@example.com"
    assert emp["employment_status"] == "ACTIVE"

    # 3. Create Second Employee to test manager hierarchy and auto-number increment
    emp2_payload = {
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob.jones@example.com",
        "phone": "+1-555-0200",
        "hire_date": "2024-02-01",
        "employment_status": "PROBATION",
        "department_id": dept_id,
        "designation_id": desig_id,
        "reporting_manager_id": emp_id,
    }
    create_res2 = await async_client.post(
        "/api/v1/hr/employees/", headers=headers, json=emp2_payload
    )
    assert create_res2.status_code == 201
    emp2 = create_res2.json()
    assert emp2["employee_number"] == "EMP-0002"
    assert emp2["reporting_manager_id"] == emp_id

    # 4. Duplicate email returns 409 Conflict
    dup_res = await async_client.post("/api/v1/hr/employees/", headers=headers, json=emp_payload)
    assert dup_res.status_code == 409

    # 5. List Employees with filters & search
    list_res = await async_client.get(
        f"/api/v1/hr/employees/?department_id={dept_id}", headers=headers
    )
    assert list_res.status_code == 200
    employees = list_res.json()
    assert len(employees) == 2

    search_res = await async_client.get("/api/v1/hr/employees/?search=Alice", headers=headers)
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["first_name"] == "Alice"

    # 6. Update Employee
    update_payload = {"phone": "+1-555-9999", "employment_status": "CONFIRMED"}
    update_res = await async_client.put(
        f"/api/v1/hr/employees/{emp_id}", headers=headers, json=update_payload
    )
    assert update_res.status_code == 200
    assert update_res.json()["phone"] == "+1-555-9999"

    # 7. Self-reporting manager validation fails
    invalid_mgr_res = await async_client.put(
        f"/api/v1/hr/employees/{emp_id}",
        headers=headers,
        json={"reporting_manager_id": emp_id},
    )
    assert invalid_mgr_res.status_code == 422

    # 8. Soft Delete Employee
    del_res = await async_client.delete(f"/api/v1/hr/employees/{emp2['id']}", headers=headers)
    assert del_res.status_code == 204

    # 9. Get Deleted Employee returns 404
    get_del_res = await async_client.get(f"/api/v1/hr/employees/{emp2['id']}", headers=headers)
    assert get_del_res.status_code == 404


@pytest.mark.asyncio
async def test_cross_tenant_isolation_employees(async_client: AsyncClient):
    """Verifies that employees are strictly isolated across tenants."""
    headers_a, _, _ = await create_tenant_and_get_auth_headers(async_client, "emp_iso_a")
    headers_b, _, _ = await create_tenant_and_get_auth_headers(async_client, "emp_iso_b")

    # Create Employee in Tenant A
    emp_a_res = await async_client.post(
        "/api/v1/hr/employees/",
        headers=headers_a,
        json={
            "first_name": "TenantA",
            "last_name": "Worker",
            "email": "worker@tenanta.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_a_res.status_code == 201
    emp_a_id = emp_a_res.json()["id"]

    # Tenant B tries to GET Tenant A's employee -> Returns 404 Not Found
    get_res = await async_client.get(f"/api/v1/hr/employees/{emp_a_id}", headers=headers_b)
    assert get_res.status_code == 404

    # Tenant B lists employees -> Does not see Tenant A's employee
    list_res = await async_client.get("/api/v1/hr/employees/", headers=headers_b)
    assert list_res.status_code == 200
    assert not any(e["id"] == emp_a_id for e in list_res.json())
