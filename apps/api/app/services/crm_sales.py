import uuid
from datetime import UTC, date, datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.crm_sales import (
    CRMTaskRepository,
    CustomerAddressRepository,
    CustomerContactRepository,
    CustomerDocumentRepository,
    CustomerNoteRepository,
    CustomerRepository,
    CustomerTimelineRepository,
    LeadActivityRepository,
    LeadRepository,
    LeadSourceRepository,
    MeetingRepository,
    OpportunityRepository,
    QuotationItemRepository,
    QuotationRepository,
    SalesOrderItemRepository,
    SalesOrderRepository,
)
from app.schemas.crm_sales import (
    CRMTaskCreate,
    CRMTaskUpdate,
    CRMDashboardSummary,
    CustomerAddressCreate,
    CustomerContactCreate,
    CustomerCreate,
    CustomerUpdate,
    LeadActivityCreate,
    LeadAssignPayload,
    LeadConvertPayload,
    LeadCreate,
    LeadSourceCreate,
    LeadUpdate,
    MeetingCreate,
    MeetingUpdate,
    OpportunityCreate,
    OpportunityUpdate,
    QuotationCreate,
    QuotationUpdate,
    SalesOrderCreate,
    SalesOrderUpdate,
)


class LeadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.activity_repo = LeadActivityRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.contact_repo = CustomerContactRepository(db)
        self.opp_repo = OpportunityRepository(db)
        self.timeline_repo = CustomerTimelineRepository(db)

    async def create_lead(self, payload: LeadCreate):
        dup = await self.lead_repo.find_by_email(payload.organization_id, payload.email)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A lead with email '{payload.email}' already exists in this organization.",
            )
        lead = await self.lead_repo.create(payload.model_dump())

        # Log initial creation activity
        await self.activity_repo.create(
            {
                "lead_id": lead.id,
                "activity_type": "Creation",
                "description": f"Lead created for {lead.company_name} ({lead.contact_name}).",
                "performed_by": payload.assigned_to,
                "performed_at": datetime.now(UTC),
            }
        )

        return await self.lead_repo.get_with_activities(lead.id)

    async def update_lead(self, lead_id: uuid.UUID, payload: LeadUpdate):
        lead = await self.lead_repo.get(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        update_dict = payload.model_dump(exclude_unset=True)
        if "email" in update_dict:
            dup = await self.lead_repo.find_by_email(lead.organization_id, update_dict["email"])
            if dup and dup.id != lead_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A lead with email '{update_dict['email']}' already exists.",
                )
        updated = await self.lead_repo.update(lead_id, update_dict)
        return await self.lead_repo.get_with_activities(updated.id)

    async def assign_lead(self, lead_id: uuid.UUID, payload: LeadAssignPayload):
        lead = await self.lead_repo.get(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        updated = await self.lead_repo.update(lead_id, {"assigned_to": payload.assigned_to})

        await self.activity_repo.create(
            {
                "lead_id": lead.id,
                "activity_type": "Assignment",
                "description": f"Lead assigned to employee ID {payload.assigned_to}.",
                "performed_by": payload.assigned_to,
                "performed_at": datetime.now(UTC),
            }
        )
        return await self.lead_repo.get_with_activities(updated.id)

    async def convert_lead(self, lead_id: uuid.UUID, payload: LeadConvertPayload):
        lead = await self.lead_repo.get(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        if lead.status == "Converted":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lead is already converted.")

        code = payload.customer_code or f"CUST-{uuid.uuid4().hex[:6].upper()}"
        existing_cust = await self.customer_repo.find_by_code(lead.organization_id, code)
        if existing_cust:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Customer code '{code}' already exists.")

        # 1. Create Customer
        customer = await self.customer_repo.create(
            {
                "organization_id": lead.organization_id,
                "customer_code": code,
                "company_name": lead.company_name,
                "display_name": lead.company_name,
                "email": lead.email,
                "phone": lead.phone,
                "website": lead.website,
                "industry": lead.industry,
                "credit_limit": 50000.0,
                "payment_terms": "Net 30",
                "status": "Active",
            }
        )

        # 2. Create primary Contact
        names = lead.contact_name.split(" ", 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else "Contact"
        await self.contact_repo.create(
            {
                "customer_id": customer.id,
                "first_name": first_name,
                "last_name": last_name,
                "email": lead.email,
                "phone": lead.phone,
                "is_primary": True,
            }
        )

        # 3. Create Opportunity
        opp_title = payload.opportunity_title or f"Opportunity for {lead.company_name}"
        opp_revenue = payload.expected_revenue if payload.expected_revenue is not None else lead.expected_value
        opp = await self.opp_repo.create(
            {
                "customer_id": customer.id,
                "title": opp_title,
                "description": f"Converted from Lead #{lead.id}",
                "expected_revenue": opp_revenue,
                "probability": 50.0,
                "stage": "Qualification",
                "expected_close_date": date.today(),
                "assigned_to": lead.assigned_to,
                "status": "Open",
            }
        )

        # 4. Update Lead Status
        await self.lead_repo.update(lead_id, {"status": "Converted"})

        # 5. Log Timeline Event
        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Lead Converted",
                "title": f"Converted Lead {lead.company_name}",
                "description": f"Customer created ({code}) with Opportunity '{opp.title}' (${opp.expected_revenue:,.2f}).",
                "event_time": datetime.now(UTC),
                "performed_by": lead.assigned_to,
            }
        )

        return await self.customer_repo.get_with_details(customer.id)


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.contact_repo = CustomerContactRepository(db)
        self.address_repo = CustomerAddressRepository(db)
        self.timeline_repo = CustomerTimelineRepository(db)

    async def create_customer(self, payload: CustomerCreate):
        dup_code = await self.customer_repo.find_by_code(payload.organization_id, payload.customer_code)
        if dup_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer code '{payload.customer_code}' already exists.",
            )
        customer = await self.customer_repo.create(payload.model_dump())

        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Customer Created",
                "title": f"Customer Account Established: {customer.company_name}",
                "description": f"Code: {customer.customer_code}, Email: {customer.email}",
                "event_time": datetime.now(UTC),
            }
        )
        return await self.customer_repo.get_with_details(customer.id)

    async def add_contact(self, payload: CustomerContactCreate):
        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        contact = await self.contact_repo.create(payload.model_dump())

        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Contact Added",
                "title": f"New Contact Added: {contact.first_name} {contact.last_name}",
                "description": f"Email: {contact.email}, Designation: {contact.designation or 'N/A'}",
                "event_time": datetime.now(UTC),
            }
        )
        return contact

    async def add_address(self, payload: CustomerAddressCreate):
        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return await self.address_repo.create(payload.model_dump())


class OpportunityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.opp_repo = OpportunityRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.timeline_repo = CustomerTimelineRepository(db)

    async def create_opportunity(self, payload: OpportunityCreate):
        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        opp = await self.opp_repo.create(payload.model_dump())

        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Opportunity Created",
                "title": f"New Opportunity: {opp.title}",
                "description": f"Expected Revenue: ${opp.expected_revenue:,.2f}, Stage: {opp.stage}",
                "event_time": datetime.now(UTC),
                "performed_by": opp.assigned_to,
            }
        )
        return opp

    async def update_opportunity(self, opp_id: uuid.UUID, payload: OpportunityUpdate):
        opp = await self.opp_repo.get(opp_id)
        if not opp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

        update_dict = payload.model_dump(exclude_unset=True)
        old_stage = opp.stage
        updated = await self.opp_repo.update(opp_id, update_dict)

        if "stage" in update_dict and update_dict["stage"] != old_stage:
            await self.timeline_repo.create(
                {
                    "customer_id": opp.customer_id,
                    "event_type": "Opportunity Stage Update",
                    "title": f"Opportunity Moved to {updated.stage}",
                    "description": f"'{opp.title}' moved from {old_stage} to {updated.stage}.",
                    "event_time": datetime.now(UTC),
                    "performed_by": updated.assigned_to,
                }
            )
        return updated


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quotation_repo = QuotationRepository(db)
        self.item_repo = QuotationItemRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.timeline_repo = CustomerTimelineRepository(db)

    async def create_quotation(self, payload: QuotationCreate):
        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        dup = await self.quotation_repo.find_by_number(payload.quotation_number)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quotation number '{payload.quotation_number}' already exists.",
            )

        if payload.quotation_date > payload.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quotation date cannot be after valid_until date.",
            )

        subtotal = 0.0
        tax = 0.0
        calculated_items = []
        for item in payload.items:
            item_subtotal = item.quantity * item.unit_price
            item_total = item_subtotal + item.tax_amount
            subtotal += item_subtotal
            tax += item.tax_amount
            calculated_items.append(
                {
                    "item_name": item.item_name,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item_subtotal,
                    "tax_amount": item.tax_amount,
                    "total_price": item_total,
                }
            )

        grand_total = max(0.0, (subtotal + tax) - payload.discount)

        quotation = await self.quotation_repo.create(
            {
                "customer_id": payload.customer_id,
                "quotation_number": payload.quotation_number,
                "quotation_date": payload.quotation_date,
                "valid_until": payload.valid_until,
                "subtotal": subtotal,
                "tax": tax,
                "discount": payload.discount,
                "grand_total": grand_total,
                "status": payload.status,
            }
        )

        for calc_item in calculated_items:
            calc_item["quotation_id"] = quotation.id
            await self.item_repo.create(calc_item)

        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Quotation Generated",
                "title": f"Quotation {quotation.quotation_number} Issued",
                "description": f"Grand Total: ${grand_total:,.2f}, Valid Until: {quotation.valid_until}",
                "event_time": datetime.now(UTC),
            }
        )

        return await self.quotation_repo.get_with_items(quotation.id)

    async def generate_pdf_text(self, q_number: str) -> str:
        q = await self.quotation_repo.find_by_number(q_number)
        if not q:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        full_q = await self.quotation_repo.get_with_items(q.id)

        lines = [
            "============================================================",
            "                   VERTEXERP AI CRM & SALES                 ",
            "                      OFFICIAL QUOTATION                    ",
            "============================================================",
            f"Quotation Number : {full_q.quotation_number}",
            f"Date             : {full_q.quotation_date}",
            f"Valid Until      : {full_q.valid_until}",
            f"Customer ID      : {full_q.customer_id}",
            f"Status           : {full_q.status}",
            "------------------------------------------------------------",
            "ITEMS:",
        ]
        for idx, item in enumerate(full_q.items, 1):
            lines.append(
                f" {idx}. {item.item_name} x {item.quantity} @ ${item.unit_price:,.2f} = ${item.total_price:,.2f}"
            )
        lines.extend(
            [
                "------------------------------------------------------------",
                f"Subtotal         : ${full_q.subtotal:,.2f}",
                f"Tax Amount       : ${full_q.tax:,.2f}",
                f"Discount         : ${full_q.discount:,.2f}",
                f"GRAND TOTAL      : ${full_q.grand_total:,.2f}",
                "============================================================",
            ]
        )
        return "\n".join(lines)


class SalesOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = SalesOrderRepository(db)
        self.item_repo = SalesOrderItemRepository(db)
        self.quotation_repo = QuotationRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.timeline_repo = CustomerTimelineRepository(db)

    async def create_sales_order(self, payload: SalesOrderCreate):
        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        dup = await self.order_repo.find_by_number(payload.sales_order_number)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sales order number '{payload.sales_order_number}' already exists.",
            )

        subtotal = 0.0
        tax = 0.0
        calculated_items = []
        for item in payload.items:
            item_subtotal = item.quantity * item.unit_price
            item_total = item_subtotal + item.tax_amount
            subtotal += item_subtotal
            tax += item.tax_amount
            calculated_items.append(
                {
                    "item_name": item.item_name,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item_subtotal,
                    "tax_amount": item.tax_amount,
                    "total_price": item_total,
                }
            )

        grand_total = max(0.0, (subtotal + tax) - payload.discount)

        order = await self.order_repo.create(
            {
                "customer_id": payload.customer_id,
                "quotation_id": payload.quotation_id,
                "sales_order_number": payload.sales_order_number,
                "order_date": payload.order_date,
                "status": payload.status,
                "subtotal": subtotal,
                "tax": tax,
                "discount": payload.discount,
                "grand_total": grand_total,
            }
        )

        for calc_item in calculated_items:
            calc_item["sales_order_id"] = order.id
            await self.item_repo.create(calc_item)

        await self.timeline_repo.create(
            {
                "customer_id": customer.id,
                "event_type": "Sales Order Placed",
                "title": f"Sales Order {order.sales_order_number} Confirmed",
                "description": f"Grand Total: ${grand_total:,.2f}, Order Date: {order.order_date}",
                "event_time": datetime.now(UTC),
            }
        )

        return await self.order_repo.get_with_items(order.id)


class CRMAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.opp_repo = OpportunityRepository(db)
        self.quotation_repo = QuotationRepository(db)
        self.order_repo = SalesOrderRepository(db)
        self.task_repo = CRMTaskRepository(db)
        self.meeting_repo = MeetingRepository(db)

    async def get_dashboard_summary(
        self, org_id: uuid.UUID, customer_id: uuid.UUID | None = None
    ) -> CRMDashboardSummary:
        leads = await self.lead_repo.get_by_org(org_id)
        total_leads = len(leads)
        qualified_leads = len([l for l in leads if l.status in ("Qualified", "Converted")])

        customers, _ = await self.customer_repo.get_multi(filters={"organization_id": org_id})
        total_customers = len(customers)

        opps = await self.opp_repo.get_all()
        if customer_id:
            opps = [o for o in opps if o.customer_id == customer_id]
        open_opps = [o for o in opps if o.status == "Open"]
        pipeline_val = sum(o.expected_revenue for o in open_opps)

        orders = await self.order_repo.get_all()
        if customer_id:
            orders = [ord for ord in orders if ord.customer_id == customer_id]
        sales_rev = sum(ord.grand_total for ord in orders if ord.status != "Cancelled")

        quotations = await self.quotation_repo.get_all()
        if customer_id:
            quotations = [q for q in quotations if q.customer_id == customer_id]
        pending_qs = len([q for q in quotations if q.status in ("Draft", "Sent")])

        meetings = await self.meeting_repo.get_all()
        tasks = await self.task_repo.get_all()

        return CRMDashboardSummary(
            total_leads=total_leads,
            qualified_leads=qualified_leads,
            total_customers=total_customers,
            open_opportunities=len(open_opps),
            pipeline_value=round(pipeline_val, 2),
            sales_revenue=round(sales_rev, 2),
            pending_quotations=pending_qs,
            total_sales_orders=len(orders),
            meetings_today=len(meetings),
            tasks_due=len(tasks),
        )
