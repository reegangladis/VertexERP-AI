"""Phase 6 Inventory Platform Migration — stock_transfers and stock_transfer_items tables.

Revision ID: phase_6_inventory_platform
Revises: phase_5_crm_platform
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sqa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers
revision = 'phase_6_inventory_platform'
down_revision = 'phase_5_crm_platform'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. stock_transfers table
    op.create_table(
        'stock_transfers',
        sqa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sqa.Column('organization_id', psql.UUID(as_uuid=True), sqa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('transfer_number', sqa.String(length=100), nullable=False, index=True),
        sqa.Column('source_warehouse_id', psql.UUID(as_uuid=True), sqa.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('target_warehouse_id', psql.UUID(as_uuid=True), sqa.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('status', sqa.String(length=50), nullable=False, server_default='draft'),
        sqa.Column('requested_by_id', psql.UUID(as_uuid=True), sqa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sqa.Column('approved_by_id', psql.UUID(as_uuid=True), sqa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sqa.Column('created_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('updated_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('deleted_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('is_deleted', sqa.Boolean(), server_default='false', nullable=False),
    )

    # 2. stock_transfer_items table
    op.create_table(
        'stock_transfer_items',
        sqa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sqa.Column('stock_transfer_id', psql.UUID(as_uuid=True), sqa.ForeignKey('stock_transfers.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('product_id', psql.UUID(as_uuid=True), sqa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('quantity', sqa.Integer(), nullable=False),
        sqa.Column('created_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('updated_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('deleted_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('is_deleted', sqa.Boolean(), server_default='false', nullable=False),
    )

def downgrade() -> None:
    op.drop_table('stock_transfer_items')
    op.drop_table('stock_transfers')
