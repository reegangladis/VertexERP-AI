import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm_customer import Contact, Customer, CustomerDocument, CustomerNote
from app.models.crm_deal import Deal, Opportunity, Quotation, SalesOrder
from app.models.crm_lead import Lead, LeadActivity, LeadSource
from app.repositories.base import BaseRepository


class SalesOrderRepository(BaseRepository[SalesOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalesOrder, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[SalesOrder]:
        stmt = (
            select(SalesOrder)
            .where(SalesOrder.organization_id == org_id, SalesOrder.is_deleted == False)
            .order_by(SalesOrder.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


from app.models.crm_activity import CRMTask, Meeting
from app.models.crm_campaign import Campaign
from app.models.crm_ticket import SupportTicket


class LeadSourceRepository(BaseRepository[LeadSource]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeadSource, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[LeadSource]:
        stmt = select(LeadSource).where(
            LeadSource.organization_id == org_id, LeadSource.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lead, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Lead]:
        stmt = select(Lead).where(
            Lead.organization_id == org_id, Lead.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class LeadActivityRepository(BaseRepository[LeadActivity]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeadActivity, db)


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Customer]:
        stmt = select(Customer).where(
            Customer.organization_id == org_id, Customer.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: AsyncSession):
        super().__init__(Contact, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Contact]:
        stmt = select(Contact).where(
            Contact.organization_id == org_id, Contact.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CustomerNoteRepository(BaseRepository[CustomerNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerNote, db)


class CustomerDocumentRepository(BaseRepository[CustomerDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerDocument, db)


class OpportunityRepository(BaseRepository[Opportunity]):
    def __init__(self, db: AsyncSession):
        super().__init__(Opportunity, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Opportunity]:
        stmt = select(Opportunity).where(
            Opportunity.organization_id == org_id, Opportunity.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DealRepository(BaseRepository[Deal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Deal, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Deal]:
        stmt = select(Deal).where(
            Deal.organization_id == org_id, Deal.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class QuotationRepository(BaseRepository[Quotation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Quotation, db)


class CRMTaskRepository(BaseRepository[CRMTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(CRMTask, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[CRMTask]:
        stmt = select(CRMTask).where(
            CRMTask.organization_id == org_id, CRMTask.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Meeting]:
        stmt = select(Meeting).where(
            Meeting.organization_id == org_id, Meeting.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class SupportTicketRepository(BaseRepository[SupportTicket]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupportTicket, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[SupportTicket]:
        stmt = select(SupportTicket).where(
            SupportTicket.organization_id == org_id, SupportTicket.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db: AsyncSession):
        super().__init__(Campaign, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Campaign]:
        stmt = select(Campaign).where(
            Campaign.organization_id == org_id, Campaign.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
