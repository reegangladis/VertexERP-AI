"""CRM domain business service managing leads, pipelines, deals, quotations, and orders."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.crm.models.contact import Contact
from app.modules.crm.models.customer import Customer
from app.modules.crm.models.deal import Deal, DealStageHistory
from app.modules.crm.models.lead import Lead
from app.modules.crm.models.quotation import Quotation, QuotationItem
from app.modules.crm.models.sales_order import SalesOrder, SalesOrderItem
from app.modules.crm.repositories.crm_repository import CRMRepository


class CRMService:
    """Service handling CRM domain workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CRMRepository(session)

    # --------------------------------------------------------------------------
    # Lead Management & Conversion
    # --------------------------------------------------------------------------
    async def create_lead(
        self,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        first_name: str,
        last_name: str,
        email: str,
        company_name: str | None = None,
        phone: str | None = None,
        title: str | None = None,
        source: str = "WEBSITE",
        estimated_value: Decimal = Decimal("0.00"),
        owner_id: uuid.UUID | None = None,
    ) -> Lead:
        """Captures a new sales lead."""
        if not email or "@" not in email:
            raise ValidationException("Valid email address is required for Lead creation.")

        lead = Lead(
            tenant_id=tenant_id,
            organization_id=organization_id,
            owner_id=owner_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            company_name=company_name.strip() if company_name else None,
            email=email.strip().lower(),
            phone=phone.strip() if phone else None,
            title=title.strip() if title else None,
            source=source.upper(),
            status="NEW",
            rating="WARM",
            estimated_value=estimated_value,
        )
        return await self.repo.create_lead(lead)

    async def qualify_and_convert_lead(
        self,
        lead_id: uuid.UUID,
        tenant_id: uuid.UUID,
        pipeline_id: uuid.UUID,
        initial_stage_id: uuid.UUID,
        deal_title: str | None = None,
        deal_value: Decimal | None = None,
        user_id: uuid.UUID | None = None,
    ) -> tuple[Customer, Contact, Deal]:
        """
        Qualifies and converts a Lead into a Customer Account, Contact, and Opportunity Deal.
        """
        lead = await self.repo.get_lead_by_id(lead_id, tenant_id)
        if not lead:
            raise NotFoundException(f"Lead with id '{lead_id}' not found.")

        if lead.status == "CONVERTED":
            raise ValidationException(f"Lead '{lead.email}' is already converted.")

        # 1. Create Customer
        customer_name = lead.company_name or f"{lead.first_name} {lead.last_name}"
        customer = Customer(
            tenant_id=tenant_id,
            organization_id=lead.organization_id,
            owner_id=lead.owner_id or user_id,
            name=customer_name,
            customer_type="BUSINESS" if lead.company_name else "INDIVIDUAL",
            industry="General",
            email=lead.email,
            phone=lead.phone,
            status="ACTIVE",
        )
        customer = await self.repo.create_customer(customer)

        # 2. Create Primary Contact
        contact = Contact(
            tenant_id=tenant_id,
            organization_id=lead.organization_id,
            customer_id=customer.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            title=lead.title,
            is_primary=True,
        )
        contact = await self.repo.create_contact(contact)

        # 3. Create Deal Opportunity
        title = deal_title or f"Opportunity - {customer_name}"
        value = deal_value if deal_value is not None else lead.estimated_value
        deal = Deal(
            tenant_id=tenant_id,
            organization_id=lead.organization_id,
            customer_id=customer.id,
            contact_id=contact.id,
            pipeline_id=pipeline_id,
            stage_id=initial_stage_id,
            owner_id=lead.owner_id or user_id,
            title=title,
            value=value,
            currency="USD",
            win_probability_pct=Decimal("20.00"),
            status="OPEN",
        )
        deal = await self.repo.create_deal(deal)

        # Record stage history
        history = DealStageHistory(
            tenant_id=tenant_id,
            organization_id=lead.organization_id,
            deal_id=deal.id,
            from_stage_id=None,
            to_stage_id=initial_stage_id,
            changed_by_user_id=user_id,
            notes="Lead converted to Opportunity Deal",
        )
        await self.repo.record_stage_history(history)

        # Update lead status
        lead.status = "CONVERTED"
        lead.converted_customer_id = customer.id
        lead.converted_contact_id = contact.id
        lead.converted_deal_id = deal.id
        lead.converted_at = datetime.now(UTC)
        await self.session.flush()

        return customer, contact, deal

    # --------------------------------------------------------------------------
    # Deal Stage Progression
    # --------------------------------------------------------------------------
    async def transition_deal_stage(
        self,
        deal_id: uuid.UUID,
        tenant_id: uuid.UUID,
        to_stage_id: uuid.UUID,
        win_probability_pct: Decimal | None = None,
        notes: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> Deal:
        """Transitions a deal to a new pipeline stage and creates an audit record."""
        deal = await self.repo.get_deal_by_id(deal_id, tenant_id)
        if not deal:
            raise NotFoundException(f"Deal '{deal_id}' not found.")

        from_stage_id = deal.stage_id
        deal.stage_id = to_stage_id
        if win_probability_pct is not None:
            deal.win_probability_pct = win_probability_pct

        history = DealStageHistory(
            tenant_id=tenant_id,
            organization_id=deal.organization_id,
            deal_id=deal.id,
            from_stage_id=from_stage_id,
            to_stage_id=to_stage_id,
            changed_by_user_id=user_id,
            notes=notes,
        )
        await self.repo.record_stage_history(history)
        await self.session.flush()
        return deal

    # --------------------------------------------------------------------------
    # Quotations & Sales Orders
    # --------------------------------------------------------------------------
    async def create_quotation(
        self,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        customer_id: uuid.UUID,
        quotation_number: str,
        valid_until: date,
        items: list[dict[str, Any]],
        deal_id: uuid.UUID | None = None,
        contact_id: uuid.UUID | None = None,
        owner_id: uuid.UUID | None = None,
        currency: str = "USD",
    ) -> Quotation:
        """Issues a formal CRM sales quotation with computed line totals and taxes."""
        if not items:
            raise ValidationException("Quotation must include at least one line item.")

        subtotal = Decimal("0.00")
        tax_amount = Decimal("0.00")
        quotation_items: list[QuotationItem] = []

        for idx, it in enumerate(items):
            qty = Decimal(str(it.get("quantity", 1)))
            price = Decimal(str(it.get("unit_price", 0)))
            disc_pct = Decimal(str(it.get("discount_pct", 0)))
            tax_pct = Decimal(str(it.get("tax_pct", 0)))

            line_gross = qty * price
            line_disc = line_gross * (disc_pct / Decimal("100"))
            line_net = line_gross - line_disc
            line_tax = line_net * (tax_pct / Decimal("100"))
            line_total = line_net + line_tax

            subtotal += line_net
            tax_amount += line_tax

            quotation_items.append(
                QuotationItem(
                    tenant_id=tenant_id,
                    organization_id=organization_id,
                    item_type=it.get("item_type", "PRODUCT"),
                    item_code=it.get("item_code"),
                    description=it.get("description", "Quoted Item"),
                    quantity=qty,
                    unit_price=price,
                    discount_pct=disc_pct,
                    tax_pct=tax_pct,
                    line_total=line_total,
                    sort_order=idx,
                )
            )

        grand_total = subtotal + tax_amount

        quotation = Quotation(
            tenant_id=tenant_id,
            organization_id=organization_id,
            customer_id=customer_id,
            deal_id=deal_id,
            contact_id=contact_id,
            owner_id=owner_id,
            quotation_number=quotation_number,
            quotation_date=date.today(),
            valid_until=valid_until,
            status="DRAFT",
            currency=currency,
            subtotal=subtotal,
            discount_amount=Decimal("0.00"),
            tax_amount=tax_amount,
            grand_total=grand_total,
            items=quotation_items,
        )
        return await self.repo.create_quotation(quotation)

    async def convert_quotation_to_sales_order(
        self,
        quotation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        order_number: str,
        user_id: uuid.UUID | None = None,
    ) -> SalesOrder:
        """Converts an accepted Quotation into a binding SalesOrder."""
        quotation = await self.repo.get_quotation_by_id(quotation_id, tenant_id)
        if not quotation:
            raise NotFoundException(f"Quotation '{quotation_id}' not found.")

        order_items = [
            SalesOrderItem(
                tenant_id=tenant_id,
                organization_id=quotation.organization_id,
                item_code=qi.item_code,
                description=qi.description,
                quantity=qi.quantity,
                unit_price=qi.unit_price,
                discount_pct=qi.discount_pct,
                tax_pct=qi.tax_pct,
                line_total=qi.line_total,
                sort_order=qi.sort_order,
            )
            for qi in quotation.items
        ]

        sales_order = SalesOrder(
            tenant_id=tenant_id,
            organization_id=quotation.organization_id,
            customer_id=quotation.customer_id,
            contact_id=quotation.contact_id,
            deal_id=quotation.deal_id,
            quotation_id=quotation.id,
            owner_id=quotation.owner_id or user_id,
            order_number=order_number,
            order_date=date.today(),
            status="CONFIRMED",
            currency=quotation.currency,
            subtotal=quotation.subtotal,
            discount_amount=quotation.discount_amount,
            tax_amount=quotation.tax_amount,
            grand_total=quotation.grand_total,
            items=order_items,
        )
        sales_order = await self.repo.create_sales_order(sales_order)

        quotation.status = "CONVERTED"
        await self.session.flush()

        return sales_order
