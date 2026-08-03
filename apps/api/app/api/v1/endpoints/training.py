import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.schemas.training import (
    AssessmentAttemptResponse,
    AssessmentCreate,
    AssessmentResponse,
    AssessmentSubmit,
    CourseModuleCreate,
    CourseModuleResponse,
    EmployeeSkillCreate,
    EmployeeSkillResponse,
    EmployeeTrainingAssign,
    EmployeeTrainingProgress,
    EmployeeTrainingResponse,
    InstructorCreate,
    InstructorResponse,
    LearningPathCreate,
    LearningPathResponse,
    SkillMatrixCreate,
    SkillMatrixResponse,
    TrainingCourseCreate,
    TrainingCourseResponse,
    TrainingDashboardSummary,
    TrainingSessionCreate,
    TrainingSessionResponse,
)
from app.services.training import TrainingService

router = APIRouter()


def get_training_service(db: AsyncSession = Depends(get_db_session)) -> TrainingService:
    return TrainingService(db)


# --- Training Courses & Modules ---
@router.post("/courses", response_model=TrainingCourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: TrainingCourseCreate,
    current_user: User = Depends(PermissionChecker("course.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_course(payload)


@router.get("/courses", response_model=list[TrainingCourseResponse])
async def list_courses(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.list_courses(org_id)


@router.post("/courses/{id}/modules", response_model=CourseModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    id: uuid.UUID,
    payload: CourseModuleCreate,
    current_user: User = Depends(PermissionChecker("course.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_module(id, payload)


# --- Learning Paths ---
@router.post("/learning-paths", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    payload: LearningPathCreate,
    current_user: User = Depends(PermissionChecker("course.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_learning_path(payload)


@router.get("/learning-paths", response_model=list[LearningPathResponse])
async def list_learning_paths(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.list_learning_paths(org_id)


# --- Training Assignments & Progress ---
@router.post("/assign", response_model=EmployeeTrainingResponse, status_code=status.HTTP_201_CREATED)
async def assign_training(
    payload: EmployeeTrainingAssign,
    current_user: User = Depends(PermissionChecker("training.assign")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.assign_training(payload)


@router.post("/trainings/{id}/progress", response_model=EmployeeTrainingResponse)
async def update_progress(
    id: uuid.UUID,
    payload: EmployeeTrainingProgress,
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.update_progress(id, payload)


@router.get("/employee-trainings", response_model=list[EmployeeTrainingResponse])
async def list_employee_trainings(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.list_employee_trainings(employee_id)


# --- Assessments & Attempts ---
@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(PermissionChecker("assessment.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_assessment(payload)


@router.post("/assessments/{id}/submit", response_model=AssessmentAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    id: uuid.UUID,
    payload: AssessmentSubmit,
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.submit_assessment(id, payload)


# --- Instructors & Sessions ---
@router.post("/instructors", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
async def create_instructor(
    payload: InstructorCreate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_instructor(payload)


@router.post("/sessions", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: TrainingSessionCreate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_session(payload)


@router.get("/sessions", response_model=list[TrainingSessionResponse])
async def list_sessions(
    course_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.list_sessions(course_id)


# --- Skills & Skill Matrix ---
@router.post("/skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_employee_skill(
    payload: EmployeeSkillCreate,
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.add_employee_skill(payload)


@router.get("/skills", response_model=list[EmployeeSkillResponse])
async def list_employee_skills(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.list_employee_skills(employee_id)


@router.post("/skill-matrix", response_model=SkillMatrixResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_matrix(
    payload: SkillMatrixCreate,
    current_user: User = Depends(PermissionChecker("learning.admin")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.create_skill_matrix(payload)


# --- Dashboard Summary ---
@router.get("/dashboard-summary", response_model=TrainingDashboardSummary)
async def get_dashboard_summary(
    org_id: uuid.UUID = Query(...),
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("training.read")),
    service: TrainingService = Depends(get_training_service),
):
    return await service.get_dashboard_summary(org_id, employee_id)
