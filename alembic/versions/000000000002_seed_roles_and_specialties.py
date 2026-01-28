"""seed_roles_and_specialties

Revision ID: 000000000002
Revises: a4d50683ad2a
Create Date: 2026-01-27 21:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000002"
down_revision: Union[str, Sequence[str], None] = "a4d50683ad2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed roles and specialties."""
    connection = op.get_bind()

    # Seed organization roles
    connection.execute(
        sa.text("""
        INSERT INTO roles (id, code, name, description, is_system, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'ORG_OWNER', 'Organization Owner', 'Full access, can delete organization', true, now(), now()),
            (gen_random_uuid(), 'ORG_ADMIN', 'Organization Admin', 'Manage members and settings', true, now(), now()),
            (gen_random_uuid(), 'ORG_MANAGER', 'Organization Manager', 'Manage schedules and shifts', true, now(), now()),
            (gen_random_uuid(), 'ORG_SCHEDULER', 'Organization Scheduler', 'Create and edit schedules', true, now(), now()),
            (gen_random_uuid(), 'ORG_VIEWER', 'Organization Viewer', 'Read-only access', true, now(), now())
        ON CONFLICT (code) DO NOTHING;
    """)
    )

    # Seed medical specialties
    connection.execute(
        sa.text("""
        INSERT INTO specialties (id, code, name, created_at, updated_at)
        VALUES
            ('517fa123-4da4-4a3c-abef-792c084e8500', 'CARDIOLOGIA', 'Cardiologia', now(), now()),
            ('2d36831d-489e-4106-80e5-03520015be16', 'ANESTESIOLOGIA', 'Anestesiologia', now(), now()),
            ('9926b9fa-daef-4bf6-92c9-0ff54d5fed57', 'CLINICA_MEDICA', 'Clínica Médica', now(), now()),
            ('0dec0e25-a26d-4ec9-8545-54d2b607830c', 'CIRURGIA_GERAL', 'Cirurgia Geral', now(), now()),
            ('4cfbd10c-788e-4d86-aed2-5d63a0b3bf52', 'GINECOLOGIA_OBSTETRICIA', 'Ginecologia e Obstetrícia', now(), now()),
            ('47208a10-4338-46f9-9684-983497893a06', 'CIRURGIA_PEDIATRICA', 'Cirurgia Pediátrica', now(), now()),
            ('6978c189-333d-435d-b861-539cf27d6d01', 'MEDICINA_EMERGENCIA', 'Medicina de Emergência', now(), now()),
            ('8459ca19-4e94-4f33-9128-3826d1f90a00', 'DERMATOLOGIA', 'Dermatologia', now(), now()),
            ('36460df6-ce00-497b-a212-b46bc8f09ef6', 'GASTROENTEROLOGIA', 'Gastroenterologia', now(), now()),
            ('f2a339d6-1c82-45df-af47-9b55e5a3e7e8', 'GERIATRIA', 'Geriatria', now(), now()),
            ('40fa0f99-6f3a-4cf4-a334-ce7cc860e6de', 'INFECTOLOGIA', 'Infectologia', now(), now()),
            ('b67f3be8-f457-4f7d-b28d-9d39c6cc6dca', 'CIRURGIA_VASCULAR', 'Cirurgia Vascular', now(), now()),
            ('a0794ed1-0a6d-4fdf-8f29-e6dd7e20a0c8', 'CIRURGIA_PLASTICA', 'Cirurgia Plástica', now(), now()),
            ('020590d6-532b-4e81-807e-b69efaeebd4c', 'ENDOCRINOLOGIA', 'Endocrinologia e Metabologia', now(), now()),
            ('a2e2c129-863f-4640-bc22-49c7bf2fc1c1', 'HEMATOLOGIA', 'Hematologia e Hemoterapia', now(), now()),
            (gen_random_uuid(), 'NEFROLOGIA', 'Nefrologia', now(), now()),
            (gen_random_uuid(), 'NEUROLOGIA', 'Neurologia', now(), now()),
            (gen_random_uuid(), 'OFTALMOLOGIA', 'Oftalmologia', now(), now()),
            (gen_random_uuid(), 'ORTOPEDIA', 'Ortopedia e Traumatologia', now(), now()),
            (gen_random_uuid(), 'OTORRINOLARINGOLOGIA', 'Otorrinolaringologia', now(), now()),
            (gen_random_uuid(), 'PEDIATRIA', 'Pediatria', now(), now()),
            (gen_random_uuid(), 'PNEUMOLOGIA', 'Pneumologia', now(), now()),
            (gen_random_uuid(), 'PSIQUIATRIA', 'Psiquiatria', now(), now()),
            (gen_random_uuid(), 'RADIOLOGIA', 'Radiologia e Diagnóstico por Imagem', now(), now()),
            (gen_random_uuid(), 'REUMATOLOGIA', 'Reumatologia', now(), now()),
            (gen_random_uuid(), 'UROLOGIA', 'Urologia', now(), now()),
            (gen_random_uuid(), 'MEDICINA_INTENSIVA', 'Medicina Intensiva', now(), now()),
            (gen_random_uuid(), 'MEDICINA_FAMILIA', 'Medicina de Família e Comunidade', now(), now()),
            (gen_random_uuid(), 'MEDICINA_TRABALHO', 'Medicina do Trabalho', now(), now()),
            (gen_random_uuid(), 'PATOLOGIA', 'Patologia', now(), now()),
            (gen_random_uuid(), 'NUTROLOGIA', 'Nutrologia', now(), now()),
            (gen_random_uuid(), 'ONCOLOGIA', 'Oncologia Clínica', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_TORACICA', 'Cirurgia Torácica', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_CABECA_PESCOCO', 'Cirurgia de Cabeça e Pescoço', now(), now()),
            (gen_random_uuid(), 'NEUROCIRURGIA', 'Neurocirurgia', now(), now()),
            (gen_random_uuid(), 'COLOPROCTOLOGIA', 'Coloproctologia', now(), now()),
            (gen_random_uuid(), 'MASTOLOGIA', 'Mastologia', now(), now()),
            (gen_random_uuid(), 'ALERGIA_IMUNOLOGIA', 'Alergia e Imunologia', now(), now()),
            (gen_random_uuid(), 'ANGIOLOGIA', 'Angiologia', now(), now()),
            (gen_random_uuid(), 'MEDICINA_ESPORTIVA', 'Medicina Esportiva', now(), now());
    """)
    )


