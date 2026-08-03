import uuid
from datetime import date, timedelta
import pytest
from httpx import ASGITransport, AsyncClient

from app.database.base import Base
from app.database.connection import set_fallback_sqlite_engine
from app.main import app
from app.tests.unit.test_phase3_org_structure import get_auth_headers_and_org


@pytest.fixture(autouse=True, scope="module")
async def setup_test_db():
    set_fallback_sqlite_engine()
    from app.database.connection import engine as test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_leave_types_balances_and_application_workflow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_LV_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Leave",
                "last_name": "User",
                "official_email": f"leave_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        employee_id = emp_res.json()["id"]

        # 2. Create Leave Type
        lt_code = f"AL_{uuid.uuid4().hex[:4].upper()}"
        lt_res = await client.post(
            "/api/v1/leave-types",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Annual Paid Leave",
                "code": lt_code,
                "description": "Standard annual paid vacation",
                "color": "#3B82F6",
                "is_paid": True,
                "requires_approval": True,
                "allow_half_day": True,
                "allow_negative_balance": False,
                "max_days_per_year": 20.0,
                "carry_forward": True,
                "carry_forward_limit": 5.0,
                "status": "active",
            },
        )
        assert lt_res.status_code == 201
        leave_type_id = lt_res.json()["id"]

        # 3. Duplicate Leave Type Code Validation
        dup_lt = await client.post(
            "/api/v1/leave-types",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Duplicate Leave Type",
                "code": lt_code,
            },
        )
        assert dup_lt.status_code == 400

        # 4. Get Leave Balances (Initializes balance automatically)
        bal_res = await client.get(
            f"/api/v1/leave-balances?employee_id={employee_id}",
            headers=headers,
        )
        assert bal_res.status_code == 200

        # 5. Apply for Leave
        today = date.today()
        start_d = str(today + timedelta(days=7))
        end_d = str(today + timedelta(days=9))

        apply_res = await client.post(
            "/api/v1/leave-requests",
            headers=headers,
            json={
                "employee_id": employee_id,
                "leave_type_id": leave_type_id,
                "start_date": start_d,
                "end_date": end_d,
                "is_half_day": False,
                "reason": "Summer vacation trip",
            },
        )
        assert apply_res.status_code == 201
        req_data = apply_res.json()
        assert req_data["status"] == "Pending"
        req_id = req_data["id"]

        # 6. Overlapping Leave Request Validation
        dup_apply = await client.post(
            "/api/v1/leave-requests",
            headers=headers,
            json={
                "employee_id": employee_id,
                "leave_type_id": leave_type_id,
                "start_date": start_d,
                "end_date": end_d,
                "reason": "Overlapping request",
            },
        )
        assert dup_apply.status_code == 400

        # 7. Approve Leave Request
        app_res = await client.post(
            f"/api/v1/leave-requests/{req_id}/approve",
            headers=headers,
            json={"approver_id": employee_id, "decision": "Approved", "remarks": "Approved by manager"},
        )
        assert app_res.status_code == 200
        assert app_res.json()["status"] == "Approved"

        # 8. Cancel Approved Leave (Restores Balance)
        cancel_res = await client.post(
            f"/api/v1/leave-requests/{req_id}/cancel",
            headers=headers,
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "Cancelled"


@pytest.mark.asyncio
async def test_comp_off_and_holiday_calendar_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_HOL_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Holiday",
                "last_name": "Tester",
                "official_email": f"hol_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        employee_id = emp_res.json()["id"]

        # 2. Create Comp-Off Credit
        co_res = await client.post(
            "/api/v1/comp-offs",
            headers=headers,
            json={
                "employee_id": employee_id,
                "earned_date": str(date.today() - timedelta(days=5)),
                "expiry_date": str(date.today() + timedelta(days=30)),
                "days": 1.0,
            },
        )
        assert co_res.status_code == 201
        co_id = co_res.json()["id"]

        # 3. List Comp-Offs
        list_co_res = await client.get(
            f"/api/v1/comp-offs?employee_id={employee_id}",
            headers=headers,
        )
        assert list_co_res.status_code == 200
        assert len(list_co_res.json()) >= 1

        # 4. Create Holiday Calendar
        cal_res = await client.post(
            "/api/v1/holiday-calendars",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "US Corporate Calendar 2026",
                "country": "United States",
                "year": 2026,
            },
        )
        assert cal_res.status_code == 201
        cal_id = cal_res.json()["id"]

        # 5. Create Holiday Event
        event_res = await client.post(
            "/api/v1/holiday-events",
            headers=headers,
            json={
                "calendar_id": cal_id,
                "holiday_date": "2026-12-25",
                "holiday_name": "Christmas Day",
                "holiday_type": "national",
                "is_optional": False,
            },
        )
        assert event_res.status_code == 201

        # 6. Get Dashboard Summary
        dash_res = await client.get(
            f"/api/v1/leave-dashboard-summary?org_id={org_id}&employee_id={employee_id}",
            headers=headers,
        )
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "total_balances" in dash_data
        assert "pending_requests_count" in dash_data
