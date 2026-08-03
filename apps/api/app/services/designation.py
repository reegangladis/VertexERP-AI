import uuid

from fastapi import HTTPException, status

from app.models.designation import Designation
from app.repositories.designation import DesignationRepository
from app.schemas.designation import DesignationCreate, DesignationUpdate
from app.services.base import BaseService


class DesignationService(BaseService[Designation, DesignationRepository]):
    def __init__(self, repository: DesignationRepository):
        super().__init__(repository)

    async def create_designation(self, obj_in: DesignationCreate) -> Designation:
        if obj_in.code:
            existing = await self.repository.get_by_code(obj_in.organization_id, obj_in.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Designation code '{obj_in.code}' already exists.",
                )
        return await self.repository.create(obj_in.model_dump())

    async def update_designation(self, designation_id: uuid.UUID, obj_in: DesignationUpdate) -> Designation:
        item = await self.repository.get(designation_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found."
            )
        if obj_in.code and obj_in.code != item.code:
            existing = await self.repository.get_by_code(item.organization_id, obj_in.code)
            if existing and existing.id != designation_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Designation code '{obj_in.code}' already exists.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(item, k, v)
        await self.repository.db.commit()
        await self.repository.db.refresh(item)
        return item
