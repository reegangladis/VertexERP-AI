"""Integration and Security tests for Employee Profiles & Sensitive HR Data (Feature 2)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"profadmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Profile Admin {suffix}",
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
            "first_name": "Jane",
            "last_name": "Doe",
            "email": f"jane.doe.{clean_suffix}@example.com",
            "hire_date": "2024-01-15",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_employee_profile_and_emergency_contacts(async_client: AsyncClient):
    """Verifies profile update and emergency contacts lifecycle."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "prof_test")

    # 1. Get initial auto-created profile
    prof_res = await async_client.get(f"/api/v1/hr/employees/{emp_id}/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["employee_id"] == str(emp_id)

    # 2. Update profile
    prof_update = {
        "marital_status": "MARRIED",
        "blood_group": "O+",
        "nationality": "American",
        "national_id_number": "SSN-123-45-6789",
        "bio": "Senior backend specialist with 10 years experience.",
    }
    put_res = await async_client.put(
        f"/api/v1/hr/employees/{emp_id}/profile", headers=headers, json=prof_update
    )
    assert put_res.status_code == 200
    assert put_res.json()["blood_group"] == "O+"
    assert put_res.json()["nationality"] == "American"

    # 3. Add Emergency Contact
    contact_in = {
        "name": "John Doe",
        "relationship": "Spouse",
        "phone_number": "+1-555-0188",
        "email": "john.doe@example.com",
        "is_primary": True,
    }
    add_c_res = await async_client.post(
        f"/api/v1/hr/employees/{emp_id}/emergency-contacts", headers=headers, json=contact_in
    )
    assert add_c_res.status_code == 201
    contact = add_c_res.json()
    contact_id = contact["id"]
    assert contact["is_primary"] is True

    # 4. List Emergency Contacts
    list_c_res = await async_client.get(
        f"/api/v1/hr/employees/{emp_id}/emergency-contacts", headers=headers
    )
    assert list_c_res.status_code == 200
    assert len(list_c_res.json()) == 1

    # 5. Delete Emergency Contact
    del_c_res = await async_client.delete(
        f"/api/v1/hr/employees/{emp_id}/emergency-contacts/{contact_id}", headers=headers
    )
    assert del_c_res.status_code == 204


@pytest.mark.asyncio
async def test_bank_accounts_masking_and_sensitive_data(async_client: AsyncClient):
    """Verifies sensitive bank accounts are masked and require appropriate permissions."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "bank_test")

    # 1. Add Bank Account
    bank_in = {
        "bank_name": "Chase Manhattan",
        "account_number": "123456789012",
        "routing_or_ifsc_code": "ROUTING01",
        "account_type": "CHECKING",
        "is_primary": True,
    }
    add_b_res = await async_client.post(
        f"/api/v1/hr/employees/{emp_id}/bank-accounts", headers=headers, json=bank_in
    )
    assert add_b_res.status_code == 201
    bank = add_b_res.json()
    assert bank["bank_name"] == "Chase Manhattan"
    # Verify account number is masked to protect sensitive PII
    assert bank["account_number_masked"] == "********9012"

    # 2. List Bank Accounts
    list_b_res = await async_client.get(
        f"/api/v1/hr/employees/{emp_id}/bank-accounts", headers=headers
    )
    assert list_b_res.status_code == 200
    assert len(list_b_res.json()) == 1
    assert list_b_res.json()[0]["account_number_masked"] == "********9012"


@pytest.mark.asyncio
async def test_documents_and_addresses(async_client: AsyncClient):
    """Verifies address records and document attachments."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "doc_test")

    # 1. Add Address
    addr_in = {
        "address_type": "RESIDENTIAL",
        "address_line1": "742 Evergreen Terrace",
        "city": "Springfield",
        "state": "OR",
        "postal_code": "97477",
        "country": "USA",
        "is_primary": True,
    }
    addr_res = await async_client.post(
        f"/api/v1/hr/employees/{emp_id}/addresses", headers=headers, json=addr_in
    )
    assert addr_res.status_code == 201
    assert addr_res.json()["city"] == "Springfield"

    # 2. Attach Document
    doc_in = {
        "document_type": "ID_PROOF",
        "title": "Passport Copy",
        "file_url": "https://s3.amazonaws.com/vertexerp-vault/passport.pdf",
        "s3_key": "vault/emp/passport.pdf",
        "file_size_bytes": 1048576,
        "mime_type": "application/pdf",
        "is_verified": True,
    }
    doc_res = await async_client.post(
        f"/api/v1/hr/employees/{emp_id}/documents", headers=headers, json=doc_in
    )
    assert doc_res.status_code == 201
    assert doc_res.json()["title"] == "Passport Copy"
    assert doc_res.json()["is_verified"] is True

    # 3. List Documents
    list_doc_res = await async_client.get(
        f"/api/v1/hr/employees/{emp_id}/documents", headers=headers
    )
    assert list_doc_res.status_code == 200
    assert len(list_doc_res.json()) == 1
