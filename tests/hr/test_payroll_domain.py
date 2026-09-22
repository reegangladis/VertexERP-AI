"""Integration and Transaction Safety tests for Payroll Domain (Feature 6)."""

import uuid

import pytest
from httpx import AsyncClient


async def create_tenant_and_employee(
    client: AsyncClient, suffix: str
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID, uuid.UUID]:
    """Helper to register a tenant, create an employee, and return headers, tenant_id, org_id, and emp_id."""
    clean_suffix = suffix.replace("_", "-")
    reg_payload = {
        "email": f"payrolladmin_{clean_suffix}@test.com",
        "password": "AdminPassword123!",
        "full_name": f"Payroll Admin {suffix}",
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
            "first_name": "Michael",
            "last_name": "Scott",
            "email": f"michael.scott.{clean_suffix}@example.com",
            "hire_date": "2024-01-01",
        },
    )
    assert emp_res.status_code == 201
    emp_id = uuid.UUID(emp_res.json()["id"])
    return headers, tenant_id, org_id, emp_id


@pytest.mark.asyncio
async def test_salary_components_and_structures(async_client: AsyncClient):
    """Verifies Salary Component and Structure creation, duplicate detection, and listing."""
    headers, _, _, _ = await create_tenant_and_employee(async_client, "comp_struct")

    # 1. Create Basic Salary Component (EARNING)
    comp_basic = {
        "code": "BASIC_PAY",
        "name": "Basic Pay",
        "component_type": "EARNING",
        "calculation_type": "FIXED",
        "is_taxable": True,
    }
    res_b = await async_client.post(
        "/api/v1/hr/payroll/components", headers=headers, json=comp_basic
    )
    assert res_b.status_code == 201
    basic_id = res_b.json()["id"]

    # 2. Create Housing Allowance (EARNING)
    comp_hra = {
        "code": "HRA",
        "name": "House Rent Allowance",
        "component_type": "EARNING",
        "calculation_type": "PERCENTAGE",
        "is_taxable": True,
    }
    res_h = await async_client.post("/api/v1/hr/payroll/components", headers=headers, json=comp_hra)
    assert res_h.status_code == 201
    hra_id = res_h.json()["id"]

    # 3. Create Income Tax (DEDUCTION)
    comp_tax = {
        "code": "INC_TAX",
        "name": "Income Tax",
        "component_type": "DEDUCTION",
        "calculation_type": "PERCENTAGE",
        "is_taxable": False,
    }
    res_t = await async_client.post("/api/v1/hr/payroll/components", headers=headers, json=comp_tax)
    assert res_t.status_code == 201
    tax_id = res_t.json()["id"]

    # 4. Create Salary Structure Template
    struct_in = {
        "code": "STANDARD_EXEC",
        "name": "Standard Executive Compensation",
        "description": "Base salary template for executives",
        "items": [
            {
                "component_id": basic_id,
                "calculation_type": "PERCENTAGE",
                "amount_or_percentage": 50.0,
            },
            {
                "component_id": hra_id,
                "calculation_type": "PERCENTAGE",
                "amount_or_percentage": 30.0,
            },
            {
                "component_id": tax_id,
                "calculation_type": "PERCENTAGE",
                "amount_or_percentage": 10.0,
            },
        ],
    }
    res_s = await async_client.post(
        "/api/v1/hr/payroll/structures", headers=headers, json=struct_in
    )
    assert res_s.status_code == 201
    struct = res_s.json()
    assert struct["code"] == "STANDARD_EXEC"
    assert len(struct["items"]) == 3

    # Duplicate structure code returns 409
    dup_s = await async_client.post(
        "/api/v1/hr/payroll/structures", headers=headers, json=struct_in
    )
    assert dup_s.status_code == 409


