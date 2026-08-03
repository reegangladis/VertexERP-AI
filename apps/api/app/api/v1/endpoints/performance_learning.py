import uuid
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.performance_learning import (
    CertificateRepository,
    CompetencyRepository,
    CourseRepository,
    EmployeeCompetencyRepository,
    EnrollmentRepository,
    FeedbackRepository,
    GoalRepository,
    KeyResultRepository,
    PerformanceReviewRepository,
    ReviewCycleRepository,
    SkillMatrixRepository,
    TrainingProgramRepository,
)
from app.schemas.performance_learning import (
    CompetencyCreate,
    CompetencyResponse,
    CompetencyUpdate,
    CourseEnrollmentCreate,
    CourseEnrollmentResponse,
    CourseEnrollmentUpdate,
    EmployeeCompetencyCreate,
    EmployeeCompetencyResponse,
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    KeyResultCreate,
    KeyResultResponse,
    KeyResultUpdate,
    LearningCertificateCreate,
    LearningCertificateResponse,
    PerformanceDashboardSummary,
    PerformanceFeedbackCreate,
    PerformanceFeedbackResponse,
    PerformanceFeedbackUpdate,
    PerformanceReviewCreate,
    PerformanceReviewCycleCreate,
    PerformanceReviewCycleResponse,
    PerformanceReviewCycleUpdate,
    PerformanceReviewResponse,
    PerformanceReviewUpdate,
    SkillMatrixCreate,
    SkillMatrixResponse,
    SkillMatrixUpdate,
    TrainingCourseCreate,
    TrainingCourseResponse,
    TrainingCourseUpdate,
    TrainingDashboardSummary,
    TrainingProgramCreate,
    TrainingProgramResponse,
)
from app.services.performance_learning import (
    CompetencyService,
    FeedbackService,
    GoalService,
    PerformanceService,
    TrainingService,
)

router = APIRouter()


