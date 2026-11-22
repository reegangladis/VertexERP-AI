"""Integration and Security tests for Shifts, Attendance, and Regularization (Feature 4)."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"attadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Attendance Admin {suffix}",
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
            "first_name": "David",
            "last_name": "Miller",
            "email": f"david.miller.{clean_suffix}@example.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_shifts_and_assignments(async_client: AsyncClient):
    """Verifies Shift creation and assignment."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "shift_test")

    # 1. Create Shift
    shift_in = {
        "code": "GEN-09-17",
        "name": "General Day Shift",
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "break_duration_minutes": 60,
        "grace_period_minutes": 15,
        "is_night_shift": False,
        "is_active": True,
    }
    res = await async_client.post("/api/v1/hr/attendance/shifts", headers=headers, json=shift_in)
    assert res.status_code == 201
    shift = res.json()
    shift_id = shift["id"]

    # 2. Duplicate Shift code returns 409
    dup_res = await async_client.post(
        "/api/v1/hr/attendance/shifts", headers=headers, json=shift_in
    )
    assert dup_res.status_code == 409

    # 3. List Shifts
    list_res = await async_client.get("/api/v1/hr/attendance/shifts", headers=headers)
    assert list_res.status_code == 200
    assert any(s["id"] == shift_id for s in list_res.json())

    # 4. Assign Shift to Employee
    assign_in = {
        "employee_id": str(emp_id),
        "shift_id": shift_id,
        "start_date": "2024-01-01",
        "is_active": True,
    }
    assign_res = await async_client.post(
        "/api/v1/hr/attendance/shifts/assign", headers=headers, json=assign_in
    )
    assert assign_res.status_code == 201


@pytest.mark.asyncio
async def test_clock_in_clock_out_and_hours_calculation(async_client: AsyncClient):
    """Verifies clock-in, clock-out, worked hours computation, and overtime."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "clock_test")

    work_date = "2024-05-10"
    in_time = datetime(2024, 5, 10, 9, 0, 0, tzinfo=UTC)
    out_time = datetime(2024, 5, 10, 18, 30, 0, tzinfo=UTC)  # 9.5 hours total

    # 1. Clock In
    clock_in_payload = {
        "employee_id": str(emp_id),
        "work_date": work_date,
        "check_in_time": in_time.isoformat(),
        "check_in_ip": "192.168.1.50",
        "verification_method": "WEB",
    }
    in_res = await async_client.post(
        "/api/v1/hr/attendance/clock-in", headers=headers, json=clock_in_payload
    )
    assert in_res.status_code == 200
    record = in_res.json()
    record["id"]
    assert record["status"] == "PRESENT"

    # 2. Duplicate Clock In returns 409
    dup_in = await async_client.post(
        "/api/v1/hr/attendance/clock-in", headers=headers, json=clock_in_payload
    )
    assert dup_in.status_code == 409

    # 3. Clock Out
    clock_out_payload = {
        "employee_id": str(emp_id),
        "work_date": work_date,
        "check_out_time": out_time.isoformat(),
        "check_out_ip": "192.168.1.50",
    }
    out_res = await async_client.post(
        "/api/v1/hr/attendance/clock-out", headers=headers, json=clock_out_payload
    )
    assert out_res.status_code == 200
    out_record = out_res.json()
    assert out_record["regular_hours"] == 8.0
    assert out_record["overtime_hours"] == 1.5
    assert out_record["status"] == "OVERTIME"

    # 4. List Attendance Records
    list_res = await async_client.get(
        f"/api/v1/hr/attendance/records?employee_id={emp_id}&start_date={work_date}&end_date={work_date}",
        headers=headers,
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1


@pytest.mark.asyncio
async def test_attendance_regularization_workflow(async_client: AsyncClient):
    """Verifies regularization request submission and manager approval."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "reg_test")

    # 1. Clock in with missing out-time
    work_date = "2024-05-11"
    in_time = datetime(2024, 5, 11, 9, 30, 0, tzinfo=UTC)
    in_res = await async_client.post(
        "/api/v1/hr/attendance/clock-in",
        headers=headers,
        json={
            "employee_id": str(emp_id),
            "work_date": work_date,
            "check_in_time": in_time.isoformat(),
        },
    )
    assert in_res.status_code == 200
    record_id = in_res.json()["id"]

    # 2. Request Regularization
    req_out = datetime(2024, 5, 11, 17, 30, 0, tzinfo=UTC)
    reg_in = {
        "attendance_record_id": record_id,
        "employee_id": str(emp_id),
        "requested_check_out": req_out.isoformat(),
        "reason": "Forgot to punch out due to client visit.",
    }
    reg_res = await async_client.post(
        "/api/v1/hr/attendance/regularizations", headers=headers, json=reg_in
    )
    assert reg_res.status_code == 201
    reg = reg_res.json()
    reg_id = reg["id"]
    assert reg["status"] == "PENDING"

    # 3. Manager approves regularization
    review_res = await async_client.put(
        f"/api/v1/hr/attendance/regularizations/{reg_id}/review",
        headers=headers,
        json={"status": "APPROVED", "remarks": "Approved. Verified with client visit slip."},
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "APPROVED"
