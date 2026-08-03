"""009_phase9_enterprise_learning_and_development

Revision ID: c9c900d900f9
Revises: b8b800c800e8
Create Date: 2026-08-03 12:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9c900d900f9'
down_revision: Union[str, None] = 'b8b800c800e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. training_courses
    op.create_table(
        'training_courses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('course_code', sa.String(length=50), nullable=False),
        sa.Column('course_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='General'),
        sa.Column('difficulty_level', sa.String(length=50), nullable=False, server_default='Intermediate'),
        sa.Column('duration_hours', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('delivery_mode', sa.String(length=50), nullable=False, server_default='Online'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_courses_course_code'), 'training_courses', ['course_code'], unique=False)
    op.create_index(op.f('ix_training_courses_id'), 'training_courses', ['id'], unique=False)
    op.create_index(op.f('ix_training_courses_organization_id'), 'training_courses', ['organization_id'], unique=False)

    # 2. course_modules
    op.create_table(
        'course_modules',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('module_name', sa.String(length=255), nullable=False),
        sa.Column('module_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('content_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_modules_course_id'), 'course_modules', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_modules_id'), 'course_modules', ['id'], unique=False)

    # 3. learning_paths
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('path_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_paths_id'), 'learning_paths', ['id'], unique=False)
    op.create_index(op.f('ix_learning_paths_organization_id'), 'learning_paths', ['organization_id'], unique=False)

    # 4. learning_path_courses
    op.create_table(
        'learning_path_courses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('learning_path_id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_path_courses_course_id'), 'learning_path_courses', ['course_id'], unique=False)
    op.create_index(op.f('ix_learning_path_courses_id'), 'learning_path_courses', ['id'], unique=False)
    op.create_index(op.f('ix_learning_path_courses_learning_path_id'), 'learning_path_courses', ['learning_path_id'], unique=False)

    # 5. employee_trainings
    op.create_table(
        'employee_trainings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Assigned'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_trainings_course_id'), 'employee_trainings', ['course_id'], unique=False)
    op.create_index(op.f('ix_employee_trainings_employee_id'), 'employee_trainings', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_trainings_id'), 'employee_trainings', ['id'], unique=False)

    # 6. lms_certifications
    op.create_table(
        'lms_certifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_training_id', sa.Uuid(), nullable=False),
        sa.Column('certificate_number', sa.String(length=100), nullable=False),
        sa.Column('issued_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_training_id'], ['employee_trainings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_certifications_certificate_number'), 'lms_certifications', ['certificate_number'], unique=False)
    op.create_index(op.f('ix_lms_certifications_employee_training_id'), 'lms_certifications', ['employee_training_id'], unique=False)
    op.create_index(op.f('ix_lms_certifications_id'), 'lms_certifications', ['id'], unique=False)

    # 7. assessments
    op.create_table(
        'assessments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('assessment_name', sa.String(length=255), nullable=False),
        sa.Column('passing_score', sa.Float(), nullable=False, server_default='70.0'),
        sa.Column('total_marks', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_course_id'), 'assessments', ['course_id'], unique=False)
    op.create_index(op.f('ix_assessments_id'), 'assessments', ['id'], unique=False)

    # 8. assessment_attempts
    op.create_table(
        'assessment_attempts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('assessment_id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_attempts_assessment_id'), 'assessment_attempts', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assessment_attempts_employee_id'), 'assessment_attempts', ['employee_id'], unique=False)
    op.create_index(op.f('ix_assessment_attempts_id'), 'assessment_attempts', ['id'], unique=False)

    # 9. instructors
    op.create_table(
        'instructors',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=True),
        sa.Column('specialization', sa.String(length=255), nullable=False),
        sa.Column('experience_years', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('bio', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_instructors_id'), 'instructors', ['id'], unique=False)
    op.create_index(op.f('ix_instructors_organization_id'), 'instructors', ['organization_id'], unique=False)

    # 10. training_sessions
    op.create_table(
        'training_sessions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('instructor_id', sa.Uuid(), nullable=True),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.String(length=20), nullable=False),
        sa.Column('end_time', sa.String(length=20), nullable=False),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instructor_id'], ['instructors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_sessions_course_id'), 'training_sessions', ['course_id'], unique=False)
    op.create_index(op.f('ix_training_sessions_id'), 'training_sessions', ['id'], unique=False)

    # 11. lms_employee_skills
    op.create_table(
        'lms_employee_skills',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('skill_level', sa.String(length=50), nullable=False, server_default='Intermediate'),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_updated', sa.Date(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_employee_skills_employee_id'), 'lms_employee_skills', ['employee_id'], unique=False)
    op.create_index(op.f('ix_lms_employee_skills_id'), 'lms_employee_skills', ['id'], unique=False)

    # 12. skill_matrix
    op.create_table(
        'skill_matrix',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('designation_id', sa.Uuid(), nullable=True),
        sa.Column('required_skill', sa.String(length=100), nullable=False),
        sa.Column('minimum_level', sa.String(length=50), nullable=False, server_default='Intermediate'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['designation_id'], ['designations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_matrix_id'), 'skill_matrix', ['id'], unique=False)
    op.create_index(op.f('ix_skill_matrix_organization_id'), 'skill_matrix', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_table('skill_matrix')
    op.drop_table('lms_employee_skills')
    op.drop_table('training_sessions')
    op.drop_table('instructors')
    op.drop_table('assessment_attempts')
    op.drop_table('assessments')
    op.drop_table('lms_certifications')
    op.drop_table('employee_trainings')
    op.drop_table('learning_path_courses')
    op.drop_table('learning_paths')
    op.drop_table('course_modules')
    op.drop_table('training_courses')
