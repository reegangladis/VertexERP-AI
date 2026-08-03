"""008_phase8_enterprise_recruitment_platform

Revision ID: b8b800c800e8
Revises: a7a700b700d7
Create Date: 2026-08-03 12:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8b800c800e8'
down_revision: Union[str, None] = 'a7a700b700d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. recruitment_jobs
    op.create_table(
        'recruitment_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('department_id', sa.Uuid(), nullable=True),
        sa.Column('designation_id', sa.Uuid(), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('job_code', sa.String(length=50), nullable=False),
        sa.Column('employment_type', sa.String(length=50), nullable=False, server_default='Full-Time'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('experience_required', sa.String(length=100), nullable=True),
        sa.Column('salary_min', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('salary_max', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('vacancies', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('description', sa.String(length=4000), nullable=True),
        sa.Column('requirements', sa.String(length=4000), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Open'),
        sa.Column('opening_date', sa.Date(), nullable=True),
        sa.Column('closing_date', sa.Date(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['designation_id'], ['designations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recruitment_jobs_id'), 'recruitment_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_recruitment_jobs_job_code'), 'recruitment_jobs', ['job_code'], unique=False)
    op.create_index(op.f('ix_recruitment_jobs_organization_id'), 'recruitment_jobs', ['organization_id'], unique=False)

    # 2. candidates
    op.create_table(
        'candidates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('linkedin_url', sa.String(length=255), nullable=True),
        sa.Column('github_url', sa.String(length=255), nullable=True),
        sa.Column('portfolio_url', sa.String(length=255), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('current_company', sa.String(length=255), nullable=True),
        sa.Column('current_designation', sa.String(length=255), nullable=True),
        sa.Column('experience_years', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expected_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notice_period', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='New'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'], unique=False)
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    op.create_index(op.f('ix_candidates_organization_id'), 'candidates', ['organization_id'], unique=False)

    # 3. applications
    op.create_table(
        'applications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('candidate_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('applied_date', sa.Date(), nullable=False),
        sa.Column('application_source', sa.String(length=50), nullable=False, server_default='Website'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Applied'),
        sa.Column('resume_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('screening_notes', sa.String(length=1000), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['recruitment_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_candidate_id'), 'applications', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'], unique=False)

    # 4. interview_rounds
    op.create_table(
        'interview_rounds',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('round_name', sa.String(length=100), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('interviewer_id', sa.Uuid(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Scheduled'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interviewer_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_rounds_application_id'), 'interview_rounds', ['application_id'], unique=False)
    op.create_index(op.f('ix_interview_rounds_id'), 'interview_rounds', ['id'], unique=False)

    # 5. interview_feedback
    op.create_table(
        'interview_feedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('interview_round_id', sa.Uuid(), nullable=False),
        sa.Column('technical_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('communication_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('problem_solving_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('culture_fit_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recommendation', sa.String(length=30), nullable=False, server_default='Hire'),
        sa.Column('comments', sa.String(length=1000), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_round_id'], ['interview_rounds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_feedback_id'), 'interview_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_interview_feedback_interview_round_id'), 'interview_feedback', ['interview_round_id'], unique=False)

    # 6. job_offers
    op.create_table(
        'job_offers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('offered_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('joining_bonus', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('joining_date', sa.Date(), nullable=False),
        sa.Column('offer_letter_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Draft'),
        sa.Column('offered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_offers_application_id'), 'job_offers', ['application_id'], unique=False)
    op.create_index(op.f('ix_job_offers_id'), 'job_offers', ['id'], unique=False)

    # 7. candidate_documents
    op.create_table(
        'candidate_documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('candidate_id', sa.Uuid(), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidate_documents_candidate_id'), 'candidate_documents', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_candidate_documents_id'), 'candidate_documents', ['id'], unique=False)

    # 8. onboarding_tasks
    op.create_table(
        'onboarding_tasks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('offer_id', sa.Uuid(), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('assigned_to', sa.Uuid(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='Pending'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to'], ['employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['offer_id'], ['job_offers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_onboarding_tasks_id'), 'onboarding_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_onboarding_tasks_offer_id'), 'onboarding_tasks', ['offer_id'], unique=False)

    # 9. recruitment_agencies
    op.create_table(
        'recruitment_agencies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('agency_name', sa.String(length=255), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recruitment_agencies_id'), 'recruitment_agencies', ['id'], unique=False)
    op.create_index(op.f('ix_recruitment_agencies_organization_id'), 'recruitment_agencies', ['organization_id'], unique=False)

    # 10. recruitment_pipeline_logs
    op.create_table(
        'recruitment_pipeline_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('previous_stage', sa.String(length=50), nullable=False),
        sa.Column('new_stage', sa.String(length=50), nullable=False),
        sa.Column('changed_by', sa.Uuid(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recruitment_pipeline_logs_application_id'), 'recruitment_pipeline_logs', ['application_id'], unique=False)
    op.create_index(op.f('ix_recruitment_pipeline_logs_id'), 'recruitment_pipeline_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('recruitment_pipeline_logs')
    op.drop_table('recruitment_agencies')
    op.drop_table('onboarding_tasks')
    op.drop_table('candidate_documents')
    op.drop_table('job_offers')
    op.drop_table('interview_feedback')
    op.drop_table('interview_rounds')
    op.drop_table('applications')
    op.drop_table('candidates')
    op.drop_table('recruitment_jobs')
