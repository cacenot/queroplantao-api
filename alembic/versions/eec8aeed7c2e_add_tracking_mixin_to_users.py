"""add_tracking_mixin_to_users

Revision ID: eec8aeed7c2e
Revises: 601b7033d64c
Create Date: 2026-01-23 11:16:06.438616

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "eec8aeed7c2e"
down_revision: Union[str, Sequence[str], None] = "601b7033d64c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add TrackingMixin columns to users table
    op.add_column("users", sa.Column("created_by", sa.Uuid(), nullable=True))
    op.add_column("users", sa.Column("updated_by", sa.Uuid(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "updated_by")
    op.drop_column("users", "created_by")
