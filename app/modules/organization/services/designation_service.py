"""Designation service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.designation import Designation
from app.modules.organization.repositories.designation_repository import DesignationRepository
from app.modules.organization.schemas.designation import DesignationCreate, DesignationUpdate


class DesignationService:
    """Business service for Designation management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.desig_repo = DesignationRepository(session)

    async def create_designation(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: DesignationCreate
    ) -> Designation:
        existing = await self.desig_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Designation with code '{data.code}' already exists in this organization"
            )

        desig = Designation(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            description=data.description,
            level=data.level,
            is_active=data.is_active,
        )
        return await self.desig_repo.create(desig)

    async def get_designation(
        self, desig_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Designation:
        desig = await self.desig_repo.get_by_id(desig_id, tenant_id, org_id)
        if not desig:
            raise NotFoundException(f"Designation '{desig_id}' not found")
        return desig

    async def list_designations(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Designation]:
        return await self.desig_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_designation(
        self, desig_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: DesignationUpdate
    ) -> Designation:
        desig = await self.get_designation(desig_id, tenant_id, org_id)

        if data.code is not None and data.code != desig.code:
            existing = await self.desig_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != desig.id:
                raise ConflictException(f"Designation with code '{data.code}' already exists")
            desig.code = data.code

        if data.name is not None:
            desig.name = data.name
        if data.description is not None:
            desig.description = data.description
        if data.level is not None:
            desig.level = data.level
        if data.is_active is not None:
            desig.is_active = data.is_active

        return await self.desig_repo.update(desig)

    async def delete_designation(
        self, desig_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        desig = await self.get_designation(desig_id, tenant_id, org_id)
        await self.desig_repo.soft_delete(desig)