# --- Goals & Key Results ---
@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(PermissionChecker("goal.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = GoalService(db)
    return await service.create_goal(payload)


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = GoalRepository(db)
    return await repo.get_by_employee(employee_id)


@router.get("/goals/{id}", response_model=GoalResponse)
async def get_goal(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = GoalRepository(db)
    goal = await repo.get_with_key_results(id)
    if not goal:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return goal


@router.put("/goals/{id}", response_model=GoalResponse)
async def update_goal(
    id: uuid.UUID,
    payload: GoalUpdate,
    current_user: User = Depends(PermissionChecker("goal.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = GoalService(db)
    return await service.update_goal(id, payload)


@router.delete("/goals/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("goal.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = GoalRepository(db)
    await repo.delete(id)
    return None


@router.post("/goals/{id}/key-results", response_model=KeyResultResponse, status_code=status.HTTP_201_CREATED)
async def add_key_result(
    id: uuid.UUID,
    payload: KeyResultCreate,
    current_user: User = Depends(PermissionChecker("goal.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = GoalService(db)
    return await service.add_key_result(id, payload)


@router.put("/key-results/{id}", response_model=KeyResultResponse)
async def update_key_result(
    id: uuid.UUID,
    payload: KeyResultUpdate,
    current_user: User = Depends(PermissionChecker("goal.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = GoalService(db)
    return await service.update_key_result(id, payload)


# --- Performance Review Cycles & Reviews ---
@router.post("/review-cycles", response_model=PerformanceReviewCycleResponse, status_code=status.HTTP_201_CREATED)
async def create_review_cycle(
    payload: PerformanceReviewCycleCreate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PerformanceService(db)
    return await service.create_cycle(payload)


@router.get("/review-cycles", response_model=list[PerformanceReviewCycleResponse])
async def list_review_cycles(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ReviewCycleRepository(db)
    return await repo.get_by_org(org_id)


@router.put("/review-cycles/{id}", response_model=PerformanceReviewCycleResponse)
async def update_review_cycle(
    id: uuid.UUID,
    payload: PerformanceReviewCycleUpdate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PerformanceService(db)
    return await service.update_cycle(id, payload)


@router.post("/reviews", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: PerformanceReviewCreate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PerformanceService(db)
    return await service.create_review(payload)


@router.get("/reviews", response_model=list[PerformanceReviewResponse])
async def list_reviews(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PerformanceReviewRepository(db)
    return await repo.get_by_employee(employee_id)


@router.get("/reviews/{id}", response_model=PerformanceReviewResponse)
async def get_review(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PerformanceReviewRepository(db)
    return await repo.get_with_feedback(id)


@router.post("/reviews/{id}/submit", response_model=PerformanceReviewResponse)
async def submit_review(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PerformanceService(db)
    return await service.submit_review(id)


# --- Performance Feedback (Self, Manager, Peer, 360) ---
@router.post("/feedback", response_model=PerformanceFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: PerformanceFeedbackCreate,
    current_user: User = Depends(PermissionChecker("feedback.submit")),
    db: AsyncSession = Depends(get_db_session),
):
    service = FeedbackService(db)
    return await service.submit_feedback(payload)


@router.put("/feedback/{id}", response_model=PerformanceFeedbackResponse)
async def update_feedback(
    id: uuid.UUID,
    payload: PerformanceFeedbackUpdate,
    current_user: User = Depends(PermissionChecker("feedback.submit")),
    db: AsyncSession = Depends(get_db_session),
):
    service = FeedbackService(db)
    return await service.update_feedback(id, payload)


@router.get("/feedback/review/{review_id}", response_model=list[PerformanceFeedbackResponse])
async def get_feedback_for_review(
    review_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = FeedbackRepository(db)
    return await repo.get_by_review(review_id)


# --- Competencies & Employee Competencies ---
@router.post("/competencies", response_model=CompetencyResponse, status_code=status.HTTP_201_CREATED)
async def create_competency(
    payload: CompetencyCreate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CompetencyService(db)
    return await service.create_competency(payload)


@router.get("/competencies", response_model=list[CompetencyResponse])
async def list_competencies(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CompetencyRepository(db)
    records, _ = await repo.get_multi(filters={"organization_id": org_id})
    return records


@router.put("/competencies/{id}", response_model=CompetencyResponse)
async def update_competency(
    id: uuid.UUID,
    payload: CompetencyUpdate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CompetencyService(db)
    return await service.update_competency(id, payload)


@router.post("/employee-competencies", response_model=EmployeeCompetencyResponse, status_code=status.HTTP_201_CREATED)
async def assign_employee_competency(
    payload: EmployeeCompetencyCreate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CompetencyService(db)
    return await service.assign_employee_competency(payload)


@router.get("/employee-competencies", response_model=list[EmployeeCompetencyResponse])
async def list_employee_competencies(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EmployeeCompetencyRepository(db)
    return await repo.get_by_employee(employee_id)


# --- Courses & Enrollments ---
@router.post("/courses", response_model=TrainingCourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: TrainingCourseCreate,
    current_user: User = Depends(PermissionChecker("course.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.create_course(payload)


@router.get("/courses", response_model=list[TrainingCourseResponse])
async def list_courses(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CourseRepository(db)
    records, _ = await repo.get_multi(filters={"organization_id": org_id})
    return records


@router.put("/courses/{id}", response_model=TrainingCourseResponse)
async def update_course(
    id: uuid.UUID,
    payload: TrainingCourseUpdate,
    current_user: User = Depends(PermissionChecker("course.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.update_course(id, payload)


@router.post("/enrollments", response_model=CourseEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_course(
    payload: CourseEnrollmentCreate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.enroll_employee(payload)


@router.get("/enrollments", response_model=list[CourseEnrollmentResponse])
async def list_enrollments(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = EnrollmentRepository(db)
    return await repo.get_by_employee(employee_id)


@router.put("/enrollments/{id}/progress", response_model=CourseEnrollmentResponse)
async def update_enrollment_progress(
    id: uuid.UUID,
    payload: CourseEnrollmentUpdate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.update_enrollment_progress(id, payload)


# --- Training Programs ---
@router.post("/training-programs", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_training_program(
    payload: TrainingProgramCreate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.create_program(payload)


@router.get("/training-programs", response_model=list[TrainingProgramResponse])
async def list_training_programs(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = TrainingProgramRepository(db)
    records, _ = await repo.get_multi(filters={"organization_id": org_id})
    return records


# --- Certificates & Download ---
@router.get("/certificates", response_model=list[LearningCertificateResponse])
async def list_certificates(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("certificate.view")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CertificateRepository(db)
    return await repo.get_by_employee(employee_id)


@router.get("/certificates/{cert_number}/download")
async def download_certificate(
    cert_number: str,
    current_user: User = Depends(PermissionChecker("certificate.view")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CertificateRepository(db)
    cert = await repo.get_by_number(cert_number)
    if not cert:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    content = f"--- VERTEXERP AI LEARNING CERTIFICATE ---\nCertificate Number: {cert.certificate_number}\nIssue Date: {cert.issue_date}\nExpiry Date: {cert.expiry_date or 'N/A'}\nIssued to Employee ID: {cert.employee_id}\nCourse ID: {cert.course_id}"
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{cert_number}.txt"'},
    )


# --- Skill Matrix ---
@router.post("/skill-matrix", response_model=SkillMatrixResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_matrix_item(
    payload: SkillMatrixCreate,
    current_user: User = Depends(PermissionChecker("performance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = SkillMatrixRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/skill-matrix", response_model=list[SkillMatrixResponse])
async def list_skill_matrix(
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = SkillMatrixRepository(db)
    return await repo.get_by_employee(employee_id)


# --- Performance & Training Dashboards ---
@router.get("/performance/dashboard", response_model=PerformanceDashboardSummary)
async def get_performance_dashboard(
    org_id: uuid.UUID = Query(...),
    employee_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("performance.review")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PerformanceService(db)
    return await service.get_dashboard_summary(org_id, employee_id)


@router.get("/training/dashboard", response_model=TrainingDashboardSummary)
async def get_training_dashboard(
    org_id: uuid.UUID = Query(...),
    employee_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("goal.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = TrainingService(db)
    return await service.get_training_dashboard(org_id, employee_id)
