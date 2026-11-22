"""CRM domain comprehensive test suite covering leads, deals, pipelines, quotes, and orders."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.crm.models.pipeline import Pipeline, PipelineStage
from app.modules.crm.services.crm_service import CRMService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def crm_context(db_session):
    """Sets up a tenant, organization, and default sales pipeline for CRM tests."""
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

    pipeline = Pipeline(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        name="Enterprise Direct Sales",
        is_default=True,
    )
    db_session.add(pipeline)

    stage_discovery = PipelineStage(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipeline.id,
        name="Discovery",
        stage_type="OPEN",
        probability_pct=Decimal("20.00"),
        stage_order=1,
    )
    stage_proposal = PipelineStage(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipeline.id,
        name="Proposal Sent",
        stage_type="OPEN",
        probability_pct=Decimal("50.00"),
        stage_order=2,
    )
    stage_closed_won = PipelineStage(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipeline.id,
        name="Closed Won",
        stage_type="WON",
        probability_pct=Decimal("100.00"),
        stage_order=3,
    )
    db_session.add_all([stage_discovery, stage_proposal, stage_closed_won])
    await db_session.commit()

    return {
        "tenant": tenant,
        "org": org,
        "pipeline": pipeline,
        "stage_discovery": stage_discovery,
        "stage_proposal": stage_proposal,
        "stage_closed_won": stage_closed_won,
    }


@pytest.mark.asyncio
async def test_crm_lead_capture_and_validation(db_session, crm_context):
    """Verify lead capture enforces validation on email formatting and stores metadata."""
    service = CRMService(db_session)
    t = crm_context["tenant"]
    o = crm_context["org"]

    # 1. Successful lead creation
    lead = await service.create_lead(
        tenant_id=t.id,
        organization_id=o.id,
        first_name="Sarah",
        last_name="Connor",
        email="sconnor@cyberdyne.com",
        company_name="Cyberdyne Systems",
        phone="+1-555-0199",
        title="VP of Procurement",
        source="EVENT",
        estimated_value=Decimal("75000.00"),
    )
    assert lead.id is not None
    assert lead.status == "NEW"
    assert lead.estimated_value == Decimal("75000.00")
    assert lead.company_name == "Cyberdyne Systems"

    # 2. Validation failure on invalid email
    with pytest.raises(ValidationException, match="Valid email address is required"):
        await service.create_lead(
            tenant_id=t.id,
            organization_id=o.id,
            first_name="Bad",
            last_name="Email",
            email="not-an-email",
        )


@pytest.mark.asyncio
async def test_crm_lead_qualification_and_conversion_pipeline(db_session, crm_context):
    """Verify lead converts into Customer, Contact, Deal, and sets up stage history."""
    service = CRMService(db_session)
    t = crm_context["tenant"]
    o = crm_context["org"]
    p = crm_context["pipeline"]
    s_disc = crm_context["stage_discovery"]

    lead = await service.create_lead(
        tenant_id=t.id,
        organization_id=o.id,
        first_name="Alexander",
        last_name="Pierce",
        email="apierce@triskelion.gov",
        company_name="Insight Dynamics",
        estimated_value=Decimal("250000.00"),
    )

    # Convert Lead
    customer, contact, deal = await service.qualify_and_convert_lead(
        lead_id=lead.id,
        tenant_id=t.id,
        pipeline_id=p.id,
        initial_stage_id=s_disc.id,
        deal_title="Insight Enterprise Infrastructure",
    )

    assert customer.id is not None
    assert customer.name == "Insight Dynamics"
    assert contact.customer_id == customer.id
    assert contact.first_name == "Alexander"
    assert deal.customer_id == customer.id
    assert deal.value == Decimal("250000.00")
    assert deal.stage_id == s_disc.id
    assert lead.status == "CONVERTED"

    # Converting already converted lead must fail
    with pytest.raises(ValidationException, match="already converted"):
        await service.qualify_and_convert_lead(
            lead_id=lead.id,
            tenant_id=t.id,
            pipeline_id=p.id,
            initial_stage_id=s_disc.id,
        )


@pytest.mark.asyncio
async def test_crm_deal_stage_progression(db_session, crm_context):
    """Verify opportunity stage transitions, win probability updates, and audit trail."""
    service = CRMService(db_session)
    t = crm_context["tenant"]
    o = crm_context["org"]
    p = crm_context["pipeline"]
    s_disc = crm_context["stage_discovery"]
    s_prop = crm_context["stage_proposal"]
    s_won = crm_context["stage_closed_won"]

    lead = await service.create_lead(
        tenant_id=t.id,
        organization_id=o.id,
        first_name="Miles",
        last_name="Dyson",
        email="mdyson@skynet-research.org",
        estimated_value=Decimal("120000.00"),
    )
    _, _, deal = await service.qualify_and_convert_lead(
        lead_id=lead.id,
        tenant_id=t.id,
        pipeline_id=p.id,
        initial_stage_id=s_disc.id,
    )

    # Transition 1: Discovery -> Proposal
    updated_deal = await service.transition_deal_stage(
        deal_id=deal.id,
        tenant_id=t.id,
        to_stage_id=s_prop.id,
        win_probability_pct=Decimal("50.00"),
        notes="Executive presentation completed successfully",
    )
    assert updated_deal.stage_id == s_prop.id
    assert updated_deal.win_probability_pct == Decimal("50.00")

    # Transition 2: Proposal -> Closed Won
    final_deal = await service.transition_deal_stage(
        deal_id=deal.id,
        tenant_id=t.id,
        to_stage_id=s_won.id,
        win_probability_pct=Decimal("100.00"),
        notes="Master services agreement signed",
    )
    assert final_deal.stage_id == s_won.id
    assert final_deal.win_probability_pct == Decimal("100.00")


@pytest.mark.asyncio
async def test_crm_quotation_and_order_conversion(db_session, crm_context):
    """Verify formal quotation generation with multi-line taxes/discounts and conversion to SalesOrder."""
    service = CRMService(db_session)
    t = crm_context["tenant"]
    o = crm_context["org"]
    p = crm_context["pipeline"]
    s_disc = crm_context["stage_discovery"]

    lead = await service.create_lead(
        tenant_id=t.id,
        organization_id=o.id,
        first_name="Bruce",
        last_name="Wayne",
        email="bruce@wayneenterprises.com",
        company_name="Wayne Enterprises",
    )
    customer, contact, deal = await service.qualify_and_convert_lead(
        lead_id=lead.id,
        tenant_id=t.id,
        pipeline_id=p.id,
        initial_stage_id=s_disc.id,
    )

    # Issue quotation with 2 items: 1 product with 10% tax, 1 service with 5% discount
    items = [
        {
            "item_code": "PROD-TI-ARMOR",
            "description": "Tactical Titanium Plating",
            "quantity": 10,
            "unit_price": 5000.00,
            "discount_pct": 0,
            "tax_pct": 10.00,
        },
        {
            "item_code": "SRV-CALIB",
            "description": "On-Site Systems Calibration",
            "quantity": 2,
            "unit_price": 2500.00,
            "discount_pct": 5.00,
            "tax_pct": 0,
        },
    ]

    quote = await service.create_quotation(
        tenant_id=t.id,
        organization_id=o.id,
        customer_id=customer.id,
        deal_id=deal.id,
        contact_id=contact.id,
        quotation_number="QT-2026-0099",
        valid_until=date.today() + timedelta(days=30),
        items=items,
    )

    assert quote.id is not None
    assert len(quote.items) == 2
    # Item 1: 10 * 5000 = 50000 net + 5000 tax = 55000
    # Item 2: 2 * 2500 = 5000 gross - 250 disc = 4750 net + 0 tax = 4750
    # Subtotal: 50000 + 4750 = 54750.00, Tax: 5000.00, Grand Total: 59750.00
    assert quote.subtotal == Decimal("54750.00")
    assert quote.tax_amount == Decimal("5000.00")
    assert quote.grand_total == Decimal("59750.00")
    assert quote.status == "DRAFT"

    # Convert Quotation to Confirmed SalesOrder
    order = await service.convert_quotation_to_sales_order(
        quotation_id=quote.id,
        tenant_id=t.id,
        order_number="SO-2026-0044",
    )
    assert order.id is not None
    assert order.status == "CONFIRMED"
    assert order.grand_total == Decimal("59750.00")
    assert len(order.items) == 2
    assert quote.status == "CONVERTED"


@pytest.mark.asyncio
async def test_crm_multi_tenant_isolation(db_session, crm_context):
    """Verify strict tenant isolation: Tenant B cannot read or modify Tenant A CRM entities."""
    service = CRMService(db_session)
    t_a = crm_context["tenant"]
    o_a = crm_context["org"]
    p_a = crm_context["pipeline"]
    s_a = crm_context["stage_discovery"]

    # Create Lead for Tenant A
    lead_a = await service.create_lead(
        tenant_id=t_a.id,
        organization_id=o_a.id,
        first_name="TenantA",
        last_name="User",
        email="lead_a@isolated.io",
    )

    # Tenant B tries to query or convert Tenant A's lead
    tenant_b_id = uuid.uuid4()
    lead_as_b = await service.repo.get_lead_by_id(lead_a.id, tenant_id=tenant_b_id)
    assert lead_as_b is None, "Tenant B must not see Tenant A lead"

    with pytest.raises(NotFoundException):
        await service.qualify_and_convert_lead(
            lead_id=lead_a.id,
            tenant_id=tenant_b_id,
            pipeline_id=p_a.id,
            initial_stage_id=s_a.id,
        )
