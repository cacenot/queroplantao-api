"""Add screening alerts support.

Revision ID: 000000000009
Revises: 000000000008
Create Date: 2026-01-28 21:00:00.000000

This migration:
1. Adds PENDING_SUPERVISOR to screening_status enum
2. Creates screening_alerts table for supervisor alerts
3. Adds supervisor_id column to screening_processes
4. Drops screening_supervisor_review_steps table (replaced by alerts)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000000000009"
down_revision: Union[str, Sequence[str], None] = "000000000008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add PENDING_SUPERVISOR to screening_status enum
    op.execute(
        "ALTER TYPE screening_status ADD VALUE IF NOT EXISTS 'PENDING_SUPERVISOR'"
    )

    # 2. Create alert_category enum
    alert_category_enum = postgresql.ENUM(
        "DOCUMENT",
        "DATA",
        "BEHAVIOR",
        "COMPLIANCE",
        "QUALIFICATION",
        "OTHER",
        name="alert_category",
        create_type=False,
    )
    alert_category_enum.create(op.get_bind(), checkfirst=True)

    # 3. Create screening_alerts table
    op.create_table(
        "screening_alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("process_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(length=2000), nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(
                "DOCUMENT",
                "DATA",
                "BEHAVIOR",
                "COMPLIANCE",
                "QUALIFICATION",
                "OTHER",
                name="alert_category",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("notes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_resolved", sa.Boolean(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["process_id"],
            ["screening_processes.id"],
            name=op.f("fk_screening_alerts_process_id_screening_processes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_screening_alerts")),
    )

    # Create indexes
    op.create_index(
        "ix_screening_alerts_process_id",
        "screening_alerts",
        ["process_id"],
        unique=False,
    )
    op.create_index(
        "ix_screening_alerts_unresolved",
        "screening_alerts",
        ["process_id", "is_resolved"],
        unique=False,
        postgresql_where=sa.text("is_resolved = FALSE"),
    )
    op.create_index(
        "ix_screening_alerts_category",
        "screening_alerts",
        ["category"],
        unique=False,
    )

    # 4. Add supervisor_id to screening_processes
    op.add_column(
        "screening_processes",
        sa.Column(
            "supervisor_id",
            sa.Uuid(),
            nullable=True,  # Initially nullable for existing data
            comment="Supervisor responsible for reviewing alerts",
        ),
    )

    # 5. Drop screening_supervisor_review_steps table
    op.drop_table("screening_supervisor_review_steps")

    # 6. Update role names to PT-BR
    op.execute("""
        UPDATE roles SET name = 'Proprietário' WHERE code = 'ORG_OWNER';
        UPDATE roles SET name = 'Administrador' WHERE code = 'ORG_ADMIN';
        UPDATE roles SET name = 'Gestor' WHERE code = 'ORG_MANAGER';
        UPDATE roles SET name = 'Escalista' WHERE code = 'ORG_SCHEDULER';
        UPDATE roles SET name = 'Visualizador' WHERE code = 'ORG_VIEWER';
    """)


def downgrade() -> None:
    # 1. Recreate screening_supervisor_review_steps table
    # Note: We need to recreate the step_status enum value check
    op.create_table(
        "screening_supervisor_review_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("process_id", sa.Uuid(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", name="step_status"
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", sa.Uuid(), nullable=True),
        sa.Column("supervisor_notes", sa.String(length=2000), nullable=True),
        sa.ForeignKeyConstraint(
            ["process_id"],
            ["screening_processes.id"],
            name="fk_screening_supervisor_review_steps_process_id_screening_proc",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_screening_supervisor_review_steps"),
    )
    op.create_index(
        "ix_screening_supervisor_review_steps_process_id",
        "screening_supervisor_review_steps",
        ["process_id"],
        unique=True,
    )

    # 2. Remove supervisor_id from screening_processes
    op.drop_column("screening_processes", "supervisor_id")

    # 3. Drop screening_alerts table
    op.drop_index("ix_screening_alerts_category", table_name="screening_alerts")
    op.drop_index("ix_screening_alerts_unresolved", table_name="screening_alerts")
    op.drop_index("ix_screening_alerts_process_id", table_name="screening_alerts")
    op.drop_table("screening_alerts")

    # 4. Drop alert_category enum
    op.execute("DROP TYPE IF EXISTS alert_category")

    # Note: Cannot remove PENDING_SUPERVISOR from screening_status enum in PostgreSQL
    # Enum values cannot be removed, only added
