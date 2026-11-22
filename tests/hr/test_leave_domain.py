"""Integration and Security tests for Leave Management Domain (Feature 5)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"leaveadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Leave Admin {suffix}",
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
            "first_name": "Sarah",
            "last_name": "Connor",
            "email": f"sarah.connor.{clean_suffix}@example.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_leave_type_and_policy_setup(async_client: AsyncClient):
    """Verifies Leave Type and Policy creation and listing."""
    headers, _, _, _ = await create_tenant_and_employee(async_client, "type_policy")

    # 1. Create Leave Type
    type_in = {
        "code": "ANNUAL",
        "name": "Annual Paid Leave",
        "is_paid": True,
        "color_code": "#3B82F6",
    }
    res = await async_client.post("/api/v1/hr/leaves/types", headers=headers, json=type_in)
    assert res.status_code == 201
    leave_type = res.json()
    type_id = leave_type["id"]
    assert leave_type["code"] == "ANNUAL"

    # Duplicate Type code returns 409
    dup_res = await async_client.post("/api/v1/hr/leaves/types", headers=headers, json=type_in)
    assert dup_res.status_code == 409

    # 2. List Leave Types
    list_res = await async_client.get("/api/v1/hr/leaves/types", headers=headers)
    assert list_res.status_code == 200
    assert any(t["id"] == type_id for t in list_res.json())

    # 3. Create Leave Policy
    policy_in = {
        "leave_type_id": type_id,
        "accrual_frequency": "ANNUAL",
        "annual_allocation_days": 20.0,
        "carry_forward_max_days": 5.0,
    }
    policy_res = await async_client.post(
        "/api/v1/hr/leaves/policies", headers=headers, json=policy_in
    )
    assert policy_res.status_code == 201
    policy = policy_res.json()
    assert policy["annual_allocation_days"] == 20.0


@pytest.mark.asyncio
async def test_leave_request_and_approval_flow(async_client: AsyncClient):
    """Verifies Leave Request application, balance deduction, and approval lifecycle."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "leave_flow")

    # 1. Setup Leave Type & Policy
    type_in = {
        "code": "SICK",
        "name": "Sick Leave",
        "is_paid": True,
        "color_code": "#EF4444",
    }
    res = await async_client.post("/api/v1/hr/leaves/types", headers=headers, json=type_in)
    assert res.status_code == 201
    type_id = res.json()["id"]

    policy_in = {
        "leave_type_id": type_id,
        "accrual_frequency": "ANNUAL",
        "annual_allocation_days": 10.0,
    }
    await async_client.post("/api/v1/hr/leaves/policies", headers=headers, json=policy_in)

    # 2. Apply for Leave
    req_in = {
        "employee_id": str(emp_id),
        "leave_type_id": type_id,
        "start_date": "2024-06-10",
        "end_date": "2024-06-12",
        "total_days": 3.0,
        "reason": "Flu recovery",
    }
    apply_res = await async_client.post("/api/v1/hr/leaves/requests", headers=headers, json=req_in)
    assert apply_res.status_code == 201
    req_data = apply_res.json()
    request_id = req_data["id"]
    assert req_data["status"] == "SUBMITTED"
    assert req_data["total_days"] == 3.0

    # 3. Check Leave Balances (should reflect 3 pending days out of 10 total allocated)
    bal_res = await async_client.get(
        f"/api/v1/hr/leaves/balances/{emp_id}?fiscal_year=2024", headers=headers
    )
    assert bal_res.status_code == 200
    balances = bal_res.json()
    assert len(balances) >= 1
    bal = next(b for b in balances if b["leave_type_id"] == type_id)
    assert bal["allocated_days"] == 10.0
    assert bal["pending_days"] == 3.0
    assert bal["used_days"] == 0.0

    # 4. Manager Approves Leave Request
    review_in = {
        "status": "APPROVED",
        "remarks": "Get well soon!",
    }
    review_res = await async_client.put(
        f"/api/v1/hr/leaves/requests/{request_id}/review",
        headers=headers,
        json=review_in,
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "APPROVED"

    # 5. Check Leave Balances after approval (pending -> used)
    bal_res2 = await async_client.get(
        f"/api/v1/hr/leaves/balances/{emp_id}?fiscal_year=2024", headers=headers
    )
    assert bal_res2.status_code == 200
    bal2 = next(b for b in bal_res2.json() if b["leave_type_id"] == type_id)
    assert bal2["pending_days"] == 0.0
    assert bal2["used_days"] == 3.0
    assert bal2["balance_days"] == 7.0

    # 6. List Leave Requests with filter
    list_req_res = await async_client.get(
        f"/api/v1/hr/leaves/requests?employee_id={emp_id}&status=APPROVED",
        headers=headers,
    )
    assert list_req_res.status_code == 200
    assert len(list_req_res.json()) == 1
