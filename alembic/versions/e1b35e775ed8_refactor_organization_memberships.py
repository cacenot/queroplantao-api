"""refactor_organization_memberships

Revision ID: e1b35e775ed8
Revises: c724fe9c3d80
Create Date: 2026-01-20 17:29:20.303602

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e1b35e775ed8"
down_revision: Union[str, Sequence[str], None] = "c724fe9c3d80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create organization_memberships table (replaces organization_members + organization_member_roles)
    op.create_table(
        "organization_memberships",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default="now()",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("granted_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "organization_id",
            "role_id",
            name="uq_org_memberships_user_org_role",
        ),
    )

    # Drop old organization_members table
    op.drop_table("organization_members")

    # Drop unused member_role enum type
    op.execute("DROP TYPE IF EXISTS member_role;")

    # Seed organization roles
    op.execute("""
        INSERT INTO roles (id, code, name, description, is_system, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'ORG_OWNER', 'Organization Owner', 'Full access, can delete organization', true, now(), now()),
            (gen_random_uuid(), 'ORG_ADMIN', 'Organization Admin', 'Manage members and settings', true, now(), now()),
            (gen_random_uuid(), 'ORG_MANAGER', 'Organization Manager', 'Manage schedules and shifts', true, now(), now()),
            (gen_random_uuid(), 'ORG_SCHEDULER', 'Organization Scheduler', 'Create and edit schedules', true, now(), now()),
            (gen_random_uuid(), 'ORG_VIEWER', 'Organization Viewer', 'Read-only access', true, now(), now())
        ON CONFLICT (code) DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove seeded organization roles
    op.execute("""
        DELETE FROM roles WHERE code IN (
            'ORG_OWNER', 'ORG_ADMIN', 'ORG_MANAGER', 'ORG_SCHEDULER', 'ORG_VIEWER'
        );
    """)

    # Recreate member_role enum
    member_role_enum = sa.Enum(
        "OWNER", "ADMIN", "MANAGER", "SCHEDULER", "VIEWER", name="member_role"
    )
    member_role_enum.create(op.get_bind())

    # Recreate organization_members table
    op.create_table(
        "organization_members",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("created_by", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("updated_by", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column(
            "role",
            postgresql.ENUM(
                "OWNER", "ADMIN", "MANAGER", "SCHEDULER", "VIEWER", name="member_role"
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "invited_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "accepted_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("organization_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("organization_members_organization_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("organization_members_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("organization_members_pkey")),
        sa.UniqueConstraint(
            "user_id",
            "organization_id",
            name=op.f("uq_organization_members_user_org"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(
        op.f("ix_organization_members_user_id"),
        "organization_members",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_members_organization_id"),
        "organization_members",
        ["organization_id"],
        unique=False,
    )
    op.drop_table("organization_memberships")
    # ### end Alembic commands ###
