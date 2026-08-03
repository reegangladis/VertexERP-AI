import uuid

from fastapi import HTTPException, status

from app.models.cost_center import CostCenter
from app.repositories.cost_center import CostCenterRepository
from app.schemas.cost_center import CostCenterCreate, CostCenterUpdate
from app.services.base import BaseService


class CostCenterService(BaseService[CostCenter, CostCenterRepository]):
    def __init__(self, repository: CostCenterRepository):
        super().__init__(repository)

    async def create_cost_center(self, obj_in: CostCenterCreate) -> CostCenter:
        existing = await self.repository.get_by_code(obj_in.organization_id, obj_in.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cost center code '{obj_in.code}' already exists.",
            )
        return await self.repository.create(obj_in.model_dump())

    async def update_cost_center(self, cc_id: uuid.UUID, obj_in: CostCenterUpdate) -> CostCenter:
        item = await self.repository.get(cc_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cost center not found."
            )
        if obj_in.code and obj_in.code != item.code:
            existing = await self.repository.get_by_code(item.organization_id, obj_in.code)
            if existing and existing.id != cc_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cost center code '{obj_in.code}' already exists.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(item, k, v)
        await self.repository.db.commit()
        await self.repository.db.refresh(item)
        return item
