"""003_phase3_organization_structure

Revision ID: 30edc2461469
Revises: 5a2cc27eb65a
Create Date: 2026-08-03 02:01:04.819842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30edc2461469'
down_revision: Union[str, None] = '5a2cc27eb65a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. business_units
    op.create_table('business_units',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('parent_business_unit_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('manager_uuid', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_business_unit_id'], ['business_units.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_units_code'), 'business_units', ['code'], unique=False)
    op.create_index(op.f('ix_business_units_id'), 'business_units', ['id'], unique=False)
    op.create_index(op.f('ix_business_units_organization_id'), 'business_units', ['organization_id'], unique=False)

    # 2. departments
    op.create_table('departments',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('parent_department_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('manager_uuid', sa.Uuid(), nullable=True),
    sa.Column('budget', sa.Float(), nullable=False, server_default='0.0'),
    sa.Column('cost_center', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=False)
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_organization_id'), 'departments', ['organization_id'], unique=False)
    op.create_index(op.f('ix_departments_parent_department_id'), 'departments', ['parent_department_id'], unique=False)

    # 3. designations
    op.create_table('designations',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('job_level', sa.String(), nullable=True),
    sa.Column('grade', sa.String(), nullable=True),
    sa.Column('reporting_level', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_designations_code'), 'designations', ['code'], unique=False)
    op.create_index(op.f('ix_designations_id'), 'designations', ['id'], unique=False)
    op.create_index(op.f('ix_designations_organization_id'), 'designations', ['organization_id'], unique=False)

    # 4. teams
    op.create_table('teams',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('department_id', sa.Uuid(), nullable=True),
    sa.Column('business_unit_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('team_type', sa.String(), nullable=True, server_default='cross_functional'),
    sa.Column('manager_uuid', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['business_unit_id'], ['business_units.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_business_unit_id'), 'teams', ['business_unit_id'], unique=False)
    op.create_index(op.f('ix_teams_code'), 'teams', ['code'], unique=False)
    op.create_index(op.f('ix_teams_department_id'), 'teams', ['department_id'], unique=False)
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_organization_id'), 'teams', ['organization_id'], unique=False)

    # 5. team_members
    op.create_table('team_members',
    sa.Column('team_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.String(), nullable=False, server_default='member'),
    sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)
    op.create_index(op.f('ix_team_members_team_id'), 'team_members', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_members_user_id'), 'team_members', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_team_members_user_id'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_team_id'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')
    op.drop_index(op.f('ix_teams_organization_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_department_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_code'), table_name='teams')
    op.drop_index(op.f('ix_teams_business_unit_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_designations_organization_id'), table_name='designations')
    op.drop_index(op.f('ix_designations_id'), table_name='designations')
    op.drop_index(op.f('ix_designations_code'), table_name='designations')
    op.drop_table('designations')
    op.drop_index(op.f('ix_departments_parent_department_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_organization_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_code'), table_name='departments')
    op.drop_table('departments')
    op.drop_index(op.f('ix_business_units_organization_id'), table_name='business_units')
    op.drop_index(op.f('ix_business_units_id'), table_name='business_units')
    op.drop_index(op.f('ix_business_units_code'), table_name='business_units')
    op.drop_table('business_units')
