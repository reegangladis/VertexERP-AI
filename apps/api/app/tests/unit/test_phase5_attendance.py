import uuid
from datetime import date, datetime, timedelta, UTC
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
async def test_attendance_checkin_checkout_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_ATT_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Attendance",
                "last_name": "TestUser",
                "official_email": f"att_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        emp_data = emp_res.json()
        employee_id = emp_data["id"]

        # 2. Check-In
        checkin_res = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={
                "employee_id": employee_id,
                "attendance_source": "Web",
                "remarks": "Morning Check-In",
            },
        )
        assert checkin_res.status_code == 201
        checkin_data = checkin_res.json()
        assert checkin_data["employee_id"] == employee_id
        assert checkin_data["status"] == "Present"
        record_id = checkin_data["id"]

        # 3. Duplicate Check-In Validation
        dup_checkin_res = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={
                "employee_id": employee_id,
                "attendance_source": "Web",
            },
        )
        assert dup_checkin_res.status_code == 400
        assert "already checked in" in dup_checkin_res.json()["message"].lower()

        # 4. Check-Out
        checkout_res = await client.post(
            "/api/v1/attendance/check-out",
            headers=headers,
            json={
                "attendance_record_id": record_id,
                "remarks": "Evening Check-Out",
            },
        )
        assert checkout_res.status_code == 200
        checkout_data = checkout_res.json()
        assert checkout_data["id"] == record_id
        assert checkout_data["check_out"] is not None

        # 5. Get Attendance Record Details
        get_res = await client.get(
            f"/api/v1/attendance/{record_id}",
            headers=headers,
        )
        assert get_res.status_code == 200
        assert get_res.json()["id"] == record_id

        # 6. List Attendance Records
        list_res = await client.get(
            f"/api/v1/attendance?employee_id={employee_id}",
            headers=headers,
        )
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_shifts_corrections_and_overtime_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_SHF_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Shift",
                "last_name": "Worker",
                "official_email": f"shift_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        employee_id = emp_res.json()["id"]

        # 2. Create Shift
        shift_code = f"SHF_{uuid.uuid4().hex[:4].upper()}"
        shift_res = await client.post(
            "/api/v1/shifts",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Morning Standard Shift",
                "code": shift_code,
                "start_time": "09:00",
                "end_time": "17:00",
                "grace_time_minutes": 15,
                "break_duration_minutes": 60,
                "is_night_shift": False,
                "status": "active",
            },
        )
        assert shift_res.status_code == 201
        shift_id = shift_res.json()["id"]

        # 3. Duplicate Shift Code Validation
        dup_shift = await client.post(
            "/api/v1/shifts",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Duplicate Shift",
                "code": shift_code,
                "start_time": "09:00",
                "end_time": "17:00",
            },
        )
        assert dup_shift.status_code == 400

        # 4. Assign Shift to Employee
        assign_res = await client.post(
            "/api/v1/shift-assignments",
            headers=headers,
            json={
                "employee_id": employee_id,
                "shift_id": shift_id,
                "effective_from": str(date.today()),
                "status": "active",
            },
        )
        assert assign_res.status_code == 201

        # 5. Create Check-In & Check-Out for Correction Test
        checkin_res = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={"employee_id": employee_id, "attendance_source": "Web"},
        )
        assert checkin_res.status_code == 201
        rec_id = checkin_res.json()["id"]

        checkout_res = await client.post(
            "/api/v1/attendance/check-out",
            headers=headers,
            json={"attendance_record_id": rec_id},
        )
        assert checkout_res.status_code == 200

        # 6. Request Attendance Correction
        now = datetime.now(UTC)
        new_in = (now - timedelta(hours=8)).isoformat()
        new_out = now.isoformat()

        corr_res = await client.post(
            "/api/v1/attendance/corrections",
            headers=headers,
            json={
                "attendance_record_id": rec_id,
                "requested_by": employee_id,
                "reason": "Forget punch card",
                "new_check_in": new_in,
                "new_check_out": new_out,
            },
        )
        assert corr_res.status_code == 201
        corr_id = corr_res.json()["id"]

        # 7. Approve Attendance Correction
        app_corr_res = await client.post(
            f"/api/v1/attendance/corrections/{corr_id}/approve",
            headers=headers,
            json={"status": "Approved", "approved_by": employee_id},
        )
        assert app_corr_res.status_code == 200
        assert app_corr_res.json()["status"] == "Approved"

        # 8. Create Overtime Record
        ot_res = await client.post(
            "/api/v1/overtime",
            headers=headers,
            json={
                "employee_id": employee_id,
                "attendance_record_id": rec_id,
                "hours": 2.5,
                "reason": "Emergency production release",
            },
        )
        assert ot_res.status_code == 201
        ot_id = ot_res.json()["id"]

        # 9. Approve Overtime Record
        app_ot_res = await client.post(
            f"/api/v1/overtime/{ot_id}/approve",
            headers=headers,
            json={"approved": True, "approved_by": employee_id},
        )
        assert app_ot_res.status_code == 200
        assert app_ot_res.json()["approved"] is True

        # 10. Attendance Devices Creation
        dev_res = await client.post(
            "/api/v1/attendance-devices",
            headers=headers,
            json={
                "organization_id": org_id,
                "device_name": "Lobby Biometric Scanner",
                "device_type": "Biometric",
                "serial_number": f"SN-{uuid.uuid4().hex[:6].upper()}",
                "location": "Main Entrance",
            },
        )
        assert dev_res.status_code == 201

        # 11. Dashboard Summary
        dash_res = await client.get(
            f"/api/v1/attendance/dashboard-summary?org_id={org_id}",
            headers=headers,
        )
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "total_employees" in dash_data
        assert "present_today" in dash_data
