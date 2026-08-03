"""015_phase15_enterprise_data_analytics_mlops

Revision ID: i5i500j500ff
Revises: h4h400i400fe
Create Date: 2026-08-04 00:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i5i500j500ff'
down_revision: Union[str, None] = 'h4h400i400fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_table_if_not_exists(table_name: str, *columns_and_constraints, **kwargs):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        op.create_table(table_name, *columns_and_constraints, **kwargs)


def upgrade() -> None:
    # 1. datasets
    create_table_if_not_exists(
        'datasets',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('dataset_name', sa.String(length=255), nullable=False),
        sa.Column('dataset_type', sa.String(length=50), nullable=False, server_default='Tabular'),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('schema_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. dataset_versions
    create_table_if_not_exists(
        'dataset_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('dataset_id', sa.Uuid(), nullable=False),
        sa.Column('version_number', sa.String(length=50), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. data_lake_objects
    create_table_if_not_exists(
        'data_lake_objects',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('bucket_name', sa.String(length=255), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('format', sa.String(length=50), nullable=False, server_default='parquet'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. metadata_catalog
    create_table_if_not_exists(
        'metadata_catalog',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('column_definitions', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_name')
    )

    # 5. pipeline_jobs
    create_table_if_not_exists(
        'pipeline_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('pipeline_name', sa.String(length=255), nullable=False),
        sa.Column('schedule_cron', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. pipeline_runs
    create_table_if_not_exists(
        'pipeline_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('pipeline_id', sa.Uuid(), nullable=False),
        sa.Column('run_date', sa.DateTime(), nullable=False),
        sa.Column('execution_time_sec', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Success'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipeline_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. etl_jobs
    create_table_if_not_exists(
        'etl_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_name', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Idle'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_name')
    )

    # 8. etl_logs
    create_table_if_not_exists(
        'etl_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('etl_job_id', sa.Uuid(), nullable=False),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('log_message', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['etl_job_id'], ['etl_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. feature_groups
    create_table_if_not_exists(
        'feature_groups',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('group_name', sa.String(length=255), nullable=False),
        sa.Column('entity_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_name')
    )

    # 10. feature_store
    create_table_if_not_exists(
        'feature_store',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('feature_group_id', sa.Uuid(), nullable=True),
        sa.Column('feature_name', sa.String(length=255), nullable=False),
        sa.Column('feature_group', sa.String(length=100), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False, server_default='FLOAT'),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['feature_group_id'], ['feature_groups.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('feature_name')
    )

    # 11. feature_versions
    create_table_if_not_exists(
        'feature_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('feature_id', sa.Uuid(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['feature_id'], ['feature_store.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. ml_models
    create_table_if_not_exists(
        'ml_models',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('framework', sa.String(length=50), nullable=False, server_default='scikit-learn'),
        sa.Column('problem_type', sa.String(length=50), nullable=False, server_default='Classification'),
        sa.Column('current_version', sa.String(length=50), nullable=False, server_default='v1.0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Production'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name')
    )

    # 13. model_versions
    create_table_if_not_exists(
        'model_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_id', sa.Uuid(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('metrics', sa.Text(), nullable=False),
        sa.Column('artifact_path', sa.String(length=500), nullable=False),
        sa.Column('registered_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_id'], ['ml_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. model_registry
    create_table_if_not_exists(
        'model_registry',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_version_id', sa.Uuid(), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False, server_default='Production'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. experiments
    create_table_if_not_exists(
        'experiments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('experiment_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('framework', sa.String(length=50), nullable=False, server_default='PyTorch'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Completed'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('experiment_name')
    )

    # 16. experiment_runs
    create_table_if_not_exists(
        'experiment_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('experiment_id', sa.Uuid(), nullable=False),
        sa.Column('run_name', sa.String(length=255), nullable=False),
        sa.Column('hyperparameters', sa.Text(), nullable=False),
        sa.Column('metrics', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. training_jobs
    create_table_if_not_exists(
        'training_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_id', sa.Uuid(), nullable=False),
        sa.Column('dataset_id', sa.Uuid(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Completed'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_id'], ['ml_models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. training_runs
    create_table_if_not_exists(
        'training_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('loss', sa.Float(), nullable=False, server_default='0.01'),
        sa.Column('accuracy', sa.Float(), nullable=False, server_default='0.96'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['job_id'], ['training_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 19. prediction_jobs
    create_table_if_not_exists(
        'prediction_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_version_id', sa.Uuid(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False, server_default='Batch'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Completed'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 20. prediction_history
    create_table_if_not_exists(
        'prediction_history',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_version_id', sa.Uuid(), nullable=False),
        sa.Column('prediction_type', sa.String(length=50), nullable=False, server_default='Classification'),
        sa.Column('input_reference', sa.String(length=500), nullable=False),
        sa.Column('output_reference', sa.String(length=500), nullable=False),
        sa.Column('latency', sa.Float(), nullable=False, server_default='0.015'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.98'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 21. drift_reports
    create_table_if_not_exists(
        'drift_reports',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_id', sa.Uuid(), nullable=False),
        sa.Column('drift_type', sa.String(length=50), nullable=False, server_default='Data Drift'),
        sa.Column('drift_score', sa.Float(), nullable=False, server_default='0.02'),
        sa.Column('threshold', sa.Float(), nullable=False, server_default='0.05'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Normal'),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_id'], ['ml_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 22. model_monitoring
    create_table_if_not_exists(
        'model_monitoring',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('model_id', sa.Uuid(), nullable=False),
        sa.Column('avg_latency_ms', sa.Float(), nullable=False, server_default='15.0'),
        sa.Column('error_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['model_id'], ['ml_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 23. kpis
    create_table_if_not_exists(
        'kpis',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('kpi_name', sa.String(length=255), nullable=False),
        sa.Column('kpi_category', sa.String(length=100), nullable=False, server_default='Executive'),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('actual_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='USD'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 24. analytics_dashboards
    create_table_if_not_exists(
        'analytics_dashboards',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('dashboard_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 25. dashboard_widgets
    create_table_if_not_exists(
        'dashboard_widgets',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('dashboard_id', sa.Uuid(), nullable=False),
        sa.Column('widget_name', sa.String(length=255), nullable=False),
        sa.Column('widget_type', sa.String(length=50), nullable=False, server_default='BarChart'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['dashboard_id'], ['analytics_dashboards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 26. reports
    create_table_if_not_exists(
        'reports',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False, server_default='Executive Summary'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 27. scheduled_reports
    create_table_if_not_exists(
        'scheduled_reports',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('report_id', sa.Uuid(), nullable=False),
        sa.Column('cron_schedule', sa.String(length=100), nullable=False, server_default='0 8 * * 1'),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    pass
