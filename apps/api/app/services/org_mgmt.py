import uuid
import os
import csv
import io
from typing import List, Optional, Any, Dict
from sqlalchemy import select
from fastapi import UploadFile

from app.services.base import BaseService
from app.repositories.org_mgmt import (
    BranchRepository,
    DepartmentRepository,
    TeamRepository,
    DesignationRepository,
    LocationRepository,
    BusinessUnitRepository,
    CalendarRepository,
    WorkingDayRepository,
    HolidayRepository,
    DocumentRepository,
    MetadataRepository,
    OrgSettingRepository,
)
from app.models.branch import Branch
from app.models.department import Department
from app.models.team import Team
from app.models.designation import Designation
from app.models.location import Location
from app.models.business_unit import BusinessUnit
from app.models.calendar import BusinessCalendar, WorkingDay, Holiday
from app.models.document import OrganizationDocument
from app.models.metadata import OrganizationMetadata
from app.models.org_setting import OrganizationSetting

class OrgMgmtServiceException(Exception):
    pass


class BranchService(BaseService[Branch, BranchRepository]):
    def __init__(self, repository: BranchRepository):
        super().__init__(repository)

    async def validate_parent(self, branch_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> None:
        if not parent_id:
            return
        if branch_id == parent_id:
            raise OrgMgmtServiceException("A branch cannot be its own parent.")
        
        # Traverse up from parent to make sure there's no cycle
        curr_id = parent_id
        visited = {branch_id}
        while curr_id:
            if curr_id in visited:
                raise OrgMgmtServiceException("Cyclic hierarchy detected in branch mappings.")
            visited.add(curr_id)
            parent_branch = await self.repository.get(curr_id)
            if not parent_branch:
                break
            curr_id = parent_branch.parent_branch_id

    async def get_by_org(self, org_id: uuid.UUID) -> List[Branch]:
        return await self.repository.get_by_org(org_id)


class DepartmentService(BaseService[Department, DepartmentRepository]):
    def __init__(self, repository: DepartmentRepository):
        super().__init__(repository)

    async def validate_parent(self, dept_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> None:
        if not parent_id:
            return
        if dept_id == parent_id:
            raise OrgMgmtServiceException("A department cannot be its own parent.")
        
        curr_id = parent_id
        visited = {dept_id}
        while curr_id:
            if curr_id in visited:
                raise OrgMgmtServiceException("Cyclic hierarchy detected in department mappings.")
            visited.add(curr_id)
            parent_dept = await self.repository.get(curr_id)
            if not parent_dept:
                break
            curr_id = parent_dept.parent_department_id

    async def get_by_org(self, org_id: uuid.UUID) -> List[Department]:
        return await self.repository.get_by_org(org_id)


class TeamService(BaseService[Team, TeamRepository]):
    def __init__(self, repository: TeamRepository):
        super().__init__(repository)

    async def validate_parent(self, team_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> None:
        if not parent_id:
            return
        if team_id == parent_id:
            raise OrgMgmtServiceException("A team cannot be its own parent.")
        
        curr_id = parent_id
        visited = {team_id}
        while curr_id:
            if curr_id in visited:
                raise OrgMgmtServiceException("Cyclic hierarchy detected in team mappings.")
            visited.add(curr_id)
            parent_team = await self.repository.get(curr_id)
            if not parent_team:
                break
            curr_id = parent_team.parent_team_id

    async def get_by_org(self, org_id: uuid.UUID) -> List[Team]:
        return await self.repository.get_by_org(org_id)


class DesignationService(BaseService[Designation, DesignationRepository]):
    def __init__(self, repository: DesignationRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Designation]:
        return await self.repository.get_by_org(org_id)


class LocationService(BaseService[Location, LocationRepository]):
    def __init__(self, repository: LocationRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Location]:
        return await self.repository.get_by_org(org_id)


class BusinessUnitService(BaseService[BusinessUnit, BusinessUnitRepository]):
    def __init__(self, repository: BusinessUnitRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> List[BusinessUnit]:
        return await self.repository.get_by_org(org_id)


class BusinessCalendarService(BaseService[BusinessCalendar, CalendarRepository]):
    def __init__(
        self,
        repository: CalendarRepository,
        working_day_repo: WorkingDayRepository,
        holiday_repo: HolidayRepository,
    ):
        super().__init__(repository)
        self.working_day_repo = working_day_repo
        self.holiday_repo = holiday_repo

    async def get_by_org(self, org_id: uuid.UUID) -> List[BusinessCalendar]:
        return await self.repository.get_by_org(org_id)

    async def get_active(self, org_id: uuid.UUID) -> Optional[BusinessCalendar]:
        return await self.repository.get_active(org_id)

    async def configure_working_days(self, org_id: uuid.UUID, calendar_id: uuid.UUID, days_data: List[Dict[str, Any]]) -> List[WorkingDay]:
        # Clear existing working days for this calendar
        existing = await self.working_day_repo.get_by_calendar(calendar_id)
        for day in existing:
            await self.working_day_repo.delete(day.id, hard=True)

        created = []
        for item in days_data:
            day_obj = await self.working_day_repo.create({
                "organization_id": org_id,
                "calendar_id": calendar_id,
                "day_of_week": item["day_of_week"],
                "is_working": item.get("is_working", True),
                "start_time": item.get("start_time", "09:00"),
                "end_time": item.get("end_time", "17:00")
            })
            created.append(day_obj)
        return created

    async def configure_holidays(self, org_id: uuid.UUID, calendar_id: uuid.UUID, holidays_data: List[Dict[str, Any]]) -> List[Holiday]:
        # Clear existing holidays
        existing = await self.holiday_repo.get_by_calendar(calendar_id)
        for holiday in existing:
            await self.holiday_repo.delete(holiday.id, hard=True)

        created = []
        for item in holidays_data:
            holiday_obj = await self.holiday_repo.create({
                "organization_id": org_id,
                "calendar_id": calendar_id,
                "name": item["name"],
                "date": item["date"],
                "type": item.get("type", "public"),
                "description": item.get("description")
            })
            created.append(holiday_obj)
        return created


class DocumentService(BaseService[OrganizationDocument, DocumentRepository]):
    def __init__(self, repository: DocumentRepository):
        super().__init__(repository)
        self.upload_dir = os.path.abspath("uploads")
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def get_by_org(self, org_id: uuid.UUID) -> List[OrganizationDocument]:
        return await self.repository.get_by_org(org_id)

    async def upload_document(
        self,
        org_id: uuid.UUID,
        name: str,
        doc_type: str,
        file: UploadFile,
        provider: str = "local"
    ) -> OrganizationDocument:
        # File reading
        content = await file.read()
        file_size = len(content)
        mime_type = file.content_type
        
        file_path = ""
        if provider == "local":
            # Save file locally
            filename = f"{uuid.uuid4()}_{file.filename}"
            full_path = os.path.join(self.upload_dir, filename)
            with open(full_path, "wb") as f:
                f.write(content)
            # Store relative/safe path
            file_path = f"uploads/{filename}"
        elif provider in ["s3", "azure", "gcs"]:
            # Cloud storage placeholders
            file_path = f"mock://{provider}-bucket/{uuid.uuid4()}_{file.filename}"
        else:
            raise OrgMgmtServiceException(f"Unsupported storage provider: {provider}")

        doc = await self.repository.create({
            "organization_id": org_id,
            "name": name,
            "type": doc_type,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "storage_provider": provider,
            "metadata_json": {"original_filename": file.filename}
        })
        return doc


class MetadataService(BaseService[OrganizationMetadata, MetadataRepository]):
    def __init__(self, repository: MetadataRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> List[OrganizationMetadata]:
        return await self.repository.get_by_org(org_id)

    async def set_metadata(self, org_id: uuid.UUID, key: str, value: str, value_type: str = "string") -> OrganizationMetadata:
        existing_list, _ = await self.repository.get_multi(filters={"organization_id": org_id, "key": key})
        if existing_list:
            db_obj = existing_list[0]
            return await self.repository.update(db_obj, {"value": value, "value_type": value_type})
        else:
            return await self.repository.create({
                "organization_id": org_id,
                "key": key,
                "value": value,
                "value_type": value_type
            })


class OrgSettingService(BaseService[OrganizationSetting, OrgSettingRepository]):
    def __init__(self, repository: OrgSettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> Optional[OrganizationSetting]:
        return await self.repository.get_by_org_id(org_id)

    async def configure_settings(self, org_id: uuid.UUID, data: Dict[str, Any]) -> OrganizationSetting:
        existing = await self.repository.get_by_org_id(org_id)
        if existing:
            return await self.repository.update(existing, data)
        else:
            data_to_create = {"organization_id": org_id, **data}
            return await self.repository.create(data_to_create)


# Helper for CSV operations
def parse_csv_file(file_content: bytes) -> List[Dict[str, str]]:
    stream = io.StringIO(file_content.decode("utf-8"))
    reader = csv.DictReader(stream)
    return list(reader)

def generate_csv_text(headers: List[str], data_rows: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in data_rows:
        writer.writerow(row)
    return output.getvalue()
