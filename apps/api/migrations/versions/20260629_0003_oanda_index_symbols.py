"""Assign index CFDs to the Oanda market-data provider.

Revision ID: 20260629_0003
Revises: 20260619_0002
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260629_0003"
down_revision: str | None = "20260619_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE symbols SET exchange = 'oanda', updated_at = now() "
        "WHERE exchange = 'index' AND symbol IN ('SP500', 'US100')"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE symbols SET exchange = 'index', updated_at = now() "
        "WHERE exchange = 'oanda' AND symbol IN ('SP500', 'US100')"
    )
