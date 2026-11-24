"""CRM API Router registering Leads, Deals, Customers, Contacts, Quotations, Orders, Activities, and Dashboard Metrics."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.crm.models.activity import Activity, Task
from app.modules.crm.models.contact import Contact
from app.modules.crm.models.customer import Customer
from app.modules.crm.models.deal import Deal
from app.modules.crm.models.pipeline import Pipeline, PipelineStage
from app.modules.crm.services.crm_service import CRMService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/crm", tags=["CRM"])


# ------------------------------------------------------------------------------
# 1. Leads Endpoints
# ------------------------------------------------------------------------------
@router.post(
    "/leads",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_WRITE.value))],
)
async def create_lead(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Capture a new sales lead."""
    service = CRMService(db)
    lead = await service.create_lead(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        email=payload.get("email", ""),
        company_name=payload.get("company_name"),
        phone=payload.get("phone"),
        title=payload.get("title"),
        source=payload.get("source", "WEBSITE"),
        status=payload.get("status", "NEW"),
        rating=payload.get("rating", "WARM"),
        estimated_value=Decimal(str(payload.get("estimated_value", "0.00"))),
    )
    return {
        "id": str(lead.id),
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "status": lead.status,
        "company_name": lead.company_name,
        "phone": lead.phone,
        "source": lead.source,
        "rating": lead.rating,
        "estimated_value": float(lead.estimated_value),
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


@router.get(
    "/leads",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_READ.value))],
)
async def list_leads(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all leads for the tenant."""
    service = CRMService(db)
    leads = await service.repo.list_leads(tenant_id=tenant_id)
    return [
        {
            "id": str(l.id),
            "first_name": l.first_name,
            "last_name": l.last_name,
            "email": l.email,
            "status": l.status,
            "company_name": l.company_name,
            "phone": l.phone,
            "title": l.title,
            "source": l.source,
            "rating": l.rating,
            "estimated_value": float(l.estimated_value),
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in leads
    ]


@router.get(
    "/leads/{lead_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_READ.value))],
)
async def get_lead(
    lead_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve lead detail by ID."""
    service = CRMService(db)
    lead = await service.repo.get_lead_by_id(lead_id, tenant_id)
    if not lead:
        raise NotFoundException(f"Lead '{lead_id}' not found.")
    return {
        "id": str(lead.id),
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "status": lead.status,
        "company_name": lead.company_name,
        "phone": lead.phone,
        "title": lead.title,
        "source": lead.source,
        "rating": lead.rating,
        "estimated_value": float(lead.estimated_value),
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


@router.put(
    "/leads/{lead_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_WRITE.value))],
)
async def update_lead(
    lead_id: uuid.UUID,
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update lead information or qualification status."""
    service = CRMService(db)
    lead = await service.repo.get_lead_by_id(lead_id, tenant_id)
    if not lead:
        raise NotFoundException(f"Lead '{lead_id}' not found.")

    if "first_name" in payload:
        lead.first_name = payload["first_name"]
    if "last_name" in payload:
        lead.last_name = payload["last_name"]
    if "company_name" in payload:
        lead.company_name = payload["company_name"]
    if "phone" in payload:
        lead.phone = payload["phone"]
    if "status" in payload:
        lead.status = payload["status"]
    if "rating" in payload:
        lead.rating = payload["rating"]
    if "estimated_value" in payload:
        lead.estimated_value = Decimal(str(payload["estimated_value"]))

    await db.flush()
    return {
        "id": str(lead.id),
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "status": lead.status,
        "company_name": lead.company_name,
        "phone": lead.phone,
        "rating": lead.rating,
        "estimated_value": float(lead.estimated_value),
    }


@router.post(
    "/leads/{lead_id}/convert",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_CONVERT.value))],
)
async def convert_lead(
    lead_id: uuid.UUID,
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Convert a qualified lead into Customer (Account), Contact, and Opportunity Deal."""
    service = CRMService(db)
    pipeline_id = uuid.UUID(str(payload.get("pipeline_id", uuid.uuid4())))
    initial_stage_id = uuid.UUID(str(payload.get("initial_stage_id", uuid.uuid4())))
    deal_title = payload.get("deal_title")
    deal_value = Decimal(str(payload["deal_value"])) if "deal_value" in payload else None

    customer, contact, deal = await service.qualify_and_convert_lead(
        lead_id=lead_id,
        tenant_id=tenant_id,
        pipeline_id=pipeline_id,
        initial_stage_id=initial_stage_id,
        deal_title=deal_title,
        deal_value=deal_value,
        user_id=user_id,
    )
    return {
        "customer": {"id": str(customer.id), "name": customer.name, "email": customer.email},
        "contact": {"id": str(contact.id), "name": f"{contact.first_name} {contact.last_name}"},
        "deal": {"id": str(deal.id), "title": deal.title, "value": float(deal.value)},
    }


# ------------------------------------------------------------------------------
# 2. Customers (Accounts) Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/customers",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_CUSTOMERS_READ.value))],
)
async def list_customers(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List customer corporate accounts."""
    service = CRMService(db)
    customers = await service.repo.list_customers(tenant_id=tenant_id)
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "customer_type": c.customer_type,
            "industry": c.industry,
            "website": c.website,
            "phone": c.phone,
            "email": c.email,
            "credit_limit": float(c.credit_limit),
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in customers
    ]


@router.post(
    "/customers",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_CUSTOMERS_WRITE.value))],
)
async def create_customer(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new corporate customer account."""
    service = CRMService(db)
    customer = Customer(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        name=payload["name"],
        customer_type=payload.get("customer_type", "CORPORATE"),
        industry=payload.get("industry", "General"),
        website=payload.get("website"),
        phone=payload.get("phone"),
        email=payload.get("email"),
        status=payload.get("status", "ACTIVE"),
        credit_limit=Decimal(str(payload.get("credit_limit", "0.00"))),
    )
    customer = await service.repo.create_customer(customer)
    return {"id": str(customer.id), "name": customer.name, "status": customer.status}


# ------------------------------------------------------------------------------
# 3. Contacts Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/contacts",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_CONTACTS_READ.value))],
)
async def list_contacts(
    customer_id: uuid.UUID | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List business contacts with optional customer filtering."""
    service = CRMService(db)
    contacts = await service.repo.list_contacts(tenant_id=tenant_id, customer_id=customer_id)
    return [
        {
            "id": str(c.id),
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone": c.phone,
            "title": c.title,
            "department": c.department,
            "customer_id": str(c.customer_id) if c.customer_id else None,
            "is_primary": c.is_primary,
        }
        for c in contacts
    ]


@router.post(
    "/contacts",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_CONTACTS_WRITE.value))],
)
async def create_contact(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new contact associated with a customer account."""
    service = CRMService(db)
    contact = Contact(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        customer_id=uuid.UUID(str(payload["customer_id"])),
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload.get("email"),
        phone=payload.get("phone"),
        title=payload.get("title"),
        is_primary=payload.get("is_primary", False),
    )
    contact = await service.repo.create_contact(contact)
    return {"id": str(contact.id), "name": f"{contact.first_name} {contact.last_name}"}


def _safe_uuid(val: Any, default: uuid.UUID | None = None) -> uuid.UUID:
    if not val:
        return default or uuid.uuid4()
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError, AttributeError):
        return default or uuid.uuid4()


# ------------------------------------------------------------------------------
# 4. Deals (Opportunities) & Kanban Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/deals",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_DEALS_READ.value))],
)
async def list_deals(
    pipeline_id: uuid.UUID | None = Query(None),
    stage_id: uuid.UUID | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List opportunities for Kanban pipeline or table view."""
    service = CRMService(db)
    deals = await service.repo.list_deals(tenant_id=tenant_id, pipeline_id=pipeline_id, stage_id=stage_id)
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "value": float(d.value),
            "currency": d.currency,
            "stage_id": str(d.stage_id),
            "pipeline_id": str(d.pipeline_id),
            "customer_id": str(d.customer_id),
            "win_probability_pct": float(d.win_probability_pct),
            "status": d.status,
            "expected_close_date": d.expected_close_date.isoformat() if d.expected_close_date else None,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in deals
    ]


@router.post(
    "/deals",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_DEALS_WRITE.value))],
)
async def create_deal(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new sales opportunity deal."""
    service = CRMService(db)
    deal = Deal(
        tenant_id=tenant_id,
        organization_id=_safe_uuid(payload.get("organization_id"), org_id),
        customer_id=_safe_uuid(payload["customer_id"]),
        pipeline_id=_safe_uuid(payload.get("pipeline_id")),
        stage_id=_safe_uuid(payload.get("stage_id")),
        owner_id=user_id,
        title=payload["title"],
        value=Decimal(str(payload.get("value", "0.00"))),
        currency=payload.get("currency", "USD"),
        win_probability_pct=Decimal(str(payload.get("win_probability_pct", "20.00"))),
        status="OPEN",
    )
    deal = await service.repo.create_deal(deal)
    return {"id": str(deal.id), "title": deal.title, "value": float(deal.value), "status": deal.status}


@router.put(
    "/deals/{deal_id}/stage",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_DEALS_WRITE.value))],
)
async def update_deal_stage(
    deal_id: uuid.UUID,
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Transition deal to a new stage (Kanban card move)."""
    service = CRMService(db)
    to_stage_id = _safe_uuid(payload.get("stage_id"))
    win_pct = Decimal(str(payload["win_probability_pct"])) if "win_probability_pct" in payload else None
    notes = payload.get("notes")

    deal = await service.transition_deal_stage(
        deal_id=deal_id,
        tenant_id=tenant_id,
        to_stage_id=to_stage_id,
        win_probability_pct=win_pct,
        notes=notes,
        user_id=user_id,
    )
    return {"id": str(deal.id), "stage_id": str(deal.stage_id), "status": deal.status}


# ------------------------------------------------------------------------------
# 5. Quotations & Sales Orders Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/quotations",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_QUOTATIONS_READ.value))],
)
async def list_quotations(
    customer_id: uuid.UUID | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List quotations."""
    service = CRMService(db)
    quotes = await service.repo.list_quotations(tenant_id=tenant_id, customer_id=customer_id)
    return [
        {
            "id": str(q.id),
            "quotation_number": q.quotation_number,
            "customer_id": str(q.customer_id),
            "status": q.status,
            "subtotal": float(q.subtotal),
            "tax_amount": float(q.tax_amount),
            "grand_total": float(q.grand_total),
            "valid_until": q.valid_until.isoformat() if q.valid_until else None,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in quotes
    ]


@router.post(
    "/quotations",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_QUOTATIONS_WRITE.value))],
)
async def create_quotation(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Issue sales quotation with Decimal pricing, line items, and tax."""
    service = CRMService(db)
    quote = await service.create_quotation(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        customer_id=uuid.UUID(str(payload["customer_id"])),
        quotation_number=payload.get("quotation_number", f"QT-{uuid.uuid4().hex[:8].upper()}"),
        valid_until=date.fromisoformat(payload.get("valid_until", date.today().isoformat())),
        items=payload.get("items", []),
        deal_id=uuid.UUID(str(payload["deal_id"])) if "deal_id" in payload else None,
        owner_id=user_id,
    )
    return {
        "id": str(quote.id),
        "quotation_number": quote.quotation_number,
        "grand_total": float(quote.grand_total),
        "status": quote.status,
    }


@router.post(
    "/quotations/{quotation_id}/convert-order",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_QUOTATIONS_CONVERT.value))],
)
async def convert_quotation_to_order(
    quotation_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Convert approved quotation into a confirmed sales order."""
    service = CRMService(db)
    order = await service.convert_quotation_to_sales_order(
        quotation_id=quotation_id,
        tenant_id=tenant_id,
        order_number=f"SO-{uuid.uuid4().hex[:8].upper()}",
        user_id=user_id,
    )
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "grand_total": float(order.grand_total),
        "status": order.status,
    }


