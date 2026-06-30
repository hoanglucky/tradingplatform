"""add candle quality metadata

Revision ID: 20260630_0006
Revises: 20260630_0005
Create Date: 2026-06-30 00:00:00+00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260630_0006"
down_revision = "20260630_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candles", sa.Column("partial", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("candles", sa.Column("complete", sa.Boolean(), server_default="true", nullable=False))
    op.add_column("candles", sa.Column("source_count", sa.Integer(), nullable=True))
    op.add_column("candles", sa.Column("expected_source_count", sa.Integer(), nullable=True))
    op.add_column("candles", sa.Column("missing_source_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("candles", "missing_source_count")
    op.drop_column("candles", "expected_source_count")
    op.drop_column("candles", "source_count")
    op.drop_column("candles", "complete")
    op.drop_column("candles", "partial")
