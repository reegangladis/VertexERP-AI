import uuid

from fastapi import HTTPException, status

from app.models.department import Department
from app.repositories.department import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentTreeNode, DepartmentUpdate
from app.services.base import BaseService


class DepartmentService(BaseService[Department, DepartmentRepository]):
    def __init__(self, repository: DepartmentRepository):
        super().__init__(repository)

    async def create_department(self, obj_in: DepartmentCreate) -> Department:
        if obj_in.code:
            existing = await self.repository.get_by_code(obj_in.organization_id, obj_in.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department code '{obj_in.code}' already exists in this organization.",
                )

        if obj_in.parent_department_id:
            parent = await self.repository.get(obj_in.parent_department_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found.",
                )

        return await self.repository.create(obj_in.model_dump())

    async def update_department(self, department_id: uuid.UUID, obj_in: DepartmentUpdate) -> Department:
        dept = await self.repository.get(department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found."
            )

        if obj_in.code and obj_in.code != dept.code:
            existing = await self.repository.get_by_code(dept.organization_id, obj_in.code)
            if existing and existing.id != department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department code '{obj_in.code}' already exists.",
                )

        if obj_in.parent_department_id is not None:
            if obj_in.parent_department_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A department cannot be its own parent.",
                )
            descendants = await self.repository.get_descendants(department_id)
            if obj_in.parent_department_id in descendants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular hierarchy error: Cannot set a descendant department as parent.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(dept, k, v)

        await self.repository.db.commit()
        await self.repository.db.refresh(dept)
        return dept

    async def get_department_tree(self, org_id: uuid.UUID) -> list[DepartmentTreeNode]:
        all_depts = await self.repository.get_all_by_org(org_id)
        dept_map = {d.id: DepartmentTreeNode.model_validate(d) for d in all_depts}
        roots: list[DepartmentTreeNode] = []

        for d in all_depts:
            node = dept_map[d.id]
            if d.parent_department_id and d.parent_department_id in dept_map:
                dept_map[d.parent_department_id].children.append(node)
            else:
                roots.append(node)

        return roots
