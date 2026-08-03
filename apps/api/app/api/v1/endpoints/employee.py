import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
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
from app.services.employee import (
    AssetService,
    CertificationService,
    DirectoryService,
    DocumentService,
    EmployeeService,
    ProfileService,
    TimelineService,
)

router = APIRouter()


def get_employee_service(db: AsyncSession = Depends(get_db_session)) -> EmployeeService:
    return EmployeeService(
        EmployeeRepository(db),
        EmployeeProfileRepository(db),
        EmployeeDocumentRepository(db),
        EmployeeNoteRepository(db),
        EmergencyContactRepository(db),
        EmployeeSkillRepository(db),
        CertificationRepository(db),
        EmploymentHistoryRepository(db),
        EmployeeAssetRepository(db),
        EmployeeTimelineRepository(db),
    )


# ---------------------------------------------------------
# EMPLOYEES CRUD
# ---------------------------------------------------------

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    current_user: User = Depends(PermissionChecker("employee.create")),
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.create_employee(data)


@router.get("/employees", response_model=list[EmployeeResponse])
async def list_employees(
    org_id: uuid.UUID | None = None,
    query: str | None = None,
    dept_id: uuid.UUID | None = None,
    branch_id: uuid.UUID | None = None,
    status: str | None = None,
    employment_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    target_org_id = org_id or current_user.organization_id
    if not target_org_id:
        return []
    dir_service = DirectoryService(EmployeeRepository(db))
    return await dir_service.search_directory(
        org_id=target_org_id,
        query=query,
        dept_id=dept_id,
        branch_id=branch_id,
        status=status,
        employment_type=employment_type,
        skip=skip,
        limit=limit,
    )


@router.get("/employees/{id}", response_model=EmployeeResponse)
async def get_employee(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.get_employee_details(id)


@router.patch("/employees/{id}", response_model=EmployeeResponse)
async def update_employee(
    id: uuid.UUID,
    data: EmployeeUpdate,
    current_user: User = Depends(PermissionChecker("employee.update")),
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.update_employee(id, data)


@router.delete("/employees/{id}", response_model=EmployeeResponse)
async def delete_employee(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.delete")),
    service: EmployeeService = Depends(get_employee_service),
):
    emp = await service.delete(id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return EmployeeResponse.model_validate(emp)


# ---------------------------------------------------------
# EMPLOYEE PROFILE: GET /employee-profile/{id}, PUT /employee-profile/{id}
# ---------------------------------------------------------

@router.get("/employee-profile/{id}", response_model=EmployeeProfileSchema)
async def get_employee_profile(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    profile_service = ProfileService(EmployeeProfileRepository(db), EmployeeRepository(db))
    return await profile_service.get_profile(id)


@router.put("/employee-profile/{id}", response_model=EmployeeProfileSchema)
async def update_employee_profile(
    id: uuid.UUID,
    data: EmployeeProfileUpdate,
    current_user: User = Depends(PermissionChecker("profile.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    profile_service = ProfileService(EmployeeProfileRepository(db), EmployeeRepository(db))
    return await profile_service.update_profile(id, data)


# ---------------------------------------------------------
# DOCUMENTS CRUD
# ---------------------------------------------------------

@router.post("/employee-documents", response_model=EmployeeDocumentSchema, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: EmployeeDocumentSchema,
    current_user: User = Depends(PermissionChecker("document.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    doc_repo = EmployeeDocumentRepository(db)
    return await doc_repo.create(data.model_dump(exclude={"id"}))


@router.get("/employee-documents", response_model=list[EmployeeDocumentSchema])
async def list_documents(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    doc_repo = EmployeeDocumentRepository(db)
    return await doc_repo.get_by_employee_id(employee_id)


@router.delete("/employee-documents/{id}", response_model=EmployeeDocumentSchema)
async def delete_document(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("document.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    doc_repo = EmployeeDocumentRepository(db)
    doc = await doc_repo.delete(id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


# ---------------------------------------------------------
# EMERGENCY CONTACTS CRUD
# ---------------------------------------------------------

@router.post("/emergency-contacts", response_model=EmergencyContactSchema, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    data: EmergencyContactSchema,
    current_user: User = Depends(PermissionChecker("employee.update")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmergencyContactRepository(db)
    return await repo.create(data.model_dump(exclude={"id"}))


@router.get("/emergency-contacts", response_model=list[EmergencyContactSchema])
async def list_emergency_contacts(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmergencyContactRepository(db)
    return await repo.get_by_employee_id(employee_id)


@router.delete("/emergency-contacts/{id}", response_model=EmergencyContactSchema)
async def delete_emergency_contact(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.update")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmergencyContactRepository(db)
    item = await repo.delete(id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
    return item


# ---------------------------------------------------------
# EMPLOYMENT HISTORY CRUD
# ---------------------------------------------------------

@router.post("/employment-history", response_model=EmploymentHistorySchema, status_code=status.HTTP_201_CREATED)
async def create_employment_history(
    data: EmploymentHistorySchema,
    current_user: User = Depends(PermissionChecker("employee.update")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmploymentHistoryRepository(db)
    return await repo.create(data.model_dump(exclude={"id"}))


@router.get("/employment-history", response_model=list[EmploymentHistorySchema])
async def list_employment_history(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmploymentHistoryRepository(db)
    return await repo.get_by_employee_id(employee_id)


# ---------------------------------------------------------
# SKILLS CRUD
# ---------------------------------------------------------

@router.post("/employee-skills", response_model=EmployeeSkillSchema, status_code=status.HTTP_201_CREATED)
async def create_skill(
    data: EmployeeSkillSchema,
    current_user: User = Depends(PermissionChecker("employee.update")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeSkillRepository(db)
    return await repo.create(data.model_dump(exclude={"id"}))


@router.get("/employee-skills", response_model=list[EmployeeSkillSchema])
async def list_skills(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeSkillRepository(db)
    return await repo.get_by_employee_id(employee_id)


# ---------------------------------------------------------
# CERTIFICATIONS CRUD
# ---------------------------------------------------------

@router.post("/employee-certifications", response_model=CertificationSchema, status_code=status.HTTP_201_CREATED)
async def create_certification(
    data: CertificationSchema,
    current_user: User = Depends(PermissionChecker("certification.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CertificationService(CertificationRepository(db))
    return await service.create_certification(data)


@router.get("/employee-certifications", response_model=list[CertificationSchema])
async def list_certifications(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CertificationRepository(db)
    return await repo.get_by_employee_id(employee_id)


# ---------------------------------------------------------
# ASSETS CRUD
# ---------------------------------------------------------

@router.post("/employee-assets", response_model=EmployeeAssetSchema, status_code=status.HTTP_201_CREATED)
async def assign_asset(
    data: EmployeeAssetSchema,
    current_user: User = Depends(PermissionChecker("asset.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = AssetService(EmployeeAssetRepository(db))
    return await service.assign_asset(data)


@router.get("/employee-assets", response_model=list[EmployeeAssetSchema])
async def list_assets(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeAssetRepository(db)
    return await repo.get_by_employee_id(employee_id)


# ---------------------------------------------------------
# EMPLOYEE NOTES CRUD
# ---------------------------------------------------------

@router.post("/employee-notes", response_model=EmployeeNoteSchema, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: EmployeeNoteSchema,
    current_user: User = Depends(PermissionChecker("employee.update")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeNoteRepository(db)
    note_data = data.model_dump(exclude={"id"})
    note_data["created_by"] = current_user.id
    return await repo.create(note_data)


@router.get("/employee-notes", response_model=list[EmployeeNoteSchema])
async def list_notes(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeNoteRepository(db)
    return await repo.get_by_employee_id(employee_id)


# ---------------------------------------------------------
# TIMELINE: GET /employee-timeline/{employee_id}
# ---------------------------------------------------------

@router.get("/employee-timeline/{employee_id}", response_model=list[EmployeeTimelineSchema])
async def get_timeline(
    employee_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("employee.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TimelineService(EmployeeTimelineRepository(db))
    return await service.get_timeline(employee_id)