@pytest.mark.asyncio
async def test_payroll_run_lifecycle_and_payslips(async_client: AsyncClient):
    """Verifies end-to-end atomic gross-to-net payroll run, payslips, approval, and disbursement."""
    headers, _, _, emp_id = await create_tenant_and_employee(async_client, "run_lifecycle")

    # 1. Setup Components
    res_b = await async_client.post(
        "/api/v1/hr/payroll/components",
        headers=headers,
        json={
            "code": "BASIC_PAY",
            "name": "Basic Pay",
            "component_type": "EARNING",
            "calculation_type": "PERCENTAGE",
        },
    )
    basic_id = res_b.json()["id"]

    res_h = await async_client.post(
        "/api/v1/hr/payroll/components",
        headers=headers,
        json={
            "code": "HRA",
            "name": "HRA",
            "component_type": "EARNING",
            "calculation_type": "PERCENTAGE",
        },
    )
    hra_id = res_h.json()["id"]

    res_t = await async_client.post(
        "/api/v1/hr/payroll/components",
        headers=headers,
        json={
            "code": "TAX",
            "name": "Income Tax",
            "component_type": "DEDUCTION",
            "calculation_type": "PERCENTAGE",
        },
    )
    tax_id = res_t.json()["id"]

    # 2. Setup Structure
    struct_res = await async_client.post(
        "/api/v1/hr/payroll/structures",
        headers=headers,
        json={
            "code": "MGR_STRUCT",
            "name": "Manager Salary Structure",
            "items": [
                {
                    "component_id": basic_id,
                    "calculation_type": "PERCENTAGE",
                    "amount_or_percentage": 60.0,
                },
                {
                    "component_id": hra_id,
                    "calculation_type": "PERCENTAGE",
                    "amount_or_percentage": 40.0,
                },
                {
                    "component_id": tax_id,
                    "calculation_type": "PERCENTAGE",
                    "amount_or_percentage": 10.0,
                },
            ],
        },
    )
    struct_id = struct_res.json()["id"]

    # 3. Assign to Employee (Gross Salary = 10,000 USD)
    assign_in = {
        "employee_id": str(emp_id),
        "salary_structure_id": struct_id,
        "base_gross_salary": 10000.0,
        "currency": "USD",
        "effective_from": "2024-01-01",
    }
    assign_res = await async_client.post(
        "/api/v1/hr/payroll/assignments", headers=headers, json=assign_in
    )
    assert assign_res.status_code == 201

    # 4. Create Draft Payroll Run
    run_in = {
        "pay_period_start": "2024-05-01",
        "pay_period_end": "2024-05-31",
        "pay_date": "2024-06-01",
        "payment_method": "DIRECT_DEPOSIT",
    }
    run_res = await async_client.post("/api/v1/hr/payroll/runs", headers=headers, json=run_in)
    assert run_res.status_code == 201
    run = run_res.json()
    run_id = run["id"]
    assert run["status"] == "DRAFT"

    # 5. Process Payroll Run (Gross-to-Net Engine)
    process_res = await async_client.post(
        f"/api/v1/hr/payroll/runs/{run_id}/process", headers=headers
    )
    assert process_res.status_code == 200
    calc_run = process_res.json()
    assert calc_run["status"] == "CALCULATED"
    assert calc_run["total_employees"] == 1
    assert calc_run["total_gross"] == 10000.0
    assert calc_run["total_deductions"] == 1000.0  # 10% of 10,000
    assert calc_run["total_net"] == 9000.0

    # 6. Verify Payslip & Line Item Breakdown
    payslips_res = await async_client.get(
        f"/api/v1/hr/payroll/payslips/run/{run_id}", headers=headers
    )
    assert payslips_res.status_code == 200
    payslips = payslips_res.json()
    assert len(payslips) == 1
    ps = payslips[0]
    assert ps["gross_pay"] == 10000.0
    assert ps["net_pay"] == 9000.0
    assert ps["deductions"] == 1000.0
    assert ps["basic_pay"] == 6000.0
    assert ps["allowances"] == 4000.0

    # Detailed payslip lines
    detail_res = await async_client.get(f"/api/v1/hr/payroll/payslips/{ps['id']}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["lines"]) == 3

    # 7. Approve Payroll Run
    approve_res = await async_client.put(
        f"/api/v1/hr/payroll/runs/{run_id}/approve",
        headers=headers,
        json={"status": "APPROVED", "remarks": "May 2024 Payroll verified and approved."},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 8. Disburse Payroll Run
    disburse_res = await async_client.post(
        f"/api/v1/hr/payroll/runs/{run_id}/disburse", headers=headers
    )
    assert disburse_res.status_code == 200
    assert disburse_res.json()["status"] == "DISBURSED"

    # Payslip should now be PAID
    ps_paid_res = await async_client.get(f"/api/v1/hr/payroll/payslips/{ps['id']}", headers=headers)
    assert ps_paid_res.json()["status"] == "PAID"
    assert ps_paid_res.json()["transaction_reference"] is not None
