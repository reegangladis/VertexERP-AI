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
async def test_salary_components_structures_and_assignments_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_PAY_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Payroll",
                "last_name": "Employee",
                "official_email": f"pay_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        employee_id = emp_res.json()["id"]

        # 2. Create Salary Component
        code = f"BASIC_{uuid.uuid4().hex[:4].upper()}"
        comp_res = await client.post(
            "/api/v1/salary-components",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Basic Salary",
                "code": code,
                "component_type": "Basic",
                "calculation_type": "flat",
                "taxable": True,
                "affects_pf": True,
                "affects_esi": False,
                "display_order": 1,
                "status": "active",
            },
        )
        assert comp_res.status_code == 201
        comp_id = comp_res.json()["id"]

        # 3. Duplicate Component Code Validation
        dup_comp = await client.post(
            "/api/v1/salary-components",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Duplicate Basic",
                "code": code,
                "component_type": "Basic",
            },
        )
        assert dup_comp.status_code == 400

        # 4. Create Salary Structure
        struct_code = f"EXEC_{uuid.uuid4().hex[:4].upper()}"
        struct_res = await client.post(
            "/api/v1/salary-structures",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Executive Compensation Structure",
                "code": struct_code,
                "description": "Standard executive grade A compensation plan",
                "effective_from": "2026-01-01",
                "status": "active",
                "components": [
                    {
                        "salary_component_id": comp_id,
                        "amount": 3000.0,
                        "percentage": 50.0,
                        "sequence": 1,
                    }
                ],
            },
        )
        assert struct_res.status_code == 201
        struct_id = struct_res.json()["id"]

        # 5. Assign Salary Structure to Employee
        assign_res = await client.post(
            "/api/v1/employee-salary-assignments",
            headers=headers,
            json={
                "employee_id": employee_id,
                "salary_structure_id": struct_id,
                "effective_from": "2026-01-01",
                "gross_salary": 6000.0,
                "ctc": 72000.0,
                "status": "active",
            },
        )
        assert assign_res.status_code == 201

        # 6. Duplicate Active Salary Assignment Validation
        dup_assign = await client.post(
            "/api/v1/employee-salary-assignments",
            headers=headers,
            json={
                "employee_id": employee_id,
                "salary_structure_id": struct_id,
                "effective_from": "2026-01-01",
                "gross_salary": 6000.0,
                "ctc": 72000.0,
            },
        )
        assert dup_assign.status_code == 400

        # 7. Negative Salary Assignment Validation
        neg_assign = await client.post(
            "/api/v1/employee-salary-assignments",
            headers=headers,
            json={
                "employee_id": employee_id,
                "salary_structure_id": struct_id,
                "effective_from": "2026-01-01",
                "gross_salary": -500.0,
                "ctc": -6000.0,
            },
        )
        assert neg_assign.status_code == 400


@pytest.mark.asyncio
async def test_payroll_period_run_generation_and_approval_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        emp_code = f"EMP_RUN_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Run",
                "last_name": "Tester",
                "official_email": f"run_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert emp_res.status_code == 201
        employee_id = emp_res.json()["id"]

        # 2. Create Salary Component & Structure
        code = f"BASIC_{uuid.uuid4().hex[:4].upper()}"
        comp_res = await client.post(
            "/api/v1/salary-components",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Base Pay",
                "code": code,
                "component_type": "Basic",
                "calculation_type": "flat",
            },
        )
        assert comp_res.status_code == 201
        comp_id = comp_res.json()["id"]

        struct_res = await client.post(
            "/api/v1/salary-structures",
            headers=headers,
            json={
                "organization_id": org_id,
                "name": "Standard Pay Structure",
                "code": f"STR_{uuid.uuid4().hex[:4].upper()}",
                "effective_from": "2026-01-01",
            },
        )
        assert struct_res.status_code == 201
        struct_id = struct_res.json()["id"]

        # 3. Assign Salary
        await client.post(
            "/api/v1/employee-salary-assignments",
            headers=headers,
            json={
                "employee_id": employee_id,
                "salary_structure_id": struct_id,
                "effective_from": "2026-01-01",
                "gross_salary": 5000.0,
                "ctc": 60000.0,
            },
        )

        # 4. Create Employee Loan & Reimbursement
        loan_res = await client.post(
            "/api/v1/employee-loans",
            headers=headers,
            json={
                "employee_id": employee_id,
                "loan_type": "Personal Advance",
                "principal_amount": 1000.0,
                "emi_amount": 100.0,
                "interest_rate": 0.0,
            },
        )
        assert loan_res.status_code == 201

        reimb_res = await client.post(
            "/api/v1/reimbursements",
            headers=headers,
            json={
                "employee_id": employee_id,
                "title": "Client Travel Expense",
                "amount": 150.0,
                "submitted_date": str(date.today()),
            },
        )
        assert reimb_res.status_code == 201
        reimb_id = reimb_res.json()["id"]

        # Approve reimbursement
        await client.patch(
            f"/api/v1/reimbursements/{reimb_id}",
            headers=headers,
            json={"status": "Approved", "approved_date": str(date.today())},
        )

        # 5. Create Payroll Period
        period_res = await client.post(
            "/api/v1/payroll-periods",
            headers=headers,
            json={
                "organization_id": org_id,
                "month": 8,
                "year": 2026,
                "start_date": "2026-08-01",
                "end_date": "2026-08-31",
                "status": "Open",
            },
        )
        assert period_res.status_code == 201
        period_id = period_res.json()["id"]

        # 6. Generate Payroll Run
        gen_res = await client.post(
            "/api/v1/payroll-runs/generate",
            headers=headers,
            json={"payroll_period_id": period_id, "processed_by": employee_id},
        )
        assert gen_res.status_code == 201
        run_data = gen_res.json()
        assert run_data["status"] == "Completed"
        assert run_data["employees_processed"] >= 1
        run_id = run_data["id"]

        # 7. List Employee Payslips
        payslip_res = await client.get(
            f"/api/v1/payslips/employee/{employee_id}",
            headers=headers,
        )
        assert payslip_res.status_code == 200
        payslips = payslip_res.json()
        assert len(payslips) >= 1
        payslip_id = payslips[0]["id"]

        # Download Payslip PDF
        dl_res = await client.get(
            f"/api/v1/payslips/{payslip_id}/download",
            headers=headers,
        )
        assert dl_res.status_code == 200
        assert "OFFICIAL PAYSLIP" in dl_res.text

        # 8. Approve Payroll Run
        app_res = await client.post(
            f"/api/v1/payroll-runs/{run_id}/approve?approver_id={employee_id}",
            headers=headers,
        )
        assert app_res.status_code == 200
        assert app_res.json()["status"] == "Approved"

        # 9. Lock Period
        lock_res = await client.post(
            f"/api/v1/payroll-periods/{period_id}/lock",
            headers=headers,
        )
        assert lock_res.status_code == 200
        assert lock_res.json()["locked"] is True

        # 10. Generate Payroll on Locked Period Validation
        locked_gen = await client.post(
            "/api/v1/payroll-runs/generate",
            headers=headers,
            json={"payroll_period_id": period_id},
        )
        assert locked_gen.status_code == 400

        # 11. Dashboard Summary
        dash_res = await client.get(
            f"/api/v1/payroll-dashboard-summary?org_id={org_id}",
            headers=headers,
        )
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "payroll_status" in dash_data
        assert "total_gross_salary" in dash_data
