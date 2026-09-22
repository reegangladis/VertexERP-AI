"""CRM domain repository providing persistence operations for CRM entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.crm.models.contact import Contact
from app.modules.crm.models.customer import Customer
from app.modules.crm.models.deal import Deal, DealStageHistory
from app.modules.crm.models.lead import Lead
from app.modules.crm.models.pipeline import Pipeline, PipelineStage
from app.modules.crm.models.quotation import Quotation
from app.modules.crm.models.sales_order import SalesOrder


class CRMRepository:
    """Repository handling CRM domain entity database interactions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # Leads
    # --------------------------------------------------------------------------
    async def create_lead(self, lead: Lead) -> Lead:
        self.session.add(lead)
        await self.session.flush()
        await self.session.refresh(lead)
        return lead

    async def get_lead_by_id(self, lead_id: uuid.UUID, tenant_id: uuid.UUID) -> Lead | None:
        stmt = select(Lead).where(
            Lead.id == lead_id,
            Lead.tenant_id == tenant_id,
            Lead.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_leads(
        self, tenant_id: uuid.UUID, organization_id: uuid.UUID | None = None
    ) -> list[Lead]:
        stmt = select(Lead).where(Lead.tenant_id == tenant_id, Lead.is_deleted.is_(False))
        if organization_id:
            stmt = stmt.where(Lead.organization_id == organization_id)
        result = await self.session.execute(stmt.order_by(Lead.created_at.desc()))
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # Pipelines & Stages
    # --------------------------------------------------------------------------
    async def create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        self.session.add(pipeline)
        await self.session.flush()
        await self.session.refresh(pipeline)
        return pipeline

    async def create_pipeline_stage(self, stage: PipelineStage) -> PipelineStage:
        self.session.add(stage)
        await self.session.flush()
        await self.session.refresh(stage)
        return stage

    async def get_pipeline_by_id(
        self, pipeline_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Pipeline | None:
        stmt = (
            select(Pipeline)
            .options(selectinload(Pipeline.stages))
            .where(
                Pipeline.id == pipeline_id,
                Pipeline.tenant_id == tenant_id,
                Pipeline.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    # Customers & Contacts
    # --------------------------------------------------------------------------
    async def create_customer(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()
        await self.session.refresh(customer)
        return customer

    async def get_customer_by_id(
        self, customer_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Customer | None:
        stmt = select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == tenant_id,
            Customer.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, contact: Contact) -> Contact:
        self.session.add(contact)
        await self.session.flush()
        await self.session.refresh(contact)
        return contact

    # --------------------------------------------------------------------------
    # Deals
    # --------------------------------------------------------------------------
    async def create_deal(self, deal: Deal) -> Deal:
        self.session.add(deal)
        await self.session.flush()
        await self.session.refresh(deal)
        return deal

    async def get_deal_by_id(self, deal_id: uuid.UUID, tenant_id: uuid.UUID) -> Deal | None:
        stmt = select(Deal).where(
            Deal.id == deal_id,
            Deal.tenant_id == tenant_id,
            Deal.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def record_stage_history(self, history: DealStageHistory) -> DealStageHistory:
        self.session.add(history)
        await self.session.flush()
        return history

    # --------------------------------------------------------------------------
    # Quotations
    # --------------------------------------------------------------------------
    async def create_quotation(self, quotation: Quotation) -> Quotation:
        self.session.add(quotation)
        await self.session.flush()
        saved = await self.get_quotation_by_id(quotation.id, quotation.tenant_id)
        return saved or quotation

    async def get_quotation_by_id(
        self, quotation_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Quotation | None:
        stmt = (
            select(Quotation)
            .options(selectinload(Quotation.items))
            .where(
                Quotation.id == quotation_id,
                Quotation.tenant_id == tenant_id,
                Quotation.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    # Sales Orders
    # --------------------------------------------------------------------------
    async def create_sales_order(self, order: SalesOrder) -> SalesOrder:
        self.session.add(order)
        await self.session.flush()
        saved = await self.get_sales_order_by_id(order.id, order.tenant_id)
        return saved or order

    async def get_sales_order_by_id(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> SalesOrder | None:
        stmt = (
            select(SalesOrder)
            .options(selectinload(SalesOrder.items))
            .where(
                SalesOrder.id == order_id,
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
