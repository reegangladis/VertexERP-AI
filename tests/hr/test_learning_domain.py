"""Integration tests for Learning & Development (LMS) Domain (Feature 9)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"learnadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Learning Admin {suffix}",
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
            "first_name": "Pam",
            "last_name": "Beesly",
            "email": f"pam.beesly.{clean_suffix}@example.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_training_course_and_modules_catalog(async_client: AsyncClient):
    """Verifies Training Course and Syllabus Modules creation and retrieval."""
    headers, _, _, _ = await create_tenant_and_employee(async_client, "courses_test")

    # 1. Create Course with Modules
    course_in = {
        "code": "SEC_101",
        "title": "Enterprise Information Security & Compliance",
        "description": "SOC2, ISO27001, and secure data handling standards.",
        "category": "COMPLIANCE",
        "duration_hours": 2.5,
        "provider": "INTERNAL",
        "is_mandatory": True,
        "modules": [
            {
                "title": "Introduction to Multi-Tenant Isolation",
                "sequence_order": 1,
                "content_type": "VIDEO",
                "duration_minutes": 30,
            },
            {
                "title": "Password & API Key Security",
                "sequence_order": 2,
                "content_type": "DOCUMENT",
                "duration_minutes": 45,
            },
            {
                "title": "Compliance Knowledge Check",
                "sequence_order": 3,
                "content_type": "QUIZ",
                "duration_minutes": 15,
            },
        ],
    }
    res = await async_client.post("/api/v1/hr/learning/courses", headers=headers, json=course_in)
    assert res.status_code == 201
    course = res.json()
    course_id = course["id"]
    assert course["code"] == "SEC_101"
    assert len(course["modules"]) == 3

    # Duplicate course code returns 409
    dup_res = await async_client.post(
        "/api/v1/hr/learning/courses", headers=headers, json=course_in
    )
    assert dup_res.status_code == 409

    # 2. Get Course details
    detail_res = await async_client.get(f"/api/v1/hr/learning/courses/{course_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "Enterprise Information Security & Compliance"


@pytest.mark.asyncio
async def test_enrollment_progress_and_skills_inventory(async_client: AsyncClient):
    """Verifies Course enrollment, progress advancement to completion, and skill/certification management."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "enrollment_test")

    # 1. Create Course
    course_res = await async_client.post(
        "/api/v1/hr/learning/courses",
        headers=headers,
        json={
            "code": "PYTHON_ADV",
            "title": "Advanced Async Python & FastAPI",
            "category": "TECHNICAL",
            "duration_hours": 10.0,
        },
    )
    course_id = course_res.json()["id"]

    # 2. Enroll Employee
    enroll_in = {"employee_id": str(emp_id), "course_id": course_id}
    enroll_res = await async_client.post(
        "/api/v1/hr/learning/enrollments", headers=headers, json=enroll_in
    )
    assert enroll_res.status_code == 201
    enrollment = enroll_res.json()
    enroll_id = enrollment["id"]
    assert enrollment["status"] == "ENROLLED"
    assert enrollment["progress_percentage"] == 0

    # 3. Update Progress to 50%
    prog_res = await async_client.put(
        f"/api/v1/hr/learning/enrollments/{enroll_id}/progress",
        headers=headers,
        json={"progress_percentage": 50},
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["status"] == "IN_PROGRESS"

    # 4. Complete Course (100% with score) -> Certificate awarded
    comp_res = await async_client.put(
        f"/api/v1/hr/learning/enrollments/{enroll_id}/progress",
        headers=headers,
        json={"progress_percentage": 100, "score": 98.0},
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["status"] == "COMPLETED"
    assert comp_data["certificate_url"] is not None
    assert comp_data["completion_date"] is not None

    # 5. Add Employee Skill
    skill_in = {
        "employee_id": str(emp_id),
        "skill_name": "FastAPI & SQLAlchemy",
        "proficiency_level": "EXPERT",
        "years_of_experience": 4.5,
    }
    skill_res = await async_client.post(
        "/api/v1/hr/learning/skills", headers=headers, json=skill_in
    )
    assert skill_res.status_code == 201
    assert skill_res.json()["is_verified"] is True

    # 6. Add Employee Certification
    cert_in = {
        "employee_id": str(emp_id),
        "certification_name": "AWS Certified Solutions Architect",
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2024-01-15",
        "credential_id": "AWS-PSA-994821",
    }
    cert_res = await async_client.post(
        "/api/v1/hr/learning/certifications", headers=headers, json=cert_in
    )
    assert cert_res.status_code == 201
    assert cert_res.json()["credential_id"] == "AWS-PSA-994821"

    # 7. List Skills and Certifications for employee
    skills_list = await async_client.get(
        f"/api/v1/hr/learning/skills/employee/{emp_id}", headers=headers
    )
    assert skills_list.status_code == 200
    assert len(skills_list.json()) == 1

    certs_list = await async_client.get(
        f"/api/v1/hr/learning/certifications/employee/{emp_id}", headers=headers
    )
    assert certs_list.status_code == 200
    assert len(certs_list.json()) == 1
