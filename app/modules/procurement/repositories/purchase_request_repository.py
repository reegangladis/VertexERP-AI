"""Purchase Request Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.procurement.models.purchase_request import PurchaseRequest


class PurchaseRequestRepository:
    """Repository for Purchase Requests with eager-loading and isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, request_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PurchaseRequest | None:
        stmt = (
            select(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .where(
                PurchaseRequest.id == request_id,
                PurchaseRequest.tenant_id == tenant_id,
                PurchaseRequest.organization_id == org_id,
                PurchaseRequest.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, request_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PurchaseRequest | None:
        stmt = select(PurchaseRequest).where(
            PurchaseRequest.request_number == request_number,
            PurchaseRequest.tenant_id == tenant_id,
            PurchaseRequest.organization_id == org_id,
            PurchaseRequest.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        requester_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[PurchaseRequest]:
        stmt = (
            select(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .where(
                PurchaseRequest.tenant_id == tenant_id,
                PurchaseRequest.organization_id == org_id,
                PurchaseRequest.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(PurchaseRequest.status == status)
        if requester_id:
            stmt = stmt.where(PurchaseRequest.requester_id == requester_id)
        stmt = stmt.order_by(PurchaseRequest.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(PurchaseRequest.id)).where(
            PurchaseRequest.tenant_id == tenant_id,
            PurchaseRequest.organization_id == org_id,
            PurchaseRequest.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(PurchaseRequest.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, request: PurchaseRequest) -> PurchaseRequest:
        self.session.add(request)
        await self.session.flush()
        return request