def downgrade() -> None:
    """Remove seeded data."""
    connection = op.get_bind()

    # Remove seeded specialties
    connection.execute(
        sa.text("""
        DELETE FROM specialties WHERE code IN (
            'CARDIOLOGIA', 'ANESTESIOLOGIA', 'CLINICA_MEDICA', 'CIRURGIA_GERAL',
            'GINECOLOGIA_OBSTETRICIA', 'CIRURGIA_PEDIATRICA', 'MEDICINA_EMERGENCIA',
            'DERMATOLOGIA', 'GASTROENTEROLOGIA', 'GERIATRIA', 'INFECTOLOGIA',
            'CIRURGIA_VASCULAR', 'CIRURGIA_PLASTICA', 'ENDOCRINOLOGIA', 'HEMATOLOGIA',
            'NEFROLOGIA', 'NEUROLOGIA', 'OFTALMOLOGIA', 'ORTOPEDIA', 'OTORRINOLARINGOLOGIA',
            'PEDIATRIA', 'PNEUMOLOGIA', 'PSIQUIATRIA', 'RADIOLOGIA', 'REUMATOLOGIA',
            'UROLOGIA', 'MEDICINA_INTENSIVA', 'MEDICINA_FAMILIA', 'MEDICINA_TRABALHO',
            'PATOLOGIA', 'NUTROLOGIA', 'ONCOLOGIA', 'CIRURGIA_TORACICA',
            'CIRURGIA_CABECA_PESCOCO', 'NEUROCIRURGIA', 'COLOPROCTOLOGIA', 'MASTOLOGIA',
            'ALERGIA_IMUNOLOGIA', 'ANGIOLOGIA', 'MEDICINA_ESPORTIVA'
        );
    """)
    )

    # Remove seeded organization roles
    connection.execute(
        sa.text("""
        DELETE FROM roles WHERE code IN (
            'ORG_OWNER', 'ORG_ADMIN', 'ORG_MANAGER', 'ORG_SCHEDULER', 'ORG_VIEWER'
        );
    """)
    )
