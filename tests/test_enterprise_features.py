"""Comprehensive verification test suite for VertexERP AI Enterprise Transformation.

Tests:
1. CRM Domain (Leads, Customers, Contacts, Deals, Stage Transitions, Quotations, Orders, Metrics)
2. Centralized Workflow & Approvals (Inbox, Stats, Actions)
3. Vertex AI Center Predictive & Intelligence (Lead Scoring, Attrition, Sales Forecast, Resume Match)
"""

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.user import User
from app.modules.identity.services.jwt_service import JwtService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def enterprise_context(db_session: AsyncSession):
    """Sets up a tenant, organization, and authenticated administrator user in the DB."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Apex Industrial Holdings",
        slug=f"apex-{uuid.uuid4().hex[:6]}",
        is_active=True,
    )
    db_session.add(tenant)

    org = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Apex Commercial Sales",
        legal_name="Apex Commercial Sales Corp",
        tax_identifier="US-EIN-9928172",
        is_active=True,
    )
    db_session.add(org)

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        default_organization_id=org.id,
        email=f"admin_{uuid.uuid4().hex[:6]}@vertexerp.com",
        full_name="Enterprise Administrator",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    token, _, _ = JwtService.create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        organization_id=org.id,
        roles=["TenantAdmin"],
    )
    headers = {"Authorization": f"Bearer {token}"}
    return {"tenant": tenant, "org": org, "user": user, "headers": headers}


@pytest.mark.asyncio
async def test_crm_leads_crud_and_metrics(async_client: AsyncClient, enterprise_context: dict):
    """Verifies CRM leads management and dashboard KPI aggregation."""
    headers = enterprise_context["headers"]

    # 1. Create a Lead
    lead_payload = {
        "first_name": "Tony",
        "last_name": "Stark",
        "email": f"tony_{uuid.uuid4().hex[:6]}@starkindustries.com",
        "company_name": "Stark Industries",
        "source": "DIRECT",
        "status": "QUALIFIED",
        "rating": "HOT",
        "estimated_value": 250000,
    }
    create_res = await async_client.post("/api/v1/crm/leads", json=lead_payload, headers=headers)
    assert create_res.status_code == 201
    lead_data = create_res.json()
    assert lead_data["first_name"] == "Tony"
    assert lead_data["rating"] == "HOT"
    lead_id = lead_data["id"]

    # 2. List Leads
    list_res = await async_client.get("/api/v1/crm/leads", headers=headers)
    assert list_res.status_code == 200
    leads = list_res.json()
    assert any(l["id"] == lead_id for l in leads)

    # 3. CRM Dashboard Metrics
    metrics_res = await async_client.get("/api/v1/crm/dashboard/metrics", headers=headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert "leads_total" in metrics
    assert "pipeline_value" in metrics
    assert "conversion_rate_pct" in metrics


@pytest.mark.asyncio
async def test_crm_customers_and_deals(async_client: AsyncClient, enterprise_context: dict):
    """Verifies customer accounts and deal pipeline progression."""
    headers = enterprise_context["headers"]

    # 1. Create Customer Account
    cust_payload = {
        "name": f"Wayne Enterprises {uuid.uuid4().hex[:6]}",
        "customer_type": "CORPORATE",
        "industry": "Defense & Technology",
        "email": f"bruce_{uuid.uuid4().hex[:6]}@waynecorp.com",
        "credit_limit": 500000,
        "status": "ACTIVE",
    }
    cust_res = await async_client.post("/api/v1/crm/customers", json=cust_payload, headers=headers)
    assert cust_res.status_code == 201
    cust_data = cust_res.json()
    cust_id = cust_data["id"]

    # 2. Create Deal / Opportunity
    stage_uuid = str(uuid.uuid4())
    deal_payload = {
        "title": "Bat-Suit High-Strength Composites",
        "value": 150000,
        "currency": "USD",
        "stage_id": stage_uuid,
        "customer_id": cust_id,
        "win_probability_pct": 60,
    }
    deal_res = await async_client.post("/api/v1/crm/deals", json=deal_payload, headers=headers)
    assert deal_res.status_code == 201
    deal_data = deal_res.json()
    deal_id = deal_data["id"]

    # 3. Advance Deal Stage
    next_stage_uuid = str(uuid.uuid4())
    stage_update = {
        "stage_id": next_stage_uuid,
        "win_probability_pct": 100,
    }
    update_res = await async_client.put(f"/api/v1/crm/deals/{deal_id}/stage", json=stage_update, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["stage_id"] == next_stage_uuid


@pytest.mark.asyncio
async def test_workflow_approvals_inbox_and_stats(async_client: AsyncClient, enterprise_context: dict):
    """Verifies centralized workflow inbox and stats."""
    headers = enterprise_context["headers"]

    # 1. Fetch Workflow Stats
    stats_res = await async_client.get("/api/v1/workflows/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "pending_total" in stats
    assert "pending_leaves" in stats
    assert "pending_regularizations" in stats

    # 2. Fetch Inbox
    inbox_res = await async_client.get("/api/v1/workflows/inbox", headers=headers)
    assert inbox_res.status_code == 200
    assert isinstance(inbox_res.json(), list)


@pytest.mark.asyncio
async def test_ai_predictive_lead_scoring(async_client: AsyncClient, enterprise_context: dict):
    """Verifies ML Lead Scoring algorithm returns calibrated scores and feature weights."""
    headers = enterprise_context["headers"]

    payload = {
        "industry": "Technology",
        "company_size": 350,
        "estimated_budget": 85000.0,
        "lead_source": "DIRECT",
        "interaction_count": 6,
        "decision_maker_identified": True,
    }
    res = await async_client.post("/api/v1/ai/predict/lead-score", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data["score"] <= 100
    assert data["rating"] in ["HOT", "WARM", "COLD"]
    assert "key_factors" in data
    assert len(data["key_factors"]) >= 2
    assert "recommended_action" in data


@pytest.mark.asyncio
async def test_ai_predictive_attrition_risk(async_client: AsyncClient, enterprise_context: dict):
    """Verifies employee attrition predictor returns risk assessment and retention strategies."""
    headers = enterprise_context["headers"]

    payload = {
        "tenure_months": 36,
        "monthly_overtime_hours": 22.5,
        "months_since_last_promotion": 40,
        "satisfaction_survey_score": 2.1,
        "compensation_ratio_to_market": 0.8,
        "leaves_taken_last_quarter": 5,
    }
    res = await async_client.post("/api/v1/ai/predict/attrition-risk", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0 <= data["risk_score"] <= 100
    assert len(data["risk_drivers"]) >= 1
    assert len(data["retention_strategies"]) >= 1


@pytest.mark.asyncio
async def test_ai_predictive_sales_forecast(async_client: AsyncClient, enterprise_context: dict):
    """Verifies 6-month predictive revenue projection API."""
    headers = enterprise_context["headers"]

    res = await async_client.get("/api/v1/ai/predict/sales-forecast", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_projected_6m"] > 0
    assert len(data["monthly_projections"]) == 6
    for slice_item in data["monthly_projections"]:
        assert slice_item["pipeline_projected"] > 0
        assert slice_item["optimistic_scenario"] >= slice_item["pipeline_projected"]
        assert slice_item["conservative_scenario"] <= slice_item["pipeline_projected"]


@pytest.mark.asyncio
async def test_ai_resume_intelligence_match(async_client: AsyncClient, enterprise_context: dict):
    """Verifies NLP resume extraction and candidate fit matching."""
    headers = enterprise_context["headers"]

    payload = {
        "resume_text": """
        Jane Foster - Senior Cloud Systems Engineer with 8 years of experience building
        distributed applications in Python, FastAPI, Docker, and PostgreSQL.
        Extensive experience with Kubernetes, AWS, and CI/CD pipelines.
        Education: Master of Science in Computer Science.
        """,
        "target_role": "Senior Cloud Infrastructure Engineer",
        "required_skills": ["Python", "Docker", "PostgreSQL", "Kubernetes"],
        "min_years_experience": 5,
    }
    res = await async_client.post("/api/v1/ai/predict/resume/match", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["match_score_pct"] >= 70
    assert "Python" in data["matching_skills"]
    assert "Docker" in data["matching_skills"]
    assert "ai_verdict" in data
