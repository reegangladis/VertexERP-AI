import uuid
import pytest
from datetime import date
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
async def test_phase9_training_complete_workflow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        uid = uuid.uuid4().hex[:6]
        email = f"trn_admin_{uid}@vertexerp.ai"

        # 1. Register Admin User
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Train",
                "last_name": "Admin",
                "username": f"trn_admin_{uid}",
                "email": email,
                "password": "TrainPassword123!",
            },
        )
        assert reg_res.status_code == 201

        # 2. Login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": email,
                "password": "TrainPassword123!",
            },
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Organization
        org_res = await client.post(
            "/api/v1/organizations",
            json={
                "name": f"LMS Enterprise Org {uid}",
                "slug": f"lms-org-{uid}",
                "country": "USA",
            },
            headers=headers,
        )
        assert org_res.status_code == 201
        org_id = org_res.json()["id"]

        # 4. Create Employee
        emp_res = await client.post(
            "/api/v1/employees",
            json={
                "organization_id": org_id,
                "employee_number": f"EMP-LMS-{uid}",
                "official_email": f"lms.emp.{uid}@vertexerp.ai",
                "employment_type": "full_time",
                "employment_status": "active",
            },
            headers=headers,
        )
        assert emp_res.status_code == 201
        emp_id = emp_res.json()["id"]

        # 5. Create Training Course & Module
        course_res = await client.post(
            "/api/v1/training/courses",
            json={
                "organization_id": org_id,
                "course_code": f"SEC-{uid}",
                "course_name": "Cybersecurity & Data Privacy 2026",
                "category": "Compliance",
                "difficulty_level": "Intermediate",
                "duration_hours": 4.5,
                "delivery_mode": "Online",
            },
            headers=headers,
        )
        assert course_res.status_code == 201
        course_id = course_res.json()["id"]

        mod_res = await client.post(
            f"/api/v1/training/courses/{course_id}/modules",
            json={
                "module_name": "Module 1: Phishing & Identity Protection",
                "module_order": 1,
                "duration_minutes": 45,
                "content_url": "https://lms.vertexerp.ai/video/sec-m1.mp4",
            },
            headers=headers,
        )
        assert mod_res.status_code == 201

        # 6. Create Assessment
        ass_res = await client.post(
            "/api/v1/training/assessments",
            json={
                "course_id": course_id,
                "assessment_name": "Security Awareness Final Exam",
                "passing_score": 75.0,
                "total_marks": 100.0,
                "duration_minutes": 30,
            },
            headers=headers,
        )
        assert ass_res.status_code == 201
        ass_id = ass_res.json()["id"]

        # 7. Assign Course to Employee
        assign_res = await client.post(
            "/api/v1/training/assign",
            json={
                "employee_id": emp_id,
                "course_id": course_id,
                "due_date": "2026-09-30",
            },
            headers=headers,
        )
        assert assign_res.status_code == 201
        training_id = assign_res.json()["id"]

        # 8. Submit Assessment Attempt (Score 85.0 -> Passed)
        attempt_res = await client.post(
            f"/api/v1/training/assessments/{ass_id}/submit",
            json={
                "employee_id": emp_id,
                "score": 85.0,
            },
            headers=headers,
        )
        assert attempt_res.status_code == 201
        assert attempt_res.json()["passed"] is True

        # 9. Update Training Progress to 100% -> Auto-generate Certificate
        prog_res = await client.post(
            f"/api/v1/training/trainings/{training_id}/progress",
            json={"completion_percentage": 100.0},
            headers=headers,
        )
        assert prog_res.status_code == 200
        tr_data = prog_res.json()
        assert tr_data["status"] == "Completed"
        assert len(tr_data["certifications"]) == 1
        assert "CERT-SEC-" in tr_data["certifications"][0]["certificate_number"]

        # 10. Add Employee Skill
        skill_res = await client.post(
            "/api/v1/training/skills",
            json={
                "employee_id": emp_id,
                "skill_name": "Cybersecurity Risk Audit",
                "skill_level": "Advanced",
                "verified": True,
            },
            headers=headers,
        )
        assert skill_res.status_code == 201

        # 11. Dashboard Summary API
        dash_res = await client.get(
            f"/api/v1/training/dashboard-summary?org_id={org_id}&employee_id={emp_id}",
            headers=headers,
        )
        assert dash_res.status_code == 200
        summary = dash_res.json()
        assert summary["completed_courses_count"] == 1
        assert summary["certificates_earned_count"] == 1
