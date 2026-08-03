import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm_sales_v10 import (
    CRMTask,
    Customer,
    CustomerAddress,
    CustomerContact,
    CustomerDocument,
    CustomerNote,
    CustomerTimeline,
    Lead,
    LeadActivity,
    LeadSource,
    Meeting,
    Opportunity,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
)
from app.repositories.base import BaseRepository


class LeadSourceRepository(BaseRepository[LeadSource]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeadSource, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[LeadSource]:
        stmt = select(LeadSource).where(
            LeadSource.organization_id == org_id, LeadSource.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lead, db)

    async def get_with_activities(self, lead_id: uuid.UUID) -> Lead | None:
        stmt = (
            select(Lead)
            .options(selectinload(Lead.activities))
            .where(Lead.id == lead_id, Lead.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_email(self, org_id: uuid.UUID, email: str) -> Lead | None:
        stmt = select(Lead).where(
            Lead.organization_id == org_id, Lead.email == email, Lead.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Lead]:
        stmt = (
            select(Lead)
            .options(selectinload(Lead.activities))
            .where(Lead.organization_id == org_id, Lead.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class LeadActivityRepository(BaseRepository[LeadActivity]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeadActivity, db)

    async def get_by_lead(self, lead_id: uuid.UUID) -> list[LeadActivity]:
        stmt = select(LeadActivity).where(
            LeadActivity.lead_id == lead_id, LeadActivity.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_with_details(self, customer_id: uuid.UUID) -> Customer | None:
        stmt = (
            select(Customer)
            .options(
                selectinload(Customer.contacts),
                selectinload(Customer.addresses),
                selectinload(Customer.opportunities),
                selectinload(Customer.quotations),
                selectinload(Customer.sales_orders),
            )
            .where(Customer.id == customer_id, Customer.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> Customer | None:
        stmt = select(Customer).where(
            Customer.organization_id == org_id, Customer.customer_code == code, Customer.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_email(self, org_id: uuid.UUID, email: str) -> Customer | None:
        stmt = select(Customer).where(
            Customer.organization_id == org_id, Customer.email == email, Customer.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class CustomerContactRepository(BaseRepository[CustomerContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerContact, db)

    async def get_by_customer(self, customer_id: uuid.UUID) -> list[CustomerContact]:
        stmt = select(CustomerContact).where(
            CustomerContact.customer_id == customer_id, CustomerContact.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class CustomerAddressRepository(BaseRepository[CustomerAddress]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerAddress, db)


class CustomerNoteRepository(BaseRepository[CustomerNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerNote, db)


class CustomerDocumentRepository(BaseRepository[CustomerDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerDocument, db)


class OpportunityRepository(BaseRepository[Opportunity]):
    def __init__(self, db: AsyncSession):
        super().__init__(Opportunity, db)

    async def get_by_customer(self, customer_id: uuid.UUID) -> list[Opportunity]:
        stmt = select(Opportunity).where(
            Opportunity.customer_id == customer_id, Opportunity.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class QuotationRepository(BaseRepository[Quotation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Quotation, db)

    async def get_with_items(self, quotation_id: uuid.UUID) -> Quotation | None:
        stmt = (
            select(Quotation)
            .options(selectinload(Quotation.items))
            .where(Quotation.id == quotation_id, Quotation.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, q_number: str) -> Quotation | None:
        stmt = select(Quotation).where(
            Quotation.quotation_number == q_number, Quotation.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class QuotationItemRepository(BaseRepository[QuotationItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(QuotationItem, db)


class SalesOrderRepository(BaseRepository[SalesOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalesOrder, db)

    async def get_with_items(self, order_id: uuid.UUID) -> SalesOrder | None:
        stmt = (
            select(SalesOrder)
            .options(selectinload(SalesOrder.items))
            .where(SalesOrder.id == order_id, SalesOrder.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, order_number: str) -> SalesOrder | None:
        stmt = select(SalesOrder).where(
            SalesOrder.sales_order_number == order_number, SalesOrder.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class SalesOrderItemRepository(BaseRepository[SalesOrderItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalesOrderItem, db)


class CRMTaskRepository(BaseRepository[CRMTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(CRMTask, db)

    async def get_by_customer(self, customer_id: uuid.UUID) -> list[CRMTask]:
        stmt = select(CRMTask).where(
            CRMTask.customer_id == customer_id, CRMTask.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def get_by_customer(self, customer_id: uuid.UUID) -> list[Meeting]:
        stmt = select(Meeting).where(
            Meeting.customer_id == customer_id, Meeting.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class CustomerTimelineRepository(BaseRepository[CustomerTimeline]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerTimeline, db)

    async def get_by_customer(self, customer_id: uuid.UUID) -> list[CustomerTimeline]:
        stmt = (
            select(CustomerTimeline)
            .where(CustomerTimeline.customer_id == customer_id, CustomerTimeline.is_deleted == False)
            .order_by(CustomerTimeline.event_time.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
