import uuid

from fastapi import HTTPException, status

from app.models.business_unit import BusinessUnit
from app.repositories.business_unit import BusinessUnitRepository
from app.schemas.business_unit import BusinessUnitCreate, BusinessUnitTreeNode, BusinessUnitUpdate
from app.services.base import BaseService


class BusinessUnitService(BaseService[BusinessUnit, BusinessUnitRepository]):
    def __init__(self, repository: BusinessUnitRepository):
        super().__init__(repository)

    async def create_business_unit(self, obj_in: BusinessUnitCreate) -> BusinessUnit:
        if obj_in.code:
            existing = await self.repository.get_by_code(obj_in.organization_id, obj_in.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Business unit code '{obj_in.code}' already exists.",
                )

        if obj_in.parent_business_unit_id:
            parent = await self.repository.get(obj_in.parent_business_unit_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent business unit not found.",
                )

        return await self.repository.create(obj_in.model_dump())

    async def update_business_unit(self, unit_id: uuid.UUID, obj_in: BusinessUnitUpdate) -> BusinessUnit:
        unit = await self.repository.get(unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Business unit not found."
            )
        if obj_in.code and obj_in.code != unit.code:
            existing = await self.repository.get_by_code(unit.organization_id, obj_in.code)
            if existing and existing.id != unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Business unit code '{obj_in.code}' already exists.",
                )

        if obj_in.parent_business_unit_id is not None:
            if obj_in.parent_business_unit_id == unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A business unit cannot be its own parent.",
                )
            descendants = await self.repository.get_descendants(unit_id)
            if obj_in.parent_business_unit_id in descendants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular hierarchy error: Cannot set a descendant business unit as parent.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(unit, k, v)
        await self.repository.db.commit()
        await self.repository.db.refresh(unit)
        return unit

    async def get_business_unit_tree(self, org_id: uuid.UUID) -> list[BusinessUnitTreeNode]:
        all_units = await self.repository.get_all_by_org(org_id)
        unit_map = {u.id: BusinessUnitTreeNode.model_validate(u) for u in all_units}
        roots: list[BusinessUnitTreeNode] = []

        for u in all_units:
            node = unit_map[u.id]
            if u.parent_business_unit_id and u.parent_business_unit_id in unit_map:
                unit_map[u.parent_business_unit_id].children.append(node)
            else:
                roots.append(node)

        return roots
