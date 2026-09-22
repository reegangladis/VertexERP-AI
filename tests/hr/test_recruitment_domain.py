"""Integration tests for Recruitment & Applicant Tracking System (Feature 7)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


async def create_tenant(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Helper to register a tenant and return headers, tenant_id, and org_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"recadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Recruitment Admin {suffix}",
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
async def test_job_requisition_lifecycle(async_client: AsyncClient):
    """Verifies Job Requisition creation, auto numbering, update, and listing."""
    headers, _, _ = await create_tenant(async_client, "req_test")

    # 1. Create Job Requisition
    req_in = {
        "title": "Senior AI Backend Engineer",
        "headcount": 2,
        "employment_type": "FULL_TIME",
        "experience_level": "SENIOR",
        "salary_min": 120000.0,
        "salary_max": 160000.0,
        "description": "Lead development of multi-tenant enterprise core modules.",
    }
    res = await async_client.post(
        "/api/v1/hr/recruitment/requisitions", headers=headers, json=req_in
    )
    assert res.status_code == 201
    data = res.json()
    assert data["requisition_number"].startswith("REQ-")
    assert data["status"] == "OPEN"
    req_id = data["id"]

    # 2. Update Requisition
    update_res = await async_client.put(
        f"/api/v1/hr/recruitment/requisitions/{req_id}",
        headers=headers,
        json={"headcount": 3, "salary_max": 170000.0},
    )
    assert update_res.status_code == 200
    assert update_res.json()["headcount"] == 3
    assert update_res.json()["salary_max"] == 170000.0

    # 3. List Requisitions
    list_res = await async_client.get(
        "/api/v1/hr/recruitment/requisitions?status=OPEN", headers=headers
    )
    assert list_res.status_code == 200
    assert any(r["id"] == req_id for r in list_res.json())


@pytest.mark.asyncio
async def test_applicant_hiring_pipeline_and_offer(async_client: AsyncClient):
    """Verifies Applicant creation, Interview scheduling, Feedback scoring, and Offer acceptance."""
    headers, _, _ = await create_tenant(async_client, "applicant_flow")

    # 1. Create Requisition
    req_res = await async_client.post(
        "/api/v1/hr/recruitment/requisitions",
        headers=headers,
        json={"title": "Frontend Architect", "headcount": 1},
    )
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # 2. Register Applicant
    app_in = {
        "requisition_id": req_id,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "phone": "+1-555-0199",
        "source": "LINKEDIN",
    }
    app_res = await async_client.post(
        "/api/v1/hr/recruitment/applicants", headers=headers, json=app_in
    )
    assert app_res.status_code == 201
    applicant = app_res.json()
    app_id = applicant["id"]
    assert applicant["current_stage"] == "APPLIED"

    # 3. Schedule Technical Interview
    sched_time = datetime.now(UTC) + timedelta(days=2)
    interview_in = {
        "applicant_id": app_id,
        "interview_type": "TECHNICAL",
        "scheduled_at": sched_time.isoformat(),
        "duration_minutes": 60,
        "meeting_link": "https://meet.google.com/xyz-test",
    }
    int_res = await async_client.post(
        "/api/v1/hr/recruitment/interviews", headers=headers, json=interview_in
    )
    assert int_res.status_code == 201
    interview = int_res.json()
    int_id = interview["id"]

    # Applicant stage should automatically transition to INTERVIEW
    app_check = await async_client.get(
        f"/api/v1/hr/recruitment/applicants/{app_id}", headers=headers
    )
    assert app_check.json()["current_stage"] == "INTERVIEW"

    # 4. Submit Interview Feedback
    feedback_in = {
        "interview_id": int_id,
        "rating": 5,
        "score": 95.0,
        "strengths": "Deep React architecture knowledge and clean component modeling.",
        "recommendation": "STRONG_HIRE",
        "notes": "Excellent cultural fit and technical depth.",
    }
    fb_res = await async_client.post(
        "/api/v1/hr/recruitment/feedbacks", headers=headers, json=feedback_in
    )
    assert fb_res.status_code == 201
    assert fb_res.json()["recommendation"] == "STRONG_HIRE"

    # 5. Extend Job Offer
    offer_in = {
        "applicant_id": app_id,
        "offered_salary": 145000.0,
        "currency": "USD",
        "joining_date": "2024-07-01",
    }
    offer_res = await async_client.post(
        "/api/v1/hr/recruitment/offers", headers=headers, json=offer_in
    )
    assert offer_res.status_code == 201
    offer = offer_res.json()
    offer_id = offer["id"]
    assert offer["status"] == "DRAFT"

    # Applicant stage should now be OFFER
    app_check2 = await async_client.get(
        f"/api/v1/hr/recruitment/applicants/{app_id}", headers=headers
    )
    assert app_check2.json()["current_stage"] == "OFFER"

    # 6. Candidate Accepts Offer -> Stage transitions to HIRED
    accept_res = await async_client.put(
        f"/api/v1/hr/recruitment/offers/{offer_id}/status",
        headers=headers,
        json={"status": "ACCEPTED"},
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"

    app_check3 = await async_client.get(
        f"/api/v1/hr/recruitment/applicants/{app_id}", headers=headers
    )
    assert app_check3.json()["current_stage"] == "HIRED"
