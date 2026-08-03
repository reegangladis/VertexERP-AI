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
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


async def get_auth_headers_and_org(client: AsyncClient):
    uid = uuid.uuid4().hex[:6]
    user_email = f"hr_admin_{uid}@vertexerp.ai"
    username = f"hr_admin_{uid}"
    password = "Password123!"

    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": user_email,
            "password": password,
            "first_name": "HR",
            "last_name": "Admin",
            "organization_name": f"Vertex HR Corp {uid}",
        },
    )
    assert reg_res.status_code == 201
    user_info = reg_res.json()
    org_id = user_info["organization_id"]

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": password},
    )
    assert login_res.status_code == 200
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers, org_id, user_info["id"]


@pytest.mark.asyncio
async def test_employee_crud_and_validations():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, _ = await get_auth_headers_and_org(client)
        emp_code = f"EMP_{uuid.uuid4().hex[:6].upper()}"
        official_email = f"john.doe_{uuid.uuid4().hex[:4]}@vertexerp.ai"

        # Create employee
        create_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "John",
                "last_name": "Doe",
                "gender": "male",
                "employment_type": "full_time",
                "employment_status": "active",
                "official_email": official_email,
                "official_phone": "+1-555-0199",
                "nationality": "American",
            },
        )
        assert create_res.status_code == 201
        emp = create_res.json()
        assert emp["employee_code"] == emp_code
        emp_id = emp["id"]

        # Duplicate code validation
        dup_code = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Jane",
                "last_name": "Smith",
                "official_email": f"jane_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert dup_code.status_code == 400
        assert "already exists" in dup_code.json()["message"]

        # Duplicate email validation
        dup_email = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": f"EMP_{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Johnny",
                "last_name": "Doe",
                "official_email": official_email,
            },
        )
        assert dup_email.status_code == 400
        assert "already exists" in dup_email.json()["message"]

        # List employees
        list_res = await client.get(
            f"/api/v1/employees?org_id={org_id}", headers=headers
        )
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # Get employee details
        get_res = await client.get(f"/api/v1/employees/{emp_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["first_name"] == "John"

        # Update employee
        update_res = await client.patch(
            f"/api/v1/employees/{emp_id}",
            headers=headers,
            json={"first_name": "Johnathon", "employment_status": "active"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["first_name"] == "Johnathon"


@pytest.mark.asyncio
async def test_employee_profile_and_subresources():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers, org_id, _ = await get_auth_headers_and_org(client)
        emp_code = f"EMP_{uuid.uuid4().hex[:6].upper()}"

        create_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "organization_id": org_id,
                "employee_code": emp_code,
                "first_name": "Alice",
                "last_name": "Smith",
                "official_email": f"alice_{uuid.uuid4().hex[:4]}@vertexerp.ai",
            },
        )
        assert create_res.status_code == 201
        emp_id = create_res.json()["id"]

        # Profile GET & PUT
        prof_res = await client.get(
            f"/api/v1/employee-profile/{emp_id}", headers=headers
        )
        assert prof_res.status_code == 200

        update_prof = await client.put(
            f"/api/v1/employee-profile/{emp_id}",
            headers=headers,
            json={
                "address": "100 Innovation Way",
                "city": "Austin",
                "state": "Texas",
                "country": "USA",
                "postal_code": "78701",
                "biography": "Senior Software Architect",
            },
        )
        assert update_prof.status_code == 200
        assert update_prof.json()["city"] == "Austin"

        # Documents CRUD
        doc_res = await client.post(
            "/api/v1/employee-documents",
            headers=headers,
            json={
                "employee_id": emp_id,
                "document_type": "Passport",
                "document_name": "US Passport",
                "document_number": "P12345678",
                "file_url": "https://storage.vertexerp.ai/docs/passport.pdf",
            },
        )
        assert doc_res.status_code == 201

        doc_list = await client.get(
            f"/api/v1/employee-documents?employee_id={emp_id}", headers=headers
        )
        assert doc_list.status_code == 200
        assert len(doc_list.json()) >= 1

        # Emergency Contacts CRUD
        contact_res = await client.post(
            "/api/v1/emergency-contacts",
            headers=headers,
            json={
                "employee_id": emp_id,
                "contact_name": "Robert Smith",
                "relationship": "Spouse",
                "phone": "+1-555-9988",
            },
        )
        assert contact_res.status_code == 201

        # Skills & Certifications
        skill_res = await client.post(
            "/api/v1/employee-skills",
            headers=headers,
            json={
                "employee_id": emp_id,
                "skill_name": "Python FastAPI",
                "proficiency": "expert",
                "years_of_experience": 5.5,
            },
        )
        assert skill_res.status_code == 201

        cert_res = await client.post(
            "/api/v1/employee-certifications",
            headers=headers,
            json={
                "employee_id": emp_id,
                "certification_name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "credential_id": "AWS-SA-98765",
            },
        )
        assert cert_res.status_code == 201

        # Duplicate certification validation
        dup_cert = await client.post(
            "/api/v1/employee-certifications",
            headers=headers,
            json={
                "employee_id": emp_id,
                "certification_name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
            },
        )
        assert dup_cert.status_code == 400
        assert "already exists" in dup_cert.json()["message"]

        # Asset assignment
        asset_code = f"MACBOOK_{uuid.uuid4().hex[:6].upper()}"
        asset_res = await client.post(
            "/api/v1/employee-assets",
            headers=headers,
            json={
                "employee_id": emp_id,
                "asset_name": "MacBook Pro M3 Max",
                "asset_code": asset_code,
                "asset_type": "Laptop",
            },
        )
        assert asset_res.status_code == 201

        # Timeline GET
        timeline_res = await client.get(
            f"/api/v1/employee-timeline/{emp_id}", headers=headers
        )
        assert timeline_res.status_code == 200
        assert len(timeline_res.json()) >= 1
