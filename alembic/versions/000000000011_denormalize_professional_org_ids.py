"""Denormalize organization_id on professional tables.

Revision ID: 000000000011
Revises: 000000000010
Create Date: 2026-02-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "000000000011"
down_revision: str | Sequence[str] | None = "000000000010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add organization_id columns
    op.add_column(
        "professional_documents",
        sa.Column("organization_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "professional_educations",
        sa.Column("organization_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "professional_companies",
        sa.Column("organization_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "professional_change_diffs",
        sa.Column("organization_id", sa.UUID(), nullable=True),
    )

    # Foreign keys
    op.create_foreign_key(
        "fk_professional_documents_organization_id",
        "professional_documents",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_professional_educations_organization_id",
        "professional_educations",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_professional_companies_organization_id",
        "professional_companies",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_professional_change_diffs_organization_id",
        "professional_change_diffs",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    # Backfill organization_id
    op.execute(
        """
        UPDATE professional_documents pd
        SET organization_id = op.organization_id
        FROM organization_professionals op
        WHERE pd.organization_professional_id = op.id
        """
    )
    op.execute(
        """
        UPDATE professional_educations pe
        SET organization_id = pq.organization_id
        FROM professional_qualifications pq
        WHERE pe.qualification_id = pq.id
        """
    )
    op.execute(
        """
        UPDATE professional_companies pc
        SET organization_id = op.organization_id
        FROM organization_professionals op
        WHERE pc.organization_professional_id = op.id
        """
    )
    op.execute(
        """
        UPDATE professional_change_diffs pcd
        SET organization_id = pv.organization_id
        FROM professional_versions pv
        WHERE pcd.version_id = pv.id
        """
    )

    # Make columns required
    op.alter_column("professional_documents", "organization_id", nullable=False)
    op.alter_column("professional_educations", "organization_id", nullable=False)
    op.alter_column("professional_companies", "organization_id", nullable=False)
    op.alter_column("professional_change_diffs", "organization_id", nullable=False)

    # Indexes
    op.create_index(
        "idx_professional_documents_org",
        "professional_documents",
        ["organization_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_professional_educations_org",
        "professional_educations",
        ["organization_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_professional_companies_org",
        "professional_companies",
        ["organization_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_professional_change_diffs_organization_id",
        "professional_change_diffs",
        ["organization_id"],
    )
    op.create_index(
        "ix_professional_change_diffs_org_version",
        "professional_change_diffs",
        ["organization_id", "version_id"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_professional_change_diffs_org_version",
        table_name="professional_change_diffs",
    )
    op.drop_index(
        "ix_professional_change_diffs_organization_id",
        table_name="professional_change_diffs",
    )
    op.drop_index(
        "idx_professional_companies_org",
        table_name="professional_companies",
    )
    op.drop_index(
        "idx_professional_educations_org",
        table_name="professional_educations",
    )
    op.drop_index(
        "idx_professional_documents_org",
        table_name="professional_documents",
    )

    # Drop foreign keys
    op.drop_constraint(
        "fk_professional_change_diffs_organization_id",
        "professional_change_diffs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_professional_companies_organization_id",
        "professional_companies",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_professional_educations_organization_id",
        "professional_educations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_professional_documents_organization_id",
        "professional_documents",
        type_="foreignkey",
    )

    # Drop columns
    op.drop_column("professional_change_diffs", "organization_id")
    op.drop_column("professional_companies", "organization_id")
    op.drop_column("professional_educations", "organization_id")
    op.drop_column("professional_documents", "organization_id")
