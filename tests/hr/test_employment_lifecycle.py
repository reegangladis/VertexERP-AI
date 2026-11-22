"""Integration and Security tests for Employment Lifecycle & Contracts (Feature 3)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"lifeadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Lifecycle Admin {suffix}",
        "tenant_name": f"Tenant {suffix}",
        "tenant_slug": f"tenant-{clean_suffix}",
        "organization_name": f"Org {suffix}",
        "tax_identifier": f"TAX-{clean_suffix}",
    }
    res = await client.post("/api/v1/identity/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    tenant_id = uuid.UUID(data["tenant_id"])
    org_id = uuid.UUID(data["organization_id"])

    # Create employee
    emp_res = await client.post(
        "/api/v1/hr/employees/",
        headers=headers,
        json={
            "first_name": "Marcus",
            "last_name": "Vance",
            "email": f"marcus.vance.{clean_suffix}@example.com",
            "hire_date": "2024-03-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_employment_contracts_lifecycle(async_client: AsyncClient):
    """Verifies contract creation, duplicate rejection, and updates."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "cntr_test")

    # 1. Create Contract
    contract_in = {
        "employee_id": str(emp_id),
        "contract_number": "CNT-2024-001",
        "contract_type": "PERMANENT",
        "start_date": "2024-03-01",
        "probation_end_date": "2024-06-01",
        "notice_period_days": 60,
        "base_salary": 95000.00,
        "currency": "USD",
        "status": "ACTIVE",
    }
    res = await async_client.post(
        "/api/v1/hr/lifecycle/contracts", headers=headers, json=contract_in
    )
    assert res.status_code == 201
    contract = res.json()
    contract_id = contract["id"]
    assert contract["contract_number"] == "CNT-2024-001"
    assert contract["base_salary"] == 95000.00

    # 2. Duplicate contract number returns 409 Conflict
    dup_res = await async_client.post(
        "/api/v1/hr/lifecycle/contracts", headers=headers, json=contract_in
    )
    assert dup_res.status_code == 409

    # 3. List contracts for employee
    list_res = await async_client.get(
        f"/api/v1/hr/lifecycle/contracts/employee/{emp_id}", headers=headers
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 4. Update contract
    put_res = await async_client.put(
        f"/api/v1/hr/lifecycle/contracts/{contract_id}",
        headers=headers,
        json={"base_salary": 105000.00, "status": "ACTIVE"},
    )
    assert put_res.status_code == 200
    assert put_res.json()["base_salary"] == 105000.00


@pytest.mark.asyncio
async def test_lifecycle_events_and_onboarding_tasks(async_client: AsyncClient):
    """Verifies immutable lifecycle event history and onboarding task checklist."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "life_event_test")

    # 1. Record Lifecycle Event (Promotion)
    event_in = {
        "employee_id": str(emp_id),
        "event_type": "PROMOTED",
        "effective_date": "2024-09-01",
        "previous_value_json": {"title": "Junior Engineer", "grade": "L3"},
        "new_value_json": {"title": "Senior Engineer", "grade": "L4"},
        "remarks": "Promoted following stellar annual review.",
    }
    event_res = await async_client.post(
        "/api/v1/hr/lifecycle/events", headers=headers, json=event_in
    )
    assert event_res.status_code == 201
    event = event_res.json()
    assert event["event_type"] == "PROMOTED"

    # 2. List Lifecycle Events
    list_e_res = await async_client.get(
        f"/api/v1/hr/lifecycle/events/employee/{emp_id}", headers=headers
    )
    assert list_e_res.status_code == 200
    assert len(list_e_res.json()) == 1

    # 3. Create Onboarding Task
    task_in = {
        "employee_id": str(emp_id),
        "title": "Configure Laptop & VPN Access",
        "description": "Issue MacBook Pro and setup company VPN profiles",
        "category": "IT_SETUP",
        "due_date": "2024-03-05",
    }
    task_res = await async_client.post(
        "/api/v1/hr/lifecycle/onboarding/tasks", headers=headers, json=task_in
    )
    assert task_res.status_code == 201
    task = task_res.json()
    task_id = task["id"]
    assert task["status"] == "PENDING"

    # 4. List Tasks
    list_t_res = await async_client.get(
        f"/api/v1/hr/lifecycle/onboarding/tasks/employee/{emp_id}", headers=headers
    )
    assert list_t_res.status_code == 200
    assert len(list_t_res.json()) == 1

    # 5. Mark Task Completed
    update_t_res = await async_client.put(
        f"/api/v1/hr/lifecycle/onboarding/tasks/{task_id}",
        headers=headers,
        json={"status": "COMPLETED"},
    )
    assert update_t_res.status_code == 200
    assert update_t_res.json()["status"] == "COMPLETED"
    assert update_t_res.json()["completed_at"] is not None
