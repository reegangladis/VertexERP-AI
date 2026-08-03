import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)

    async def get_by_code(self, org_id: uuid.UUID, emp_code: str) -> Employee | None:
        stmt = select(Employee).where(
            Employee.organization_id == org_id,
            Employee.employee_code == emp_code,
            Employee.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, org_id: uuid.UUID, official_email: str) -> Employee | None:
        stmt = select(Employee).where(
            Employee.organization_id == org_id,
            Employee.official_email == official_email,
            Employee.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_details(self, employee_id: uuid.UUID) -> Employee | None:
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.profile),
                selectinload(Employee.documents),
                selectinload(Employee.notes),
                selectinload(Employee.emergency_contacts),
                selectinload(Employee.skills),
                selectinload(Employee.certifications),
                selectinload(Employee.history),
                selectinload(Employee.assets),
                selectinload(Employee.timeline),
            )
            .where(Employee.id == employee_id, Employee.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_employees(
        self,
        org_id: uuid.UUID,
        query: str | None = None,
        dept_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
        status: str | None = None,
        employment_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Employee]:
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.profile),
                selectinload(Employee.documents),
                selectinload(Employee.notes),
                selectinload(Employee.emergency_contacts),
                selectinload(Employee.skills),
                selectinload(Employee.certifications),
                selectinload(Employee.history),
                selectinload(Employee.assets),
                selectinload(Employee.timeline),
            )
            .where(Employee.organization_id == org_id, Employee.is_deleted == False)
        )
        if dept_id:
            stmt = stmt.where(Employee.department_id == dept_id)
        if branch_id:
            stmt = stmt.where(Employee.branch_id == branch_id)
        if status:
            stmt = stmt.where(Employee.employment_status == status)
        if employment_type:
            stmt = stmt.where(Employee.employment_type == employment_type)
        if query:
            stmt = stmt.where(
                or_(
                    Employee.employee_code.ilike(f"%{query}%"),
                    Employee.first_name.ilike(f"%{query}%"),
                    Employee.last_name.ilike(f"%{query}%"),
                    Employee.official_email.ilike(f"%{query}%"),
                )
            )

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class EmployeeProfileRepository(BaseRepository[EmployeeProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeProfile, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> EmployeeProfile | None:
        stmt = select(EmployeeProfile).where(
            EmployeeProfile.employee_id == employee_id,
            EmployeeProfile.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class EmployeeDocumentRepository(BaseRepository[EmployeeDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeDocument, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmployeeDocument]:
        stmt = select(EmployeeDocument).where(
            EmployeeDocument.employee_id == employee_id,
            EmployeeDocument.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class EmployeeNoteRepository(BaseRepository[EmployeeNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeNote, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmployeeNote]:
        stmt = select(EmployeeNote).where(
            EmployeeNote.employee_id == employee_id,
            EmployeeNote.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class EmergencyContactRepository(BaseRepository[EmergencyContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmergencyContact, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmergencyContact]:
        stmt = select(EmergencyContact).where(
            EmergencyContact.employee_id == employee_id,
            EmergencyContact.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class EmployeeSkillRepository(BaseRepository[EmployeeSkill]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeSkill, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmployeeSkill]:
        stmt = select(EmployeeSkill).where(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CertificationRepository(BaseRepository[Certification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Certification, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[Certification]:
        stmt = select(Certification).where(
            Certification.employee_id == employee_id,
            Certification.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_duplicate(self, employee_id: uuid.UUID, cert_name: str) -> Certification | None:
        stmt = select(Certification).where(
            Certification.employee_id == employee_id,
            Certification.certification_name == cert_name,
            Certification.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class EmploymentHistoryRepository(BaseRepository[EmploymentHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmploymentHistory, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmploymentHistory]:
        stmt = select(EmploymentHistory).where(
            EmploymentHistory.employee_id == employee_id,
            EmploymentHistory.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class EmployeeAssetRepository(BaseRepository[EmployeeAsset]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeAsset, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmployeeAsset]:
        stmt = select(EmployeeAsset).where(
            EmployeeAsset.employee_id == employee_id,
            EmployeeAsset.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_duplicate_code(self, asset_code: str) -> EmployeeAsset | None:
        stmt = select(EmployeeAsset).where(
            EmployeeAsset.asset_code == asset_code,
            EmployeeAsset.status == "assigned",
            EmployeeAsset.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class EmployeeTimelineRepository(BaseRepository[EmployeeTimeline]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeTimeline, db)

    async def get_by_employee_id(self, employee_id: uuid.UUID) -> list[EmployeeTimeline]:
        stmt = (
            select(EmployeeTimeline)
            .where(
                EmployeeTimeline.employee_id == employee_id,
                EmployeeTimeline.is_deleted == False,
            )
            .order_by(EmployeeTimeline.event_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
