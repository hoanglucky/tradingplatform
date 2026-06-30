"""Add persisted multi-timeframe layout.

Revision ID: 20260630_0005
Revises: 20260629_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260630_0005"
down_revision: str | None = "20260629_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column("multi_timeframe_layout", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "multi_timeframe_layout")