@router.get(
    "/orders",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_ORDERS_READ.value))],
)
async def list_sales_orders(
    customer_id: uuid.UUID | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List sales orders."""
    service = CRMService(db)
    orders = await service.repo.list_sales_orders(tenant_id=tenant_id, customer_id=customer_id)
    return [
        {
            "id": str(o.id),
            "order_number": o.order_number,
            "customer_id": str(o.customer_id),
            "status": o.status,
            "grand_total": float(o.grand_total),
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


# ------------------------------------------------------------------------------
# 6. Activities & Tasks Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/activities",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_ACTIVITIES_READ.value))],
)
async def list_activities(
    entity_type: str | None = Query(None),
    entity_id: uuid.UUID | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List calls, meetings, follow-ups, and interaction timeline events."""
    service = CRMService(db)
    acts = await service.repo.list_activities(tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id)
    return [
        {
            "id": str(a.id),
            "activity_type": a.activity_type,
            "title": a.title,
            "description": a.description,
            "status": a.status,
            "priority": a.priority,
            "scheduled_start": a.scheduled_start.isoformat() if a.scheduled_start else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in acts
    ]


@router.post(
    "/activities",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_ACTIVITIES_WRITE.value))],
)
async def create_activity(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Log an interaction activity or follow-up."""
    service = CRMService(db)
    act = Activity(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        activity_type=payload.get("activity_type", "CALL"),
        title=payload["title"],
        description=payload.get("description"),
        entity_type=payload.get("entity_type", "LEAD"),
        entity_id=uuid.UUID(str(payload.get("entity_id", uuid.uuid4()))),
        owner_id=user_id,
        status="PLANNED",
    )
    act = await service.repo.create_activity(act)
    return {"id": str(act.id), "title": act.title, "activity_type": act.activity_type}


# ------------------------------------------------------------------------------
# 7. Salesforce-Inspired CRM Dashboard Metrics
# ------------------------------------------------------------------------------
@router.get(
    "/dashboard/metrics",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_READ.value))],
)
async def get_crm_metrics(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Returns database-backed aggregate metrics for CRM dashboards."""
    service = CRMService(db)
    return await service.repo.get_crm_metrics(tenant_id)
