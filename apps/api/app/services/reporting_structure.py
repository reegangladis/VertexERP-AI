import uuid

from fastapi import HTTPException, status

from app.models.reporting_structure import ReportingStructure
from app.repositories.reporting_structure import ReportingStructureRepository
from app.schemas.reporting_structure import ReportingStructureCreate, ReportingStructureUpdate
from app.services.base import BaseService


class ReportingStructureService(BaseService[ReportingStructure, ReportingStructureRepository]):
    def __init__(self, repository: ReportingStructureRepository):
        super().__init__(repository)

    async def create_reporting_relation(self, obj_in: ReportingStructureCreate) -> ReportingStructure:
        if obj_in.employee_uuid == obj_in.manager_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee cannot report to themselves.",
            )
        return await self.repository.create(obj_in.model_dump())
