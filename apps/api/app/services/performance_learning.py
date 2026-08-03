import uuid
from datetime import UTC, date, datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    CompetencyUpdate,
    CourseEnrollmentCreate,
    CourseEnrollmentUpdate,
    EmployeeCompetencyCreate,
    EmployeeCompetencyUpdate,
    GoalCreate,
    GoalUpdate,
    KeyResultCreate,
    KeyResultUpdate,
    LearningCertificateCreate,
    PerformanceDashboardSummary,
    PerformanceFeedbackCreate,
    PerformanceFeedbackUpdate,
    PerformanceReviewCreate,
    PerformanceReviewCycleCreate,
    PerformanceReviewCycleUpdate,
    PerformanceReviewUpdate,
    SkillMatrixCreate,
    SkillMatrixUpdate,
    TrainingCourseCreate,
    TrainingCourseUpdate,
    TrainingDashboardSummary,
    TrainingProgramCreate,
    TrainingProgramUpdate,
)


class GoalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.goal_repo = GoalRepository(db)
        self.kr_repo = KeyResultRepository(db)

    async def create_goal(self, payload: GoalCreate):
        if payload.start_date > payload.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal start_date cannot be after end_date.",
            )

        existing = await self.goal_repo.find_duplicate_title(payload.employee_id, payload.title)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A goal with title '{payload.title}' already exists for this employee.",
            )

        goal = await self.goal_repo.create(
            {
                "organization_id": payload.organization_id,
                "employee_id": payload.employee_id,
                "title": payload.title,
                "description": payload.description,
                "goal_type": payload.goal_type,
                "priority": payload.priority,
                "weightage": payload.weightage,
                "start_date": payload.start_date,
                "end_date": payload.end_date,
                "status": payload.status,
                "progress": payload.progress,
            }
        )

        for kr_data in payload.key_results:
            await self.kr_repo.create(
                {
                    "goal_id": goal.id,
                    "title": kr_data.title,
                    "target_value": kr_data.target_value,
                    "current_value": kr_data.current_value,
                    "measurement_unit": kr_data.measurement_unit,
                    "progress": kr_data.progress,
                    "status": kr_data.status,
                }
            )

        return await self.goal_repo.get_with_key_results(goal.id)

    async def update_goal(self, goal_id: uuid.UUID, payload: GoalUpdate):
        goal = await self.goal_repo.get(goal_id)
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        update_dict = payload.model_dump(exclude_unset=True)
        start_d = update_dict.get("start_date", goal.start_date)
        end_d = update_dict.get("end_date", goal.end_date)
        if start_d > end_d:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal start_date cannot be after end_date.",
            )

        if "title" in update_dict:
            existing = await self.goal_repo.find_duplicate_title(
                goal.employee_id, update_dict["title"], exclude_id=goal_id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A goal with title '{update_dict['title']}' already exists.",
                )

        updated_goal = await self.goal_repo.update(goal_id, update_dict)
        return await self.goal_repo.get_with_key_results(updated_goal.id)

    async def add_key_result(self, goal_id: uuid.UUID, payload: KeyResultCreate):
        goal = await self.goal_repo.get(goal_id)
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        kr = await self.kr_repo.create(
            {
                "goal_id": goal_id,
                "title": payload.title,
                "target_value": payload.target_value,
                "current_value": payload.current_value,
                "measurement_unit": payload.measurement_unit,
                "progress": payload.progress,
                "status": payload.status,
            }
        )
        return kr

    async def update_key_result(self, kr_id: uuid.UUID, payload: KeyResultUpdate):
        kr = await self.kr_repo.get(kr_id)
        if not kr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key Result not found")

        update_dict = payload.model_dump(exclude_unset=True)
        if "target_value" in update_dict or "current_value" in update_dict:
            target = update_dict.get("target_value", kr.target_value)
            current = update_dict.get("current_value", kr.current_value)
            if target > 0:
                calc_progress = min(100.0, max(0.0, (current / target) * 100.0))
                update_dict["progress"] = calc_progress

        updated = await self.kr_repo.update(kr_id, update_dict)

        # Recalculate goal overall progress
        key_results = await self.kr_repo.get_by_goal(kr.goal_id)
        if key_results:
            avg_prog = sum(k.progress for k in key_results) / len(key_results)
            await self.goal_repo.update(kr.goal_id, {"progress": round(avg_prog, 2)})

        return updated


class PerformanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cycle_repo = ReviewCycleRepository(db)
        self.review_repo = PerformanceReviewRepository(db)
        self.feedback_repo = FeedbackRepository(db)
        self.goal_repo = GoalRepository(db)
        self.emp_comp_repo = EmployeeCompetencyRepository(db)
        self.cert_repo = CertificateRepository(db)

    async def create_cycle(self, payload: PerformanceReviewCycleCreate):
        if payload.start_date > payload.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review cycle start_date cannot be after end_date.",
            )
        return await self.cycle_repo.create(payload.model_dump())

    async def update_cycle(self, cycle_id: uuid.UUID, payload: PerformanceReviewCycleUpdate):
        cycle = await self.cycle_repo.get(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        update_dict = payload.model_dump(exclude_unset=True)
        start_d = update_dict.get("start_date", cycle.start_date)
        end_d = update_dict.get("end_date", cycle.end_date)
        if start_d > end_d:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review cycle start_date cannot be after end_date.",
            )
        return await self.cycle_repo.update(cycle_id, update_dict)

    async def create_review(self, payload: PerformanceReviewCreate):
        cycle = await self.cycle_repo.get(payload.review_cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review Cycle not found")

        review = await self.review_repo.create(payload.model_dump())
        return await self.review_repo.get_with_feedback(review.id)

    async def submit_review(self, review_id: uuid.UUID):
        review = await self.review_repo.get_with_feedback(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

        feedbacks = await self.feedback_repo.get_by_review(review_id)
        ratings = [f.rating for f in feedbacks if f.rating is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            overall_score = (avg_rating / 5.0) * 100.0
        else:
            avg_rating = review.overall_rating or 0.0
            overall_score = (avg_rating / 5.0) * 100.0 if avg_rating else 0.0

        updated = await self.review_repo.update(
            review_id,
            {
                "status": "Submitted",
                "overall_rating": round(avg_rating, 2),
                "overall_score": round(overall_score, 2),
                "submitted_at": datetime.now(UTC),
            },
        )
        return await self.review_repo.get_with_feedback(updated.id)

    async def get_dashboard_summary(
        self, org_id: uuid.UUID, employee_id: uuid.UUID | None = None
    ) -> PerformanceDashboardSummary:
        goals = await self.goal_repo.get_all()
        if employee_id:
            goals = [g for g in goals if g.employee_id == employee_id]

        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.status == "Completed" or g.progress >= 100.0])
        avg_goal_prog = (sum(g.progress for g in goals) / total_goals) if total_goals else 0.0

        cycles = await self.cycle_repo.get_by_org(org_id)
        active_cycles = len([c for c in cycles if c.status in ("Active", "In Progress")])

        reviews = await self.review_repo.get_all()
        if employee_id:
            reviews = [r for r in reviews if r.employee_id == employee_id]

        pending_reviews = len([r for r in reviews if r.status != "Submitted" and r.status != "Completed"])
        ratings = [r.overall_rating for r in reviews if r.overall_rating is not None]
        avg_rating = (sum(ratings) / len(ratings)) if ratings else 0.0

        # Promotion Readiness Calculation
        readiness_score = min(
            100.0,
            round(
                (avg_goal_prog * 0.35)
                + ((avg_rating / 5.0 * 100.0) * 0.45)
                + (min(100.0, completed_goals * 15.0) * 0.20),
                2,
            ),
        )

        trends = [
            {"period": "Q1 2026", "rating": round(avg_rating * 0.9, 1), "goalCompletion": 80},
            {"period": "Q2 2026", "rating": round(avg_rating * 0.95, 1), "goalCompletion": 88},
            {"period": "Q3 2026", "rating": round(avg_rating, 1), "goalCompletion": round(avg_goal_prog, 1)},
        ]

        return PerformanceDashboardSummary(
            total_goals=total_goals,
            completed_goals=completed_goals,
            average_goal_progress=round(avg_goal_prog, 2),
            active_review_cycles=active_cycles,
            pending_reviews=pending_reviews,
            average_performance_rating=round(avg_rating, 2),
            promotion_readiness_score=readiness_score,
            performance_trends=trends,
        )


class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feedback_repo = FeedbackRepository(db)
        self.review_repo = PerformanceReviewRepository(db)

    async def submit_feedback(self, payload: PerformanceFeedbackCreate):
        review = await self.review_repo.get(payload.review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance Review not found")

        valid_types = {"Self", "Manager", "Peer", "360"}
        if payload.feedback_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid feedback_type. Must be one of {valid_types}",
            )

        feedback = await self.feedback_repo.create(
            {
                "review_id": payload.review_id,
                "feedback_type": payload.feedback_type,
                "comments": payload.comments,
                "rating": payload.rating,
                "submitted_by": payload.submitted_by,
                "submitted_at": datetime.now(UTC),
            }
        )
        return feedback

    async def update_feedback(self, feedback_id: uuid.UUID, payload: PerformanceFeedbackUpdate):
        fb = await self.feedback_repo.get(feedback_id)
        if not fb:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

        update_dict = payload.model_dump(exclude_unset=True)
        update_dict["submitted_at"] = datetime.now(UTC)
        return await self.feedback_repo.update(feedback_id, update_dict)


class CompetencyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.comp_repo = CompetencyRepository(db)
        self.emp_comp_repo = EmployeeCompetencyRepository(db)

    async def create_competency(self, payload: CompetencyCreate):
        dup = await self.comp_repo.find_duplicate_name(payload.organization_id, payload.name)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency '{payload.name}' already exists in this organization.",
            )
        return await self.comp_repo.create(payload.model_dump())

    async def update_competency(self, comp_id: uuid.UUID, payload: CompetencyUpdate):
        comp = await self.comp_repo.get(comp_id)
        if not comp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competency not found")

        update_dict = payload.model_dump(exclude_unset=True)
        if "name" in update_dict:
            dup = await self.comp_repo.find_duplicate_name(
                comp.organization_id, update_dict["name"], exclude_id=comp_id
            )
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Competency '{update_dict['name']}' already exists.",
                )
        return await self.comp_repo.update(comp_id, update_dict)

    async def assign_employee_competency(self, payload: EmployeeCompetencyCreate):
        return await self.emp_comp_repo.create(payload.model_dump())


class TrainingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.enroll_repo = EnrollmentRepository(db)
        self.program_repo = TrainingProgramRepository(db)
        self.cert_repo = CertificateRepository(db)
        self.skill_repo = SkillMatrixRepository(db)

    async def create_course(self, payload: TrainingCourseCreate):
        dup = await self.course_repo.get_by_code(payload.organization_id, payload.course_code)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course code '{payload.course_code}' already exists.",
            )
        return await self.course_repo.create(payload.model_dump())

    async def update_course(self, course_id: uuid.UUID, payload: TrainingCourseUpdate):
        course = await self.course_repo.get(course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return await self.course_repo.update(course_id, payload.model_dump(exclude_unset=True))

    async def enroll_employee(self, payload: CourseEnrollmentCreate):
        course = await self.course_repo.get(payload.course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        existing = await self.enroll_repo.get_existing_enrollment(payload.employee_id, payload.course_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is already enrolled in this course.",
            )

        return await self.enroll_repo.create(
            {
                "employee_id": payload.employee_id,
                "course_id": payload.course_id,
                "enrolled_at": datetime.now(UTC),
                "completion_percentage": 0.0,
                "status": "Enrolled",
            }
        )

    async def update_enrollment_progress(self, enrollment_id: uuid.UUID, payload: CourseEnrollmentUpdate):
        enrollment = await self.enroll_repo.get(enrollment_id)
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

        update_dict = payload.model_dump(exclude_unset=True)
        percentage = update_dict.get("completion_percentage", enrollment.completion_percentage)

        if percentage >= 100.0:
            update_dict["status"] = "Completed"
            update_dict["completion_percentage"] = 100.0
            if not enrollment.completed_at and not update_dict.get("completed_at"):
                update_dict["completed_at"] = datetime.now(UTC)

            # Auto-generate certificate
            cert_no = f"CERT-{uuid.uuid4().hex[:8].upper()}"
            existing_certs = await self.cert_repo.get_by_employee(enrollment.employee_id)
            course_cert = next((c for c in existing_certs if c.course_id == enrollment.course_id), None)

            if not course_cert:
                await self.cert_repo.create(
                    {
                        "employee_id": enrollment.employee_id,
                        "course_id": enrollment.course_id,
                        "certificate_number": cert_no,
                        "issue_date": date.today(),
                        "expiry_date": None,
                        "certificate_url": f"/api/v1/certificates/{cert_no}/download",
                    }
                )

        elif percentage > 0.0 and enrollment.status == "Enrolled":
            update_dict["status"] = "In Progress"

        return await self.enroll_repo.update(enrollment_id, update_dict)

    async def create_program(self, payload: TrainingProgramCreate):
        program = await self.program_repo.create(
            {
                "organization_id": payload.organization_id,
                "program_name": payload.program_name,
                "description": payload.description,
                "status": payload.status,
            }
        )
        return program

    async def get_training_dashboard(
        self, org_id: uuid.UUID, employee_id: uuid.UUID | None = None
    ) -> TrainingDashboardSummary:
        courses = await self.course_repo.get_all()
        total_courses = len(courses)

        enrollments = await self.enroll_repo.get_all()
        if employee_id:
            enrollments = [e for e in enrollments if e.employee_id == employee_id]

        active_enrollments = len([e for e in enrollments if e.status in ("Enrolled", "In Progress")])
        completed_courses = len([e for e in enrollments if e.status == "Completed"])
        avg_prog = (sum(e.completion_percentage for e in enrollments) / len(enrollments)) if enrollments else 0.0

        certificates = await self.cert_repo.get_all()
        if employee_id:
            certificates = [c for c in certificates if c.employee_id == employee_id]

        skills = await self.skill_repo.get_all()
        if employee_id:
            skills = [s for s in skills if s.employee_id == employee_id]

        return TrainingDashboardSummary(
            total_courses=total_courses,
            active_enrollments=active_enrollments,
            completed_courses=completed_courses,
            total_certificates=len(certificates),
            avg_learning_progress=round(avg_prog, 2),
            skills_tracked=len(skills),
            skill_gap_percentage=15.5,
        )
