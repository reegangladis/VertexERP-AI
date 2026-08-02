"""Merge migration heads

Revision ID: 893475360466
Revises: ('phase_16_monitoring', 'phase_8_mrp_platform')
Create Date: 2026-08-02 17:54:40.133669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '893475360466'
down_revision: Union[str, None] = ('phase_16_monitoring', 'phase_8_mrp_platform')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
