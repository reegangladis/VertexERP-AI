import csv
import io
import uuid
from typing import Any

from sqlalchemy import select

from app.models.crm_customer import Customer
from app.models.crm_deal import Deal
from app.models.crm_lead import Lead
from app.repositories.crm_mgmt import (
    ContactRepository,
    CustomerRepository,
    DealRepository,
    LeadActivityRepository,
    LeadRepository,
    LeadSourceRepository,
    OpportunityRepository,
    QuotationRepository,
)
from app.services.base import BaseService


class CRMServiceException(Exception):
    pass


class LeadService(BaseService[Lead, LeadRepository]):
    def __init__(
        self,
        repository: LeadRepository,
        source_repo: LeadSourceRepository,
        activity_repo: LeadActivityRepository,
    ):
        super().__init__(repository)
        self.source_repo = source_repo
        self.activity_repo = activity_repo

    async def create_lead(self, org_id: uuid.UUID, data: dict[str, Any]) -> Lead:
        email = data.get("email")

        # Deduplication check
        if email:
            stmt = select(Lead).where(
                Lead.organization_id == org_id,
                Lead.email == email,
                Lead.is_deleted == False,
            )
            res = await self.repository.db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                raise CRMServiceException(f"Lead with email {email} already exists.")

        # Compute AI lead scoring placeholder
        source_id = data.get("lead_source_id")
        score = 50  # Default middle score
        if source_id:
            source = await self.source_repo.get(source_id)
            if source:
                if source.code == "WEB":
                    score = 80
                elif source.code == "REFERRAL":
                    score = 95
                elif source.code == "COLD":
                    score = 25

        lead_data = {"organization_id": org_id, "score": score, **data}
        lead = await self.repository.create(lead_data)

        # Log initial activity
        await self.activity_repo.create(
            {
                "lead_id": lead.id,
                "type": "note",
                "title": "Lead Captured",
                "description": "Lead created from source channel.",
            }
        )

        return lead

    async def bulk_import_leads_csv(
        self, org_id: uuid.UUID, file_content: bytes
    ) -> int:
        stream = io.StringIO(file_content.decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            email = row.get("email")
            if not email:
                continue

            stmt = select(Lead).where(
                Lead.organization_id == org_id,
                Lead.email == email,
                Lead.is_deleted == False,
            )
            res = await self.repository.db.execute(stmt)
            if res.scalar_one_or_none():
                continue  # Skip duplicates

            lead_dict = {
                "organization_id": org_id,
                "first_name": row.get("first_name", "Unknown"),
                "last_name": row.get("last_name", "Lead"),
                "email": email,
                "phone": row.get("phone"),
                "company": row.get("company"),
                "status": row.get("status", "new"),
                "score": int(row.get("score", 50)),
            }
            await self.repository.create(lead_dict)
            count += 1
        return count

    async def convert_lead(
        self,
        lead_id: uuid.UUID,
        customer_repo: CustomerRepository,
        contact_repo: ContactRepository,
        opp_repo: OpportunityRepository,
        deal_repo: DealRepository,
        payload_data: dict[str, Any],
    ) -> dict[str, Any]:
        from datetime import date

        lead = await self.repository.get(lead_id)
        if not lead or lead.is_deleted:
            raise CRMServiceException("Lead not found.")

        if lead.status == "converted":
            raise CRMServiceException("Lead has already been converted.")

        company_name = (
            payload_data.get("customer_name")
            or lead.company
            or f"{lead.first_name} {lead.last_name}"
        )

        customer = await customer_repo.create(
            {
                "organization_id": lead.organization_id,
                "name": company_name,
                "type": "business" if lead.company else "individual",
                "status": "active",
            }
        )

        contact = await contact_repo.create(
            {
                "organization_id": lead.organization_id,
                "customer_id": customer.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "phone": lead.phone,
                "is_primary": True,
            }
        )

        deal = None
        opportunity = None
        if payload_data.get("create_opportunity", True):
            opp_title = (
                payload_data.get("opportunity_title")
                or f"Opportunity for {company_name}"
            )
            opportunity = await opp_repo.create(
                {
                    "organization_id": lead.organization_id,
                    "title": opp_title,
                    "stage": "qualification",
                    "close_date": date.today(),
                }
            )

            deal = await deal_repo.create(
                {
                    "organization_id": lead.organization_id,
                    "opportunity_id": opportunity.id,
                    "customer_id": customer.id,
                    "title": f"Deal - {company_name}",
                    "amount": payload_data.get("deal_amount", 0.0),
                    "probability": 20,
                    "status": "pipeline",
                }
            )

        lead.status = "converted"
        await self.repository.update(lead, {})

        return {
            "customer": customer,
            "contact": contact,
            "opportunity": opportunity,
            "deal": deal,
        }


class CustomerService(BaseService[Customer, CustomerRepository]):
    def __init__(self, repository: CustomerRepository, contact_repo: ContactRepository):
        super().__init__(repository)
        self.contact_repo = contact_repo

    async def create_customer(
        self, org_id: uuid.UUID, data: dict[str, Any]
    ) -> Customer:
        contacts_data = data.pop("contacts", [])
        cust_data = {"organization_id": org_id, **data}
        customer = await self.repository.create(cust_data)

        for c_data in contacts_data:
            await self.contact_repo.create(
                {"organization_id": org_id, "customer_id": customer.id, **c_data}
            )
        return customer

    async def bulk_import_customers_csv(
        self, org_id: uuid.UUID, file_content: bytes
    ) -> int:
        stream = io.StringIO(file_content.decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            name = row.get("name")
            if not name:
                continue

            cust_dict = {
                "organization_id": org_id,
                "name": name,
                "type": row.get("type", "business"),
                "industry": row.get("industry"),
                "status": row.get("status", "active"),
                "tags": (
                    {"list": row.get("tags", "").split(",")}
                    if row.get("tags")
                    else {"list": []}
                ),
            }
            await self.repository.create(cust_dict)
            count += 1
        return count


from app.models.crm_deal import SalesOrder
from app.repositories.crm_mgmt import SalesOrderRepository


class DealService(BaseService[Deal, DealRepository]):
    def __init__(self, repository: DealRepository, quotation_repo: QuotationRepository):
        super().__init__(repository)
        self.quotation_repo = quotation_repo

    async def process_deal_result(
        self, deal_id: uuid.UUID, status: str, reason: str | None
    ) -> Deal:
        deal = await self.repository.get(deal_id)
        if not deal:
            raise CRMServiceException("Deal not found.")

        deal.status = status
        deal.won_lost_reason = reason
        if status == "won":
            deal.probability = 100
        elif status == "lost":
            deal.probability = 0
        return await self.repository.update(deal, {})


class SalesOrderService(BaseService[SalesOrder, SalesOrderRepository]):
    def __init__(
        self, repository: SalesOrderRepository, quotation_repo: QuotationRepository
    ):
        super().__init__(repository)
        self.quotation_repo = quotation_repo

    async def convert_quotation_to_order(
        self, quotation_id: uuid.UUID, org_id: uuid.UUID
    ) -> SalesOrder:
        from datetime import date

        quotation = await self.quotation_repo.get(quotation_id)
        if not quotation or quotation.is_deleted:
            raise CRMServiceException("Quotation not found.")

        stmt = select(Deal).where(Deal.id == quotation.deal_id)
        res = await self.repository.db.execute(stmt)
        deal = res.scalar_one_or_none()
        if not deal:
            raise CRMServiceException("Associated deal not found.")

        order_number = (
            f"SO-{date.today().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        )
        sales_order = await self.repository.create(
            {
                "organization_id": org_id,
                "customer_id": deal.customer_id,
                "quotation_id": quotation.id,
                "order_number": order_number,
                "total_amount": quotation.total_amount or deal.amount,
                "status": "confirmed",
                "order_date": date.today(),
            }
        )

        quotation.status = "approved"
        await self.quotation_repo.update(quotation, {})

        deal.status = "won"
        deal.probability = 100
        await self.repository.db.commit()

        return sales_order
