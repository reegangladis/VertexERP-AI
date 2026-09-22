"""Business Unit service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.business_unit import BusinessUnit
from app.modules.organization.repositories.business_unit_repository import BusinessUnitRepository
from app.modules.organization.schemas.business_unit import BusinessUnitCreate, BusinessUnitUpdate


class BusinessUnitService:
    """Business service for Business Unit management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bu_repo = BusinessUnitRepository(session)

    async def create_business_unit(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: BusinessUnitCreate
    ) -> BusinessUnit:
        existing = await self.bu_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Business unit with code '{data.code}' already exists in this organization"
            )

        bu = BusinessUnit(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            description=data.description,
            head_user_id=data.head_user_id,
            is_active=data.is_active,
        )
        return await self.bu_repo.create(bu)

    async def get_business_unit(
        self, bu_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BusinessUnit:
        bu = await self.bu_repo.get_by_id(bu_id, tenant_id, org_id)
        if not bu:
            raise NotFoundException(f"Business unit '{bu_id}' not found")
        return bu

    async def list_business_units(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[BusinessUnit]:
        return await self.bu_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_business_unit(
        self, bu_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: BusinessUnitUpdate
    ) -> BusinessUnit:
        bu = await self.get_business_unit(bu_id, tenant_id, org_id)

        if data.code is not None and data.code != bu.code:
            existing = await self.bu_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != bu.id:
                raise ConflictException(f"Business unit with code '{data.code}' already exists")
            bu.code = data.code

        if data.name is not None:
            bu.name = data.name
        if data.description is not None:
            bu.description = data.description
        if data.head_user_id is not None:
            bu.head_user_id = data.head_user_id
        if data.is_active is not None:
            bu.is_active = data.is_active

        return await self.bu_repo.update(bu)

    async def delete_business_unit(
        self, bu_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        bu = await self.get_business_unit(bu_id, tenant_id, org_id)
        await self.bu_repo.soft_delete(bu)
