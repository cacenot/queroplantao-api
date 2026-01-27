"""Remove screening template.

Revision ID: a1b2c3d4e5f7
Revises: fa4b42729c2d
Create Date: 2026-01-25 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: str | None = "fa4b42729c2d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove template_id FK and add client_validation_required."""
    # 1. Drop the FK constraint first
    op.drop_constraint(
        "screening_processes_template_id_fkey",
        "screening_processes",
        type_="foreignkey",
    )

    # 2. Drop the template_id column
    op.drop_column("screening_processes", "template_id")

    # 3. Add client_validation_required column
    op.add_column(
        "screening_processes",
        sa.Column(
            "client_validation_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # 4. Drop indexes on screening_templates
    op.drop_index(
        "ix_screening_templates_organization_id", table_name="screening_templates"
    )
    op.drop_index(
        "ix_screening_templates_professional_type", table_name="screening_templates"
    )
    op.drop_index(
        "uq_screening_templates_org_default", table_name="screening_templates"
    )
    op.drop_index("uq_screening_templates_org_name", table_name="screening_templates")

    # 5. Drop screening_template_steps table first (has FK to screening_templates)
    op.drop_table("screening_template_steps")

    # 6. Drop screening_templates table
    op.drop_table("screening_templates")


def downgrade() -> None:
    """Restore template tables and template_id FK."""
    # 1. Recreate screening_templates table
    op.create_table(
        "screening_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("professional_type", sa.String(length=50), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_screening_templates_organization_id",
        "screening_templates",
        ["organization_id"],
    )
    op.create_index(
        "ix_screening_templates_professional_type",
        "screening_templates",
        ["professional_type"],
    )
    op.create_index(
        "uq_screening_templates_org_default",
        "screening_templates",
        ["organization_id", "is_default"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND is_default = true"),
    )
    op.create_index(
        "uq_screening_templates_org_name",
        "screening_templates",
        ["organization_id", "name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # 2. Recreate screening_template_steps table
    op.create_table(
        "screening_template_steps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=False),
        sa.Column(
            "step_type",
            sa.Enum(
                "CONVERSATION",
                "PROFESSIONAL_DATA",
                "QUALIFICATION",
                "SPECIALTY",
                "EDUCATION",
                "DOCUMENTS",
                "COMPANY",
                "BANK_ACCOUNT",
                "DOCUMENT_REVIEW",
                "SUPERVISOR_REVIEW",
                "INTERVIEW",
                "CLIENT_VALIDATION",
                name="step_type",
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["screening_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Drop client_validation_required column
    op.drop_column("screening_processes", "client_validation_required")

    # 4. Add template_id column back
    op.add_column(
        "screening_processes",
        sa.Column("template_id", sa.UUID(), nullable=False),
    )

    # 5. Add FK constraint back
    op.create_foreign_key(
        "screening_processes_template_id_fkey",
        "screening_processes",
        "screening_templates",
        ["template_id"],
        ["id"],
    )
