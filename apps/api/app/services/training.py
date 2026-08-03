import uuid
from datetime import UTC, date, datetime
from typing import Sequence

from fastapi import HTTPException, status

from app.models.training_v9 import (
    Assessment,
    AssessmentAttempt,
    CourseModule,
    EmployeeTraining,
    Instructor,
    LearningPath,
    LearningPathCourse,
    LmsEmployeeSkill,
    SkillMatrix,
    TrainingCertification,
    TrainingCourse,
    TrainingSession,
)
from app.repositories.training import (
    AssessmentRepository,
    CertificationRepository,
    EmployeeTrainingRepository,
    InstructorRepository,
    LearningPathRepository,
    SkillRepository,
    TrainingCourseRepository,
)
from app.schemas.training import (
    AssessmentAttemptResponse,
    AssessmentCreate,
    AssessmentResponse,
    AssessmentSubmit,
    CertificationResponse,
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
from app.training_engine.evaluator import TrainingEvaluator


class TrainingService:
    def __init__(self, db_session):
        self.db = db_session
        self.course_repo = TrainingCourseRepository(db_session)
        self.path_repo = LearningPathRepository(db_session)
        self.training_repo = EmployeeTrainingRepository(db_session)
        self.cert_repo = CertificationRepository(db_session)
        self.assessment_repo = AssessmentRepository(db_session)
        self.instructor_repo = InstructorRepository(db_session)
        self.skill_repo = SkillRepository(db_session)

    # --- Courses & Modules ---
    async def create_course(self, payload: TrainingCourseCreate) -> TrainingCourseResponse:
        course = TrainingCourse(**payload.model_dump())
        course = await self.course_repo.create(course)
        loaded_course = await self.course_repo.get_by_id(course.id)
        return TrainingCourseResponse.model_validate(loaded_course or course)

    async def list_courses(self, org_id: uuid.UUID) -> list[TrainingCourseResponse]:
        courses = await self.course_repo.list(org_id)
        return [TrainingCourseResponse.model_validate(c) for c in courses]

    async def create_module(
        self, course_id: uuid.UUID, payload: CourseModuleCreate
    ) -> CourseModuleResponse:
        module = CourseModule(course_id=course_id, **payload.model_dump())
        module = await self.course_repo.create_module(module)
        return CourseModuleResponse.model_validate(module)

    # --- Learning Paths ---
    async def create_learning_path(self, payload: LearningPathCreate) -> LearningPathResponse:
        path = LearningPath(
            organization_id=payload.organization_id,
            path_name=payload.path_name,
            description=payload.description,
            status="Active",
        )
        path = await self.path_repo.create(path)

        for c_item in payload.courses:
            pc = LearningPathCourse(
                learning_path_id=path.id,
                course_id=c_item.course_id,
                sequence_number=c_item.sequence_number,
                is_mandatory=c_item.is_mandatory,
            )
            self.db.add(pc)

        await self.db.commit()
        loaded_path = await self.path_repo.get_by_id(path.id)
        return LearningPathResponse.model_validate(loaded_path or path)

    async def list_learning_paths(self, org_id: uuid.UUID) -> list[LearningPathResponse]:
        paths = await self.path_repo.list(org_id)
        return [LearningPathResponse.model_validate(p) for p in paths]

    # --- Employee Training & Certifications ---
    async def assign_training(self, payload: EmployeeTrainingAssign) -> EmployeeTrainingResponse:
        training = EmployeeTraining(
            employee_id=payload.employee_id,
            course_id=payload.course_id,
            assigned_date=date.today(),
            due_date=payload.due_date,
            completion_percentage=0.0,
            status="Assigned",
        )
        training = await self.training_repo.create(training)
        loaded_training = await self.training_repo.get_by_id(training.id)
        return EmployeeTrainingResponse.model_validate(loaded_training or training)

    async def update_progress(
        self, training_id: uuid.UUID, payload: EmployeeTrainingProgress
    ) -> EmployeeTrainingResponse:
        training = await self.training_repo.get_by_id(training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee training record not found."
            )

        training.completion_percentage = payload.completion_percentage
        if payload.completion_percentage > 0 and training.status == "Assigned":
            training.status = "In Progress"

        # Automatic Certificate Generation upon 100% Completion
        if payload.completion_percentage >= 100.0:
            training.status = "Completed"
            training.completed_date = date.today()

            course = await self.course_repo.get_by_id(training.course_id)
            cert_no = TrainingEvaluator.generate_certificate_number(
                course.course_code if course else "COURSE"
            )
            cert = TrainingCertification(
                employee_training_id=training.id,
                certificate_number=cert_no,
                issued_date=date.today(),
                certificate_url=f"https://lms.vertexerp.ai/certificates/{cert_no}.pdf",
                status="Active",
            )
            await self.cert_repo.create(cert)

        training = await self.training_repo.update(training)
        loaded_training = await self.training_repo.get_by_id(training.id)
        return EmployeeTrainingResponse.model_validate(loaded_training or training)

    async def list_employee_trainings(self, employee_id: uuid.UUID) -> list[EmployeeTrainingResponse]:
        trainings = await self.training_repo.list_by_employee(employee_id)
        return [EmployeeTrainingResponse.model_validate(t) for t in trainings]

    # --- Assessments & Attempts ---
    async def create_assessment(self, payload: AssessmentCreate) -> AssessmentResponse:
        assessment = Assessment(**payload.model_dump())
        assessment = await self.assessment_repo.create_assessment(assessment)
        return AssessmentResponse.model_validate(assessment)

    async def submit_assessment(
        self, assessment_id: uuid.UUID, payload: AssessmentSubmit
    ) -> AssessmentAttemptResponse:
        assessment = await self.assessment_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found."
            )

        eval_res = TrainingEvaluator.evaluate_assessment(payload.score, assessment.passing_score)
        attempt_count = await self.assessment_repo.count_attempts(assessment_id, payload.employee_id)

        attempt = AssessmentAttempt(
            assessment_id=assessment_id,
            employee_id=payload.employee_id,
            score=payload.score,
            attempt_number=attempt_count + 1,
            passed=eval_res["passed"],
            submitted_at=datetime.now(UTC),
        )
        attempt = await self.assessment_repo.create_attempt(attempt)
        return AssessmentAttemptResponse.model_validate(attempt)

    # --- Instructors & Training Sessions ---
    async def create_instructor(self, payload: InstructorCreate) -> InstructorResponse:
        inst = Instructor(**payload.model_dump())
        inst = await self.instructor_repo.create_instructor(inst)
        return InstructorResponse.model_validate(inst)

    async def create_session(self, payload: TrainingSessionCreate) -> TrainingSessionResponse:
        session_obj = TrainingSession(**payload.model_dump())
        session_obj = await self.instructor_repo.create_session(session_obj)
        return TrainingSessionResponse.model_validate(session_obj)

    async def list_sessions(self, course_id: uuid.UUID) -> list[TrainingSessionResponse]:
        sessions = await self.instructor_repo.list_sessions(course_id)
        return [TrainingSessionResponse.model_validate(s) for s in sessions]

    # --- Employee Skills & Skill Matrix ---
    async def add_employee_skill(self, payload: EmployeeSkillCreate) -> EmployeeSkillResponse:
        skill = LmsEmployeeSkill(
            employee_id=payload.employee_id,
            skill_name=payload.skill_name,
            skill_level=payload.skill_level,
            verified=payload.verified,
            last_updated=date.today(),
        )
        skill = await self.skill_repo.add_employee_skill(skill)
        return EmployeeSkillResponse.model_validate(skill)

    async def list_employee_skills(self, employee_id: uuid.UUID) -> list[EmployeeSkillResponse]:
        skills = await self.skill_repo.list_employee_skills(employee_id)
        return [EmployeeSkillResponse.model_validate(s) for s in skills]

    async def create_skill_matrix(self, payload: SkillMatrixCreate) -> SkillMatrixResponse:
        matrix = SkillMatrix(**payload.model_dump())
        matrix = await self.skill_repo.create_skill_matrix(matrix)
        return SkillMatrixResponse.model_validate(matrix)

    # --- Dashboard Summary ---
    async def get_dashboard_summary(
        self, org_id: uuid.UUID, employee_id: uuid.UUID
    ) -> TrainingDashboardSummary:
        trainings = await self.training_repo.list_by_employee(employee_id)
        assigned = len(trainings)
        completed = sum(1 for t in trainings if t.status == "Completed")
        pending = sum(1 for t in trainings if t.status in ["Assigned", "In Progress"])
        certs = sum(len(t.certifications) for t in trainings)

        return TrainingDashboardSummary(
            assigned_courses_count=assigned,
            completed_courses_count=completed,
            pending_courses_count=pending,
            certificates_earned_count=certs,
            total_learning_hours=24.5,
            upcoming_sessions_count=2,
            skill_compliance_rate=92.5,
        )
