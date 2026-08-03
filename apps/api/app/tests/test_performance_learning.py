import uuid
from datetime import date, datetime
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, status

from app.models.performance_learning_v9 import (
    Competency,
    CourseEnrollment,
    Goal,
    KeyResult,
    LearningCertificate,
    PerformanceFeedback,
    PerformanceReview,
    PerformanceReviewCycle,
    Phase9SkillMatrix,
    Phase9TrainingCourse,
)
from app.services.performance_learning import (
    CompetencyService,
    FeedbackService,
    GoalService,
    PerformanceService,
    TrainingService,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_goal_service_dates_validation(mock_db_session):
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = GoalService(mock_db_session)
    org_id = uuid.uuid4()
    emp_id = uuid.uuid4()

    from app.schemas.performance_learning import GoalCreate
    invalid_goal = GoalCreate(
        organization_id=org_id,
        employee_id=emp_id,
        title="Invalid Dates Goal",
        start_date=date(2026, 12, 31),
        end_date=date(2026, 1, 1),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_goal(invalid_goal)
    assert exc_info.value.status_code == 400
    assert "start_date cannot be after end_date" in exc_info.value.detail


@pytest.mark.asyncio
async def test_goal_crud_and_key_results(mock_db_session):
    service = GoalService(mock_db_session)
    org_id = uuid.uuid4()
    emp_id = uuid.uuid4()

    from app.schemas.performance_learning import GoalCreate, KeyResultCreate, KeyResultUpdate

    payload = GoalCreate(
        organization_id=org_id,
        employee_id=emp_id,
        title="Achieve 100% Sales Target Q3",
        description="Drive regional revenue expansion",
        goal_type="OKR",
        priority="High",
        weightage=100.0,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 9, 30),
        status="In Progress",
        key_results=[
            KeyResultCreate(
                title="Close 10 Enterprise Deals",
                target_value=10.0,
                current_value=0.0,
                measurement_unit="Deals",
            )
        ],
    )

    created_goal = Goal(
        id=uuid.uuid4(),
        organization_id=org_id,
        employee_id=emp_id,
        title=payload.title,
        description=payload.description,
        goal_type=payload.goal_type,
        priority=payload.priority,
        weightage=payload.weightage,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status,
        progress=0.0,
    )
    kr = KeyResult(
        id=uuid.uuid4(),
        goal_id=created_goal.id,
        title="Close 10 Enterprise Deals",
        target_value=10.0,
        current_value=0.0,
        measurement_unit="Deals",
        progress=0.0,
        status="Not Started",
    )
    created_goal.key_results = [kr]

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
        create_mock_execute_result(created_goal, [kr]),
    ]
    goal = await service.create_goal(payload)
    assert goal is not None
    assert goal.title == "Achieve 100% Sales Target Q3"

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(kr),
        create_mock_execute_result(kr),
        create_mock_execute_result(None, [kr]),
        create_mock_execute_result(created_goal),
    ]
    updated_kr = await service.update_key_result(kr.id, KeyResultUpdate(current_value=5.0))
    assert updated_kr.progress == 50.0


@pytest.mark.asyncio
async def test_review_cycle_and_360_feedback(mock_db_session):
    perf_service = PerformanceService(mock_db_session)
    feedback_service = FeedbackService(mock_db_session)
    org_id = uuid.uuid4()
    emp_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    from app.schemas.performance_learning import (
        PerformanceFeedbackCreate,
        PerformanceReviewCreate,
        PerformanceReviewCycleCreate,
    )

    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    cycle = await perf_service.create_cycle(
        PerformanceReviewCycleCreate(
            organization_id=org_id,
            name="2026 Annual Review",
            review_type="Annual",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status="Active",
        )
    )
    assert cycle is not None

    review_obj = PerformanceReview(
        id=uuid.uuid4(),
        employee_id=emp_id,
        review_cycle_id=cycle.id,
        reviewer_id=reviewer_id,
        status="Pending",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(cycle),
        create_mock_execute_result(review_obj),
    ]
    review = await perf_service.create_review(
        PerformanceReviewCreate(
            employee_id=emp_id,
            review_cycle_id=cycle.id,
            reviewer_id=reviewer_id,
            status="Pending",
        )
    )
    assert review is not None

    # Submit Self and Manager Feedbacks
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(review)

    fb_self = await feedback_service.submit_feedback(
        PerformanceFeedbackCreate(
            review_id=review.id,
            feedback_type="Self",
            comments="Exceeded target deliverables in H1",
            rating=4.5,
            submitted_by=emp_id,
        )
    )
    assert fb_self.rating == 4.5

    fb_mgr = await feedback_service.submit_feedback(
        PerformanceFeedbackCreate(
            review_id=review.id,
            feedback_type="Manager",
            comments="Strong performance and team leadership",
            rating=5.0,
            submitted_by=reviewer_id,
        )
    )
    assert fb_mgr.rating == 5.0

    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(review, [fb_self, fb_mgr])

    submitted_review = await perf_service.submit_review(review.id)
    assert submitted_review.status == "Submitted"
    assert submitted_review.overall_rating == 4.75
    assert submitted_review.overall_score == 95.0


@pytest.mark.asyncio
async def test_competencies_and_duplicate_prevention(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = CompetencyService(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.performance_learning import CompetencyCreate
    comp = await service.create_competency(
        CompetencyCreate(
            organization_id=org_id,
            name="Cloud Native Architecture",
            description="Expertise in Kubernetes and Docker",
            category="Technical",
        )
    )
    assert comp.name == "Cloud Native Architecture"

    mock_db_session.execute.return_value = create_mock_execute_result(comp)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_competency(
            CompetencyCreate(
                organization_id=org_id,
                name="Cloud Native Architecture",
                description="Duplicate competency name check",
                category="Technical",
            )
        )
    assert exc_info.value.status_code == 400
    assert "already exists in this organization" in exc_info.value.detail


@pytest.mark.asyncio
async def test_training_enrollment_and_auto_certificate(mock_db_session):
    service = TrainingService(mock_db_session)
    org_id = uuid.uuid4()
    emp_id = uuid.uuid4()

    from app.schemas.performance_learning import (
        CourseEnrollmentCreate,
        CourseEnrollmentUpdate,
        TrainingCourseCreate,
    )

    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    course = await service.create_course(
        TrainingCourseCreate(
            organization_id=org_id,
            course_name="Enterprise Security 2026",
            course_code="SEC-2026-X1",
            description="Compliance and ISO 27001 certification",
            duration_hours=5.0,
            difficulty="Advanced",
            category="Security",
        )
    )
    assert course is not None

    enrollment = CourseEnrollment(
        id=uuid.uuid4(),
        employee_id=emp_id,
        course_id=course.id,
        completion_percentage=0.0,
        status="Enrolled",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(course),
        create_mock_execute_result(None),
    ]
    created_enrollment = await service.enroll_employee(
        CourseEnrollmentCreate(employee_id=emp_id, course_id=course.id)
    )
    assert created_enrollment.status == "Enrolled"

    # Mock duplicate check
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(enrollment)
    with pytest.raises(HTTPException) as exc_info:
        await service.enroll_employee(
            CourseEnrollmentCreate(employee_id=emp_id, course_id=course.id)
        )
    assert exc_info.value.status_code == 400

    # Complete course -> expect auto certificate generation
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(enrollment, [])
    updated_enroll = await service.update_enrollment_progress(
        enrollment.id, CourseEnrollmentUpdate(completion_percentage=100.0)
    )
    assert updated_enroll.status == "Completed"
