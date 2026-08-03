import uuid
from datetime import date, datetime
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, status

from app.models.crm_sales_v10 import (
    CRMTask,
    Customer,
    CustomerContact,
    Lead,
    LeadActivity,
    LeadSource,
    Meeting,
    Opportunity,
    Quotation,
    QuotationItem,
    SalesOrder,
)
from app.services.crm_sales import (
    CRMAnalyticsService,
    CustomerService,
    LeadService,
    OpportunityService,
    QuotationService,
    SalesOrderService,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_lead_creation_and_duplicate_validation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = LeadService(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.crm_sales import LeadCreate
    payload = LeadCreate(
        organization_id=org_id,
        company_name="Acme Corporation",
        contact_name="John Doe",
        email="john.doe@acme.com",
        phone="+1-555-0199",
        industry="Technology",
        expected_value=75000.0,
    )

    lead_obj = Lead(
        id=uuid.uuid4(),
        organization_id=org_id,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        email=payload.email,
        phone=payload.phone,
        status="New",
        activities=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
        create_mock_execute_result(lead_obj, []),
    ]
    lead = await service.create_lead(payload)
    assert lead is not None
    assert lead.email == "john.doe@acme.com"

    # Duplicate check
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(lead_obj)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_lead(payload)
    assert exc_info.value.status_code == 400
    assert "already exists in this organization" in exc_info.value.detail


@pytest.mark.asyncio
async def test_lead_conversion_to_customer_and_opportunity(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = LeadService(mock_db_session)
    org_id = uuid.uuid4()
    lead_id = uuid.uuid4()

    lead_obj = Lead(
        id=lead_id,
        organization_id=org_id,
        company_name="Nexus Technologies",
        contact_name="Alice Smith",
        email="alice@nexus.io",
        phone="+1-555-0200",
        expected_value=120000.0,
        status="Qualified",
        assigned_to=uuid.uuid4(),
    )

    customer_obj = Customer(
        id=uuid.uuid4(),
        organization_id=org_id,
        customer_code="CUST-NX100",
        company_name="Nexus Technologies",
        display_name="Nexus Technologies",
        email="alice@nexus.io",
        status="Active",
        contacts=[],
        addresses=[],
        opportunities=[],
        quotations=[],
        sales_orders=[],
    )

    from app.schemas.crm_sales import LeadConvertPayload
    payload = LeadConvertPayload(
        customer_code="CUST-NX100",
        opportunity_title="Nexus Enterprise ERP License Deal",
        expected_revenue=120000.0,
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(lead_obj),
        create_mock_execute_result(None),  # Duplicate customer code check
        create_mock_execute_result(lead_obj),  # update lead status get check
        create_mock_execute_result(customer_obj),  # get_with_details
    ]

    customer = await service.convert_lead(lead_id, payload)
    assert customer is not None
    assert customer.customer_code == "CUST-NX100"


@pytest.mark.asyncio
async def test_quotation_creation_and_pdf_generation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    q_service = QuotationService(mock_db_session)
    cust_id = uuid.uuid4()

    from app.schemas.crm_sales import QuotationCreate, QuotationItemCreate
    payload = QuotationCreate(
        customer_id=cust_id,
        quotation_number="QT-2026-0001",
        quotation_date=date(2026, 8, 1),
        valid_until=date(2026, 8, 31),
        discount=500.0,
        items=[
            QuotationItemCreate(
                item_name="VertexERP Cloud Subscription",
                quantity=10.0,
                unit_price=500.0,
                tax_amount=250.0,
            )
        ],
    )

    cust_obj = Customer(id=cust_id, organization_id=uuid.uuid4(), company_name="Test Cust", customer_code="C1", email="c1@test.com")
    q_obj = Quotation(
        id=uuid.uuid4(),
        customer_id=cust_id,
        quotation_number="QT-2026-0001",
        quotation_date=payload.quotation_date,
        valid_until=payload.valid_until,
        subtotal=5000.0,
        tax=250.0,
        discount=500.0,
        grand_total=4750.0,
        status="Draft",
    )
    q_item = QuotationItem(
        id=uuid.uuid4(),
        quotation_id=q_obj.id,
        item_name="VertexERP Cloud Subscription",
        quantity=10.0,
        unit_price=500.0,
        subtotal=5000.0,
        tax_amount=250.0,
        total_price=5250.0,
    )
    q_obj.items = [q_item]

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(cust_obj),
        create_mock_execute_result(None),  # duplicate check
        create_mock_execute_result(q_obj),
    ]
    quotation = await q_service.create_quotation(payload)
    assert quotation is not None
    assert quotation.quotation_number == "QT-2026-0001"

    # PDF Text Generation test
    mock_db_session.execute.side_effect = [
        create_mock_execute_result(q_obj),
        create_mock_execute_result(q_obj, [q_item]),
    ]
    pdf_text = await q_service.generate_pdf_text("QT-2026-0001")
    assert "VERTEXERP AI CRM & SALES" in pdf_text
    assert "QT-2026-0001" in pdf_text


@pytest.mark.asyncio
async def test_sales_order_creation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = SalesOrderService(mock_db_session)
    cust_id = uuid.uuid4()

    from app.schemas.crm_sales import SalesOrderCreate, SalesOrderItemCreate
    payload = SalesOrderCreate(
        customer_id=cust_id,
        sales_order_number="SO-2026-0010",
        order_date=date(2026, 8, 1),
        discount=100.0,
        items=[
            SalesOrderItemCreate(
                item_name="Enterprise CRM Implementation Service",
                quantity=1.0,
                unit_price=10000.0,
                tax_amount=500.0,
            )
        ],
    )

    cust_obj = Customer(id=cust_id, organization_id=uuid.uuid4(), company_name="Test Cust", customer_code="C2", email="c2@test.com")
    so_obj = SalesOrder(
        id=uuid.uuid4(),
        customer_id=cust_id,
        sales_order_number="SO-2026-0010",
        order_date=payload.order_date,
        subtotal=10000.0,
        tax=500.0,
        discount=100.0,
        grand_total=10400.0,
        status="Pending",
        items=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(cust_obj),
        create_mock_execute_result(None),
        create_mock_execute_result(so_obj),
    ]
    so = await service.create_sales_order(payload)
    assert so is not None
    assert so.sales_order_number == "SO-2026-0010"


@pytest.mark.asyncio
async def test_crm_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = CRMAnalyticsService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_leads == 0
    assert summary.total_customers == 0
    assert summary.pipeline_value == 0.0
