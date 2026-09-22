"""Department service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.organization.models.department import Department
from app.modules.organization.repositories.department_repository import DepartmentRepository
from app.modules.organization.schemas.department import (
    DepartmentCreate,
    DepartmentTreeNode,
    DepartmentUpdate,
)


class DepartmentService:
    """Business service for Department operations with hierarchy support."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dept_repo = DepartmentRepository(session)

    async def create_department(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: DepartmentCreate
    ) -> Department:
        existing = await self.dept_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Department with code '{data.code}' already exists in this organization"
            )

        if data.parent_department_id:
            parent = await self.dept_repo.get_by_id(data.parent_department_id, tenant_id, org_id)
            if not parent:
                raise NotFoundException(
                    f"Parent department '{data.parent_department_id}' not found"
                )

        dept = Department(
            tenant_id=tenant_id,
            organization_id=org_id,
            parent_department_id=data.parent_department_id,
            code=data.code,
            name=data.name,
            description=data.description,
            manager_user_id=data.manager_user_id,
            is_active=data.is_active,
        )
        return await self.dept_repo.create(dept)

    async def get_department(
        self, dept_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Department:
        dept = await self.dept_repo.get_by_id(dept_id, tenant_id, org_id)
        if not dept:
            raise NotFoundException(f"Department '{dept_id}' not found")
        return dept

    async def list_departments(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Department]:
        return await self.dept_repo.list_by_org(tenant_id, org_id, is_active)

    async def get_department_tree(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[DepartmentTreeNode]:
        all_depts = await self.dept_repo.list_by_org(tenant_id, org_id)
        nodes_map: dict[uuid.UUID, DepartmentTreeNode] = {}
        for d in all_depts:
            node = DepartmentTreeNode(
                id=d.id,
                tenant_id=d.tenant_id,
                organization_id=d.organization_id,
                parent_department_id=d.parent_department_id,
                code=d.code,
                name=d.name,
                description=d.description,
                manager_user_id=d.manager_user_id,
                is_active=d.is_active,
                version=d.version,
                created_at=d.created_at,
                updated_at=d.updated_at,
                children=[],
            )
            nodes_map[d.id] = node

        root_nodes: list[DepartmentTreeNode] = []
        for node in nodes_map.values():
            if node.parent_department_id and node.parent_department_id in nodes_map:
                nodes_map[node.parent_department_id].children.append(node)
            else:
                root_nodes.append(node)

        return root_nodes

    async def update_department(
        self, dept_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: DepartmentUpdate
    ) -> Department:
        dept = await self.get_department(dept_id, tenant_id, org_id)

        if data.code is not None and data.code != dept.code:
            existing = await self.dept_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != dept.id:
                raise ConflictException(f"Department with code '{data.code}' already exists")
            dept.code = data.code

        if data.parent_department_id is not None:
            if data.parent_department_id == dept.id:
                raise ValidationException("A department cannot be its own parent")
            parent = await self.dept_repo.get_by_id(data.parent_department_id, tenant_id, org_id)
            if not parent:
                raise NotFoundException(
                    f"Parent department '{data.parent_department_id}' not found"
                )
            dept.parent_department_id = data.parent_department_id

        if data.name is not None:
            dept.name = data.name
        if data.description is not None:
            dept.description = data.description
        if data.manager_user_id is not None:
            dept.manager_user_id = data.manager_user_id
        if data.is_active is not None:
            dept.is_active = data.is_active

        return await self.dept_repo.update(dept)

    async def delete_department(
        self, dept_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        dept = await self.get_department(dept_id, tenant_id, org_id)
        await self.dept_repo.soft_delete(dept)
