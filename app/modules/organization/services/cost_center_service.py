"""Cost Center service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.cost_center import CostCenter
from app.modules.organization.repositories.cost_center_repository import CostCenterRepository
from app.modules.organization.schemas.cost_center import CostCenterCreate, CostCenterUpdate


class CostCenterService:
    """Business service for Cost Center management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.cc_repo = CostCenterRepository(session)

    async def create_cost_center(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: CostCenterCreate
    ) -> CostCenter:
        existing = await self.cc_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Cost center with code '{data.code}' already exists in this organization"
            )

        cc = CostCenter(
            tenant_id=tenant_id,
            organization_id=org_id,
            department_id=data.department_id,
            code=data.code,
            name=data.name,
            description=data.description,
            annual_budget=data.annual_budget,
            currency=data.currency,
            is_active=data.is_active,
        )
        return await self.cc_repo.create(cc)

    async def get_cost_center(
        self, cc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CostCenter:
        cc = await self.cc_repo.get_by_id(cc_id, tenant_id, org_id)
        if not cc:
            raise NotFoundException(f"Cost center '{cc_id}' not found")
        return cc

    async def list_cost_centers(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[CostCenter]:
        return await self.cc_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_cost_center(
        self, cc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: CostCenterUpdate
    ) -> CostCenter:
        cc = await self.get_cost_center(cc_id, tenant_id, org_id)

        if data.code is not None and data.code != cc.code:
            existing = await self.cc_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != cc.id:
                raise ConflictException(f"Cost center with code '{data.code}' already exists")
            cc.code = data.code

        if data.name is not None:
            cc.name = data.name
        if data.description is not None:
            cc.description = data.description
        if data.department_id is not None:
            cc.department_id = data.department_id
        if data.annual_budget is not None:
            cc.annual_budget = data.annual_budget
        if data.currency is not None:
            cc.currency = data.currency
        if data.is_active is not None:
            cc.is_active = data.is_active

        return await self.cc_repo.update(cc)

    async def delete_cost_center(
        self, cc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        cc = await self.get_cost_center(cc_id, tenant_id, org_id)
        await self.cc_repo.soft_delete(cc)
