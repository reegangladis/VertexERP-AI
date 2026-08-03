import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.employee import (
    Certification,
    EmergencyContact,
    Employee,
    EmployeeAsset,
    EmployeeDocument,
    EmployeeNote,
    EmployeeProfile,
    EmployeeSkill,
    EmployeeTimeline,
    EmploymentHistory,
)
from app.repositories.employee import (
    CertificationRepository,
    EmergencyContactRepository,
    EmployeeAssetRepository,
    EmployeeDocumentRepository,
    EmployeeNoteRepository,
    EmployeeProfileRepository,
    EmployeeRepository,
    EmployeeSkillRepository,
    EmployeeTimelineRepository,
    EmploymentHistoryRepository,
)
from app.schemas.employee import (
    CertificationSchema,
    EmergencyContactSchema,
    EmployeeAssetSchema,
    EmployeeCreate,
    EmployeeDocumentSchema,
    EmployeeNoteSchema,
    EmployeeProfileSchema,
    EmployeeProfileUpdate,
    EmployeeResponse,
    EmployeeSkillSchema,
    EmployeeTimelineSchema,
    EmployeeUpdate,
    EmploymentHistorySchema,
)
from app.services.base import BaseService


class EmployeeService(BaseService[Employee, EmployeeRepository]):
    def __init__(
        self,
        repository: EmployeeRepository,
        profile_repo: EmployeeProfileRepository,
        doc_repo: EmployeeDocumentRepository,
        note_repo: EmployeeNoteRepository,
        contact_repo: EmergencyContactRepository,
        skill_repo: EmployeeSkillRepository,
        cert_repo: CertificationRepository,
        history_repo: EmploymentHistoryRepository,
        asset_repo: EmployeeAssetRepository,
        timeline_repo: EmployeeTimelineRepository,
    ):
        super().__init__(repository)
        self.profile_repo = profile_repo
        self.doc_repo = doc_repo
        self.note_repo = note_repo
        self.contact_repo = contact_repo
        self.skill_repo = skill_repo
        self.cert_repo = cert_repo
        self.history_repo = history_repo
        self.asset_repo = asset_repo
        self.timeline_repo = timeline_repo

    async def create_employee(self, obj_in: EmployeeCreate) -> EmployeeResponse:
        existing_code = await self.repository.get_by_code(obj_in.organization_id, obj_in.employee_code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee code '{obj_in.employee_code}' already exists in this organization.",
            )
        existing_email = await self.repository.get_by_email(obj_in.organization_id, obj_in.official_email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Official email '{obj_in.official_email}' already exists in this organization.",
            )

        emp_data = obj_in.model_dump(exclude={"profile"})
        emp = await self.repository.create(emp_data)

        # Create Profile
        prof_data = obj_in.profile.model_dump() if obj_in.profile else {}
        prof_data["employee_id"] = emp.id
        await self.profile_repo.create(prof_data)

        # Create Timeline Entry
        await self.timeline_repo.create(
            {
                "employee_id": emp.id,
                "event_type": "onboarding",
                "title": "Joined Organization",
                "description": f"Joined organization with code {emp.employee_code}",
                "event_date": datetime.now(UTC),
            }
        )

        full_emp = await self.repository.get_with_details(emp.id) or emp
        return EmployeeResponse.model_validate(full_emp)

    async def update_employee(self, emp_id: uuid.UUID, obj_in: EmployeeUpdate) -> EmployeeResponse:
        emp = await self.repository.get(emp_id)
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )

        if obj_in.employee_code and obj_in.employee_code != emp.employee_code:
            existing_code = await self.repository.get_by_code(emp.organization_id, obj_in.employee_code)
            if existing_code and existing_code.id != emp_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employee code '{obj_in.employee_code}' already exists.",
                )

        if obj_in.official_email and obj_in.official_email != emp.official_email:
            existing_email = await self.repository.get_by_email(emp.organization_id, obj_in.official_email)
            if existing_email and existing_email.id != emp_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Official email '{obj_in.official_email}' already exists.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(emp, k, v)

        await self.repository.db.commit()

        # Log timeline event
        await self.timeline_repo.create(
            {
                "employee_id": emp.id,
                "event_type": "update",
                "title": "Employee Profile Updated",
                "description": "Core employment info updated",
                "event_date": datetime.now(UTC),
            }
        )

        full_emp = await self.repository.get_with_details(emp_id) or emp
        return EmployeeResponse.model_validate(full_emp)

    async def get_employee_details(self, emp_id: uuid.UUID) -> EmployeeResponse:
        full_emp = await self.repository.get_with_details(emp_id)
        if not full_emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )
        return EmployeeResponse.model_validate(full_emp)


class ProfileService(BaseService[EmployeeProfile, EmployeeProfileRepository]):
    def __init__(self, repository: EmployeeProfileRepository, emp_repo: EmployeeRepository):
        super().__init__(repository)
        self.emp_repo = emp_repo

    async def get_profile(self, employee_id: uuid.UUID) -> EmployeeProfile:
        prof = await self.repository.get_by_employee_id(employee_id)
        if not prof:
            emp = await self.emp_repo.get(employee_id)
            if not emp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
                )
            prof = await self.repository.create({"employee_id": employee_id})
        return prof

    async def update_profile(self, employee_id: uuid.UUID, obj_in: EmployeeProfileUpdate) -> EmployeeProfile:
        prof = await self.get_profile(employee_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(prof, k, v)
        await self.repository.db.commit()
        await self.repository.db.refresh(prof)
        return prof


class DocumentService(BaseService[EmployeeDocument, EmployeeDocumentRepository]):
    def __init__(self, repository: EmployeeDocumentRepository):
        super().__init__(repository)


class CertificationService(BaseService[Certification, CertificationRepository]):
    def __init__(self, repository: CertificationRepository):
        super().__init__(repository)

    async def create_certification(self, obj_in: CertificationSchema) -> Certification:
        if obj_in.employee_id:
            dup = await self.repository.check_duplicate(obj_in.employee_id, obj_in.certification_name)
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Certification '{obj_in.certification_name}' already exists for this employee.",
                )
        return await self.repository.create(obj_in.model_dump())


class AssetService(BaseService[EmployeeAsset, EmployeeAssetRepository]):
    def __init__(self, repository: EmployeeAssetRepository):
        super().__init__(repository)

    async def assign_asset(self, obj_in: EmployeeAssetSchema) -> EmployeeAsset:
        dup = await self.repository.check_duplicate_code(obj_in.asset_code)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset with code '{obj_in.asset_code}' is currently assigned.",
            )
        return await self.repository.create(obj_in.model_dump())


class TimelineService(BaseService[EmployeeTimeline, EmployeeTimelineRepository]):
    def __init__(self, repository: EmployeeTimelineRepository):
        super().__init__(repository)

    async def get_timeline(self, employee_id: uuid.UUID) -> list[EmployeeTimeline]:
        return await self.repository.get_by_employee_id(employee_id)


class DirectoryService:
    def __init__(self, emp_repo: EmployeeRepository):
        self.emp_repo = emp_repo

    async def search_directory(
        self,
        org_id: uuid.UUID,
        query: str | None = None,
        dept_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
        status: str | None = None,
        employment_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EmployeeResponse]:
        employees = await self.emp_repo.search_employees(
            org_id=org_id,
            query=query,
            dept_id=dept_id,
            branch_id=branch_id,
            status=status,
            employment_type=employment_type,
            skip=skip,
            limit=limit,
        )
        return [EmployeeResponse.model_validate(e) for e in employees]

