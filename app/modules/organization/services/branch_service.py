"""Branch service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.branch import Branch
from app.modules.organization.repositories.branch_repository import BranchRepository
from app.modules.organization.schemas.branch import BranchCreate, BranchUpdate


class BranchService:
    """Business service for Branch operations with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.branch_repo = BranchRepository(session)

    async def create_branch(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: BranchCreate
    ) -> Branch:
        existing = await self.branch_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Branch with code '{data.code}' already exists in this organization"
            )

        branch = Branch(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            phone=data.phone,
            email=data.email,
            is_headquarters=data.is_headquarters,
            is_active=data.is_active,
        )
        return await self.branch_repo.create(branch)

    async def get_branch(
        self, branch_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Branch:
        branch = await self.branch_repo.get_by_id(branch_id, tenant_id, org_id)
        if not branch:
            raise NotFoundException(f"Branch '{branch_id}' not found")
        return branch

    async def list_branches(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Branch]:
        return await self.branch_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_branch(
        self, branch_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: BranchUpdate
    ) -> Branch:
        branch = await self.get_branch(branch_id, tenant_id, org_id)

        if data.code is not None and data.code != branch.code:
            existing = await self.branch_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != branch.id:
                raise ConflictException(f"Branch with code '{data.code}' already exists")
            branch.code = data.code

        if data.name is not None:
            branch.name = data.name
        if data.address_line1 is not None:
            branch.address_line1 = data.address_line1
        if data.address_line2 is not None:
            branch.address_line2 = data.address_line2
        if data.city is not None:
            branch.city = data.city
        if data.state is not None:
            branch.state = data.state
        if data.postal_code is not None:
            branch.postal_code = data.postal_code
        if data.country is not None:
            branch.country = data.country
        if data.phone is not None:
            branch.phone = data.phone
        if data.email is not None:
            branch.email = data.email
        if data.is_headquarters is not None:
            branch.is_headquarters = data.is_headquarters
        if data.is_active is not None:
            branch.is_active = data.is_active

        return await self.branch_repo.update(branch)

    async def delete_branch(
        self, branch_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        branch = await self.get_branch(branch_id, tenant_id, org_id)
        await self.branch_repo.soft_delete(branch)
