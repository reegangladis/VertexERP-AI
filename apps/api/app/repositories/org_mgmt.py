import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.branch import Branch
from app.models.department import Department
from app.models.team import Team
from app.models.designation import Designation
from app.models.location import Location
from app.models.calendar import BusinessCalendar, WorkingDay, Holiday
from app.models.document import OrganizationDocument
from app.models.metadata import OrganizationMetadata
from app.models.org_setting import OrganizationSetting

class BranchRepository(BaseRepository[Branch]):
    def __init__(self, db: AsyncSession):
        super().__init__(Branch, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Branch]:
        stmt = select(Branch).where(Branch.organization_id == org_id, Branch.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: AsyncSession):
        super().__init__(Department, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Department]:
        stmt = select(Department).where(Department.organization_id == org_id, Department.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db: AsyncSession):
        super().__init__(Team, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Team]:
        stmt = select(Team).where(Team.organization_id == org_id, Team.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DesignationRepository(BaseRepository[Designation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Designation, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Designation]:
        stmt = select(Designation).where(Designation.organization_id == org_id, Designation.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class LocationRepository(BaseRepository[Location]):
    def __init__(self, db: AsyncSession):
        super().__init__(Location, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Location]:
        stmt = select(Location).where(Location.organization_id == org_id, Location.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CalendarRepository(BaseRepository[BusinessCalendar]):
    def __init__(self, db: AsyncSession):
        super().__init__(BusinessCalendar, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[BusinessCalendar]:
        stmt = select(BusinessCalendar).where(BusinessCalendar.organization_id == org_id, BusinessCalendar.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self, org_id: uuid.UUID) -> Optional[BusinessCalendar]:
        stmt = select(BusinessCalendar).where(
            BusinessCalendar.organization_id == org_id,
            BusinessCalendar.is_active == True,
            BusinessCalendar.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class WorkingDayRepository(BaseRepository[WorkingDay]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkingDay, db)

    async def get_by_calendar(self, calendar_id: uuid.UUID) -> List[WorkingDay]:
        stmt = select(WorkingDay).where(WorkingDay.calendar_id == calendar_id, WorkingDay.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class HolidayRepository(BaseRepository[Holiday]):
    def __init__(self, db: AsyncSession):
        super().__init__(Holiday, db)

    async def get_by_calendar(self, calendar_id: uuid.UUID) -> List[Holiday]:
        stmt = select(Holiday).where(Holiday.calendar_id == calendar_id, Holiday.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DocumentRepository(BaseRepository[OrganizationDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(OrganizationDocument, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[OrganizationDocument]:
        stmt = select(OrganizationDocument).where(OrganizationDocument.organization_id == org_id, OrganizationDocument.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class MetadataRepository(BaseRepository[OrganizationMetadata]):
    def __init__(self, db: AsyncSession):
        super().__init__(OrganizationMetadata, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[OrganizationMetadata]:
        stmt = select(OrganizationMetadata).where(OrganizationMetadata.organization_id == org_id, OrganizationMetadata.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class OrgSettingRepository(BaseRepository[OrganizationSetting]):
    def __init__(self, db: AsyncSession):
        super().__init__(OrganizationSetting, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> Optional[OrganizationSetting]:
        stmt = select(OrganizationSetting).where(OrganizationSetting.organization_id == org_id, OrganizationSetting.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
