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
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_enterprise_hr_workflow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        uid = uuid.uuid4().hex[:6]
        email = f"hr_admin_{uid}@vertexerp.ai"

        # 1. Register HR Admin User
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "HR",
                "last_name": "Admin",
                "username": f"hr_admin_{uid}",
                "email": email,
                "password": "HrPassword123!",
            },
        )
        assert reg_res.status_code == 201

        # 2. Login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": email,
                "password": "HrPassword123!",
            },
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Organization
        org_res = await client.post(
            "/api/v1/organizations",
            json={
                "name": f"HR Enterprise Org {uid}",
                "slug": f"hr-org-{uid}",
                "country": "USA",
            },
            headers=headers,
        )
        assert org_res.status_code == 201
        org_id = org_res.json()["id"]

        # 4. Create Department
        dept_res = await client.post(
            "/api/v1/departments",
            json={
                "organization_id": org_id,
                "name": "Human Resources",
                "code": f"HRD-{uid}",
            },
            headers=headers,
        )
        assert dept_res.status_code == 201
        dept_id = dept_res.json()["id"]

        # 5. Create Employee
        emp_number = f"EMP-{uid}"
        official_email = f"john.doe.{uid}@vertexerp.ai"
        emp_payload = {
            "organization_id": org_id,
            "department_id": dept_id,
            "employee_number": emp_number,
            "official_email": official_email,
            "official_phone": "+1-555-0199",
            "work_location": "Headquarters - New York",
            "employment_type": "full_time",
            "employment_status": "active",
            "profile": {
                "personal_email": f"john.personal.{uid}@gmail.com",
                "personal_phone": "+1-555-0188",
                "city": "New York",
                "country": "USA",
                "bio": "Senior HR Manager with 8+ years of ERP HCM experience.",
            },
        }
        create_emp_res = await client.post(
            "/api/v1/employees",
            json=emp_payload,
            headers=headers,
        )
        assert create_emp_res.status_code == 201
        emp_data = create_emp_res.json()
        emp_id = emp_data["id"]
        assert emp_data["employee_number"] == emp_number
        assert emp_data["profile_completion_percentage"] > 0

        # 6. Add Emergency Contact
        contact_res = await client.post(
            f"/api/v1/employees/{emp_id}/emergency-contacts",
            json={
                "name": "Jane Doe",
                "relationship": "Spouse",
                "phone": "+1-555-9988",
                "primary_contact": True,
            },
            headers=headers,
        )
        assert contact_res.status_code == 201

        # 7. Add Skill
        skill_res = await client.post(
            f"/api/v1/employees/{emp_id}/skills",
            json={
                "skill_name": "Workday HCM",
                "skill_level": "expert",
                "years_of_experience": 5.5,
            },
            headers=headers,
        )
        assert skill_res.status_code == 201

        # 8. Add Certification
        cert_res = await client.post(
            f"/api/v1/employees/{emp_id}/certifications",
            json={
                "certificate_name": "SHRM Certified Professional (SHRM-CP)",
                "issuer": "SHRM",
            },
            headers=headers,
        )
        assert cert_res.status_code == 201

        # 9. Fetch Employee Details
        get_emp_res = await client.get(f"/api/v1/employees/{emp_id}", headers=headers)
        assert get_emp_res.status_code == 200
        full_emp = get_emp_res.json()
        assert len(full_emp["emergency_contacts"]) == 1
        assert len(full_emp["skills"]) == 1
        assert len(full_emp["certifications"]) == 1
        assert len(full_emp["history"]) >= 1

        # 10. Search Employees
        search_res = await client.get(
            f"/api/v1/employees?org_id={org_id}&query={emp_number}", headers=headers
        )
        assert search_res.status_code == 200
        search_list = search_res.json()
        assert len(search_list) >= 1
