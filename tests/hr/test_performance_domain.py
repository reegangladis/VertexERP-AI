"""Integration tests for Performance Management & OKR Domain (Feature 8)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"perfadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Performance Admin {suffix}",
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
            "first_name": "Jim",
            "last_name": "Halpert",
            "email": f"jim.halpert.{clean_suffix}@example.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_review_periods_and_goals(async_client: AsyncClient):
    """Verifies Performance Review Period and Employee Goal / OKR lifecycle."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "goals_test")

    # 1. Create Review Period
    period_in = {
        "code": "CY2024_H1",
        "title": "H1 2024 Performance Appraisal Cycle",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "self_review_deadline": "2024-07-07",
        "manager_review_deadline": "2024-07-15",
        "status": "ACTIVE",
    }
    period_res = await async_client.post(
        "/api/v1/hr/performance/periods", headers=headers, json=period_in
    )
    assert period_res.status_code == 201
    period = period_res.json()
    period_id = period["id"]
    assert period["code"] == "CY2024_H1"

    # Duplicate code returns 409
    dup_p = await async_client.post(
        "/api/v1/hr/performance/periods", headers=headers, json=period_in
    )
    assert dup_p.status_code == 409

    # 2. Create Employee Goal
    goal_in = {
        "employee_id": str(emp_id),
        "review_period_id": period_id,
        "title": "Deliver Core HR Module Architecture",
        "description": "Implement 9 HR sub-features with 100% test coverage.",
        "category": "INDIVIDUAL",
        "weightage": 3.0,
        "target_date": "2024-06-15",
    }
    goal_res = await async_client.post(
        "/api/v1/hr/performance/goals", headers=headers, json=goal_in
    )
    assert goal_res.status_code == 201
    goal = goal_res.json()
    goal_id = goal["id"]
    assert goal["status"] == "NOT_STARTED"

    # 3. Update Goal Progress
    update_g = await async_client.put(
        f"/api/v1/hr/performance/goals/{goal_id}",
        headers=headers,
        json={"progress_percentage": 75, "self_rating": 4.5},
    )
    assert update_g.status_code == 200
    assert update_g.json()["status"] == "IN_PROGRESS"
    assert update_g.json()["progress_percentage"] == 75

    # 4. List Goals
    list_g = await async_client.get(
        f"/api/v1/hr/performance/goals?employee_id={emp_id}", headers=headers
    )
    assert list_g.status_code == 200
    assert len(list_g.json()) == 1


@pytest.mark.asyncio
async def test_appraisal_multistage_review_workflow(async_client: AsyncClient):
    """Verifies complete multi-stage performance appraisal workflow."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "appraisal_flow")

    # 1. Setup Period
    p_res = await async_client.post(
        "/api/v1/hr/performance/periods",
        headers=headers,
        json={
            "code": "ANNUAL_2024",
            "title": "Annual 2024 Appraisal",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "status": "ACTIVE",
        },
    )
    period_id = p_res.json()["id"]

    # 2. Initiate Review
    rev_res = await async_client.post(
        "/api/v1/hr/performance/reviews",
        headers=headers,
        json={"employee_id": str(emp_id), "review_period_id": period_id},
    )
    assert rev_res.status_code == 201
    review = rev_res.json()
    review_id = review["id"]
    assert review["status"] == "SELF_REVIEW"

    # 3. Employee Submits Self Review
    self_res = await async_client.put(
        f"/api/v1/hr/performance/reviews/{review_id}/self",
        headers=headers,
        json={
            "self_score": 90.0,
            "strengths": "Fast delivery and zero critical bugs.",
            "improvements": "Documentation",
        },
    )
    assert self_res.status_code == 200
    assert self_res.json()["status"] == "MANAGER_REVIEW"

    # 4. Manager Submits Review Assessment
    mgr_res = await async_client.put(
        f"/api/v1/hr/performance/reviews/{review_id}/manager",
        headers=headers,
        json={
            "manager_score": 92.5,
            "strengths": "Great cross-functional teamwork.",
            "promotion_recommendation": True,
            "salary_revision_recommendation": 15.0,
        },
    )
    assert mgr_res.status_code == 200
    assert mgr_res.json()["status"] == "HR_REVIEW"
    assert mgr_res.json()["promotion_recommendation"] is True

    # 5. HR Finalizes Review
    final_res = await async_client.put(
        f"/api/v1/hr/performance/reviews/{review_id}/finalize",
        headers=headers,
        json={"final_score": 92.0, "final_rating": "EXCEEDS"},
    )
    assert final_res.status_code == 200
    final = final_res.json()
    assert final["status"] == "FINALIZED"
    assert final["final_rating"] == "EXCEEDS"
    assert final["final_score"] == 92.0
