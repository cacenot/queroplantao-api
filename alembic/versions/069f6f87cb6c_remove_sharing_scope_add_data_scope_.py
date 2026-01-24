"""remove_sharing_scope_add_data_scope_policy

Revision ID: 069f6f87cb6c
Revises: eec8aeed7c2e
Create Date: 2026-01-24 01:22:39.146959

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "069f6f87cb6c"
down_revision: Union[str, Sequence[str], None] = "eec8aeed7c2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove sharing_scope column from organizations
    op.drop_column("organizations", "sharing_scope")

    # Drop the sharing_scope enum type
    sa.Enum(name="sharing_scope").drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the sharing_scope enum type
    sharing_scope_enum = postgresql.ENUM(
        "NONE",
        "PROFESSIONALS",
        "SCHEDULES",
        "FULL",
        name="sharing_scope",
        create_type=False,
    )
    sharing_scope_enum.create(op.get_bind(), checkfirst=True)

    # Add back the sharing_scope column
    op.add_column(
        "organizations",
        sa.Column(
            "sharing_scope",
            postgresql.ENUM(
                "NONE",
                "PROFESSIONALS",
                "SCHEDULES",
                "FULL",
                name="sharing_scope",
                create_type=False,
            ),
            autoincrement=False,
            nullable=False,
            server_default="NONE",
        ),
    )
