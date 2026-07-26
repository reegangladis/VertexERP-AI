import uuid
import csv
import io
from typing import List, Optional, Any, Dict
from sqlalchemy import select, and_
from app.services.base import BaseService
from app.repositories.crm_mgmt import (
    LeadSourceRepository,
    LeadRepository,
    LeadActivityRepository,
    CustomerRepository,
    ContactRepository,
    CustomerNoteRepository,
    CustomerDocumentRepository,
    OpportunityRepository,
    DealRepository,
    QuotationRepository,
    CRMTaskRepository,
    MeetingRepository,
    SupportTicketRepository,
    CampaignRepository,
)
from app.models.crm_lead import Lead, LeadSource, LeadActivity
from app.models.crm_customer import Customer, Contact, CustomerNote, CustomerDocument
from app.models.crm_deal import Opportunity, Deal, Quotation
from app.models.crm_activity import CRMTask, Meeting
from app.models.crm_ticket import SupportTicket
from app.models.crm_campaign import Campaign

class CRMServiceException(Exception):
    pass

class LeadService(BaseService[Lead, LeadRepository]):
    def __init__(self, repository: LeadRepository, source_repo: LeadSourceRepository, activity_repo: LeadActivityRepository):
        super().__init__(repository)
        self.source_repo = source_repo
        self.activity_repo = activity_repo

    async def create_lead(self, org_id: uuid.UUID, data: Dict[str, Any]) -> Lead:
        email = data.get("email")
        
        # Deduplication check
        if email:
            stmt = select(Lead).where(
                Lead.organization_id == org_id,
                Lead.email == email,
                Lead.is_deleted == False
            )
            res = await self.repository.db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                raise CRMServiceException(f"Lead with email {email} already exists.")

        # Compute AI lead scoring placeholder
        source_id = data.get("lead_source_id")
        score = 50 # Default middle score
        if source_id:
            source = await self.source_repo.get(source_id)
            if source:
                if source.code == "WEB":
                    score = 80
                elif source.code == "REFERRAL":
                    score = 95
                elif source.code == "COLD":
                    score = 25
        
        lead_data = {
            "organization_id": org_id,
            "score": score,
            **data
        }
        lead = await self.repository.create(lead_data)

        # Log initial activity
        await self.activity_repo.create({
            "lead_id": lead.id,
            "type": "note",
            "title": "Lead Captured",
            "description": f"Lead created from source channel."
        })

        return lead

    async def bulk_import_leads_csv(self, org_id: uuid.UUID, file_content: bytes) -> int:
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
                Lead.is_deleted == False
            )
            res = await self.repository.db.execute(stmt)
            if res.scalar_one_or_none():
                continue # Skip duplicates

            lead_dict = {
                "organization_id": org_id,
                "first_name": row.get("first_name", "Unknown"),
                "last_name": row.get("last_name", "Lead"),
                "email": email,
                "phone": row.get("phone"),
                "company": row.get("company"),
                "status": row.get("status", "new"),
                "score": int(row.get("score", 50))
            }
            await self.repository.create(lead_dict)
            count += 1
        return count


class CustomerService(BaseService[Customer, CustomerRepository]):
    def __init__(self, repository: CustomerRepository, contact_repo: ContactRepository):
        super().__init__(repository)
        self.contact_repo = contact_repo

    async def create_customer(self, org_id: uuid.UUID, data: Dict[str, Any]) -> Customer:
        contacts_data = data.pop("contacts", [])
        cust_data = {
            "organization_id": org_id,
            **data
        }
        customer = await self.repository.create(cust_data)

        for c_data in contacts_data:
            await self.contact_repo.create({
                "organization_id": org_id,
                "customer_id": customer.id,
                **c_data
            })
        return customer

    async def bulk_import_customers_csv(self, org_id: uuid.UUID, file_content: bytes) -> int:
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
                "tags": {"list": row.get("tags", "").split(",")} if row.get("tags") else {"list": []}
            }
            await self.repository.create(cust_dict)
            count += 1
        return count


class DealService(BaseService[Deal, DealRepository]):
    def __init__(self, repository: DealRepository, quotation_repo: QuotationRepository):
        super().__init__(repository)
        self.quotation_repo = quotation_repo

    async def process_deal_result(self, deal_id: uuid.UUID, status: str, reason: Optional[str]) -> Deal:
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
