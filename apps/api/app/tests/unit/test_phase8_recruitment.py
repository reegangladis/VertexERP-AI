import uuid
from datetime import date, datetime, timedelta
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
async def test_job_requisition_candidate_and_application_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        code = f"JOB_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Recruitment Job
        job_res = await client.post(
            "/api/v1/recruitment-jobs",
            headers=headers,
            json={
                "organization_id": org_id,
                "job_title": "Senior AI Architect",
                "job_code": code,
                "employment_type": "Full-Time",
                "location": "San Francisco, CA",
                "vacancies": 2,
                "salary_min": 140000.0,
                "salary_max": 180000.0,
                "description": "Lead the enterprise AI ERP architecture team.",
                "status": "Open",
            },
        )
        assert job_res.status_code == 201
        job_id = job_res.json()["id"]

        # 2. Duplicate Job Code Validation
        dup_job = await client.post(
            "/api/v1/recruitment-jobs",
            headers=headers,
            json={
                "organization_id": org_id,
                "job_title": "Duplicate Job",
                "job_code": code,
            },
        )
        assert dup_job.status_code == 400

        # 3. Create Candidate
        email = f"candidate_{uuid.uuid4().hex[:4]}@vertexerp.ai"
        cand_res = await client.post(
            "/api/v1/candidates",
            headers=headers,
            json={
                "organization_id": org_id,
                "first_name": "Sarah",
                "last_name": "Connor",
                "email": email,
                "phone": "+1-555-0192",
                "experience_years": 6.5,
                "expected_salary": 165000.0,
                "resume_url": "https://storage.vertexerp.ai/resumes/sarah_connor.pdf",
            },
        )
        assert cand_res.status_code == 201
        candidate_id = cand_res.json()["id"]

        # 4. Duplicate Candidate Email Validation
        dup_cand = await client.post(
            "/api/v1/candidates",
            headers=headers,
            json={
                "organization_id": org_id,
                "first_name": "Duplicate",
                "last_name": "Sarah",
                "email": email,
            },
        )
        assert dup_cand.status_code == 400

        # 5. Apply for Job
        app_res = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={
                "candidate_id": candidate_id,
                "job_id": job_id,
                "application_source": "LinkedIn",
                "screening_notes": "Strong background in AI and cloud architecture.",
            },
        )
        assert app_res.status_code == 201
        app_data = app_res.json()
        assert app_data["status"] == "Applied"
        assert app_data["resume_score"] > 0
        application_id = app_data["id"]

        # 6. Duplicate Application Validation
        dup_app = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={
                "candidate_id": candidate_id,
                "job_id": job_id,
            },
        )
        assert dup_app.status_code == 400

        # 7. Move Application Pipeline Stage
        move_res = await client.post(
            f"/api/v1/applications/{application_id}/move-stage",
            headers=headers,
            json={"new_stage": "Screening", "remarks": "Screening call scheduled."},
        )
        assert move_res.status_code == 200
        assert move_res.json()["status"] == "Screening"


@pytest.mark.asyncio
async def test_interview_offer_and_onboarding_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, user_id = await get_auth_headers_and_org(client)
        code = f"JOB_{uuid.uuid4().hex[:6].upper()}"

        # 1. Create Job & Candidate
        job_res = await client.post(
            "/api/v1/recruitment-jobs",
            headers=headers,
            json={
                "organization_id": org_id,
                "job_title": "Lead Full Stack Engineer",
                "job_code": code,
                "vacancies": 1,
            },
        )
        assert job_res.status_code == 201
        job_id = job_res.json()["id"]

        cand_res = await client.post(
            "/api/v1/candidates",
            headers=headers,
            json={
                "organization_id": org_id,
                "first_name": "Alex",
                "last_name": "Rivera",
                "email": f"alex_{uuid.uuid4().hex[:4]}@vertexerp.ai",
                "experience_years": 5.0,
            },
        )
        assert cand_res.status_code == 201
        candidate_id = cand_res.json()["id"]

        # 2. Apply for Job
        app_res = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={"candidate_id": candidate_id, "job_id": job_id},
        )
        assert app_res.status_code == 201
        application_id = app_res.json()["id"]

        # 3. Schedule Interview Round
        sched_time = (datetime.now() + timedelta(days=2)).isoformat()
        round_res = await client.post(
            "/api/v1/interview-rounds",
            headers=headers,
            json={
                "application_id": application_id,
                "round_name": "Technical Deep Dive",
                "round_number": 1,
                "scheduled_at": sched_time,
                "meeting_link": "https://meet.vertexerp.ai/room-101",
            },
        )
        assert round_res.status_code == 201
        round_id = round_res.json()["id"]

        # 4. Submit Interview Feedback
        fb_res = await client.post(
            "/api/v1/interview-feedback",
            headers=headers,
            json={
                "interview_round_id": round_id,
                "technical_score": 4.8,
                "communication_score": 4.5,
                "problem_solving_score": 4.7,
                "culture_fit_score": 4.9,
                "recommendation": "Strong Hire",
                "comments": "Exceptional technical & architectural skills.",
            },
        )
        assert fb_res.status_code == 201
        assert fb_res.json()["overall_score"] >= 4.5

        # 5. Create Job Offer
        offer_res = await client.post(
            "/api/v1/job-offers",
            headers=headers,
            json={
                "application_id": application_id,
                "offered_salary": 150000.0,
                "joining_bonus": 10000.0,
                "joining_date": str(date.today() + timedelta(days=30)),
                "offer_letter_url": "https://storage.vertexerp.ai/offers/offer_alex.pdf",
            },
        )
        assert offer_res.status_code == 201
        offer_id = offer_res.json()["id"]

        # 6. List Onboarding Tasks (Generated automatically upon offer)
        tasks_res = await client.get(
            f"/api/v1/onboarding-tasks?offer_id={offer_id}",
            headers=headers,
        )
        assert tasks_res.status_code == 200
        tasks = tasks_res.json()
        assert len(tasks) >= 3

        # 7. Accept Offer
        accept_res = await client.post(
            f"/api/v1/job-offers/{offer_id}/accept",
            headers=headers,
        )
        assert accept_res.status_code == 200
        assert accept_res.json()["status"] == "Accepted"

        # 8. Dashboard Summary
        dash_res = await client.get(
            f"/api/v1/recruitment-dashboard-summary?org_id={org_id}",
            headers=headers,
        )
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "open_positions" in dash_data
        assert "candidates_applied" in dash_data
