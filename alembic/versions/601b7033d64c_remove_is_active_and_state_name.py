"""remove_is_active_and_state_name

Revision ID: 601b7033d64c
Revises: 1c3fbae705d9
Create Date: 2026-01-22 22:41:30.227483

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "601b7033d64c"
down_revision: Union[str, Sequence[str], None] = "1c3fbae705d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove is_active column and related indexes from organization_professionals
    op.drop_index(
        "idx_organization_professionals_is_active",
        table_name="organization_professionals",
        postgresql_where="(deleted_at IS NULL)",
    )
    op.drop_index(
        "idx_organization_professionals_org_active",
        table_name="organization_professionals",
        postgresql_where="(deleted_at IS NULL)",
    )
    op.drop_column("organization_professionals", "is_active")

    # Remove state_name column from all tables that use AddressMixin
    op.drop_column("organization_professionals", "state_name")
    op.drop_column("companies", "state_name")
    op.drop_column("units", "state_name")


def downgrade() -> None:
    """Downgrade schema."""
    # Restore state_name column to all tables that use AddressMixin
    op.add_column(
        "units", sa.Column("state_name", sa.VARCHAR(length=100), nullable=True)
    )
    op.add_column(
        "companies", sa.Column("state_name", sa.VARCHAR(length=100), nullable=True)
    )
    op.add_column(
        "organization_professionals",
        sa.Column("state_name", sa.VARCHAR(length=100), nullable=True),
    )

    # Restore is_active column and indexes to organization_professionals
    op.add_column(
        "organization_professionals",
        sa.Column("is_active", sa.BOOLEAN(), nullable=False, server_default="true"),
    )
    op.create_index(
        "idx_organization_professionals_is_active",
        "organization_professionals",
        ["is_active"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_organization_professionals_org_active",
        "organization_professionals",
        ["organization_id", "is_active"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
