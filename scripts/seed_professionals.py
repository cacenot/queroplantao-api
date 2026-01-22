"""Script to seed 50 professionals into the database."""

import asyncio
import os
import random
import sys
from datetime import date
from uuid import UUID, uuid4

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app.config import Settings


def uuid7():
    """Generate a UUID v7-like ID (using uuid4 as fallback)."""
    # Use Python 3.14's built-in uuid7 if available, otherwise uuid4
    try:
        from uuid import uuid7 as _uuid7

        return _uuid7()
    except ImportError:
        return uuid4()


# Brazilian first names
FIRST_NAMES_MALE = [
    "João",
    "Pedro",
    "Lucas",
    "Gabriel",
    "Rafael",
    "Matheus",
    "Bruno",
    "Felipe",
    "Gustavo",
    "Leonardo",
    "André",
    "Carlos",
    "Daniel",
    "Eduardo",
    "Fernando",
    "Henrique",
    "Igor",
    "José",
    "Marcos",
    "Paulo",
    "Ricardo",
    "Thiago",
    "Vinícius",
    "Alexandre",
    "Antônio",
    "Caio",
    "Diego",
    "Fábio",
    "Guilherme",
    "Hugo",
]

FIRST_NAMES_FEMALE = [
    "Maria",
    "Ana",
    "Juliana",
    "Fernanda",
    "Camila",
    "Beatriz",
    "Larissa",
    "Amanda",
    "Carolina",
    "Gabriela",
    "Isabela",
    "Letícia",
    "Mariana",
    "Natália",
    "Patricia",
    "Renata",
    "Sabrina",
    "Tatiana",
    "Vanessa",
    "Bianca",
    "Carla",
    "Daniela",
    "Elisa",
    "Flávia",
    "Helena",
    "Lívia",
    "Priscila",
    "Raquel",
    "Simone",
    "Viviane",
]

LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Rodrigues",
    "Ferreira",
    "Alves",
    "Pereira",
    "Lima",
    "Gomes",
    "Costa",
    "Ribeiro",
    "Martins",
    "Carvalho",
    "Almeida",
    "Lopes",
    "Soares",
    "Fernandes",
    "Vieira",
    "Barbosa",
    "Rocha",
    "Dias",
    "Nascimento",
    "Andrade",
    "Moreira",
    "Nunes",
    "Marques",
    "Machado",
    "Mendes",
    "Freitas",
    "Cardoso",
    "Ramos",
    "Gonçalves",
    "Santana",
    "Teixeira",
]

BRAZILIAN_STATES = [
    "SP",
    "RJ",
    "MG",
    "RS",
    "PR",
    "SC",
    "BA",
    "PE",
    "CE",
    "DF",
    "GO",
    "ES",
]

# Professional types with their councils
PROFESSIONAL_CONFIGS = [
    # Doctors (will be 80%+ of professionals)
    {"type": "DOCTOR", "council": "CRM", "specialties_required": True},
    # Other healthcare professionals (20%)
    {"type": "NURSE", "council": "COREN", "specialties_required": False},
    {"type": "NURSING_TECH", "council": "COREN", "specialties_required": False},
    {"type": "PHYSIOTHERAPIST", "council": "CREFITO", "specialties_required": False},
    {"type": "PHARMACIST", "council": "CRF", "specialties_required": False},
]

# Medical specialties (only for doctors)
MEDICAL_SPECIALTIES = [
    ("517fa123-4da4-4a3c-abef-792c084e8500", "Cardiologia"),
    ("2d36831d-489e-4106-80e5-03520015be16", "Anestesiologia"),
    ("9926b9fa-daef-4bf6-92c9-0ff54d5fed57", "Clínica Médica"),
    ("0dec0e25-a26d-4ec9-8545-54d2b607830c", "Cirurgia Geral"),
    ("4cfbd10c-788e-4d86-aed2-5d63a0b3bf52", "Ginecologia e Obstetrícia"),
    ("47208a10-4338-46f9-9684-983497893a06", "Cirurgia Pediátrica"),
    ("6978c189-333d-435d-b861-539cf27d6d01", "Medicina de Emergência"),
    ("8459ca19-4e94-4f33-9128-3826d1f90a00", "Dermatologia"),
    ("36460df6-ce00-497b-a212-b46bc8f09ef6", "Gastroenterologia"),
    ("f2a339d6-1c82-45df-af47-9b55e5a3e7e8", "Geriatria"),
    ("40fa0f99-6f3a-4cf4-a334-ce7cc860e6de", "Infectologia"),
    ("b67f3be8-f457-4f7d-b28d-9d39c6cc6dca", "Cirurgia Vascular"),
    ("a0794ed1-0a6d-4fdf-8f29-e6dd7e20a0c8", "Cirurgia Plástica"),
    ("020590d6-532b-4e81-807e-b69efaeebd4c", "Endocrinologia e Metabologia"),
    ("a2e2c129-863f-4640-bc22-49c7bf2fc1c1", "Hematologia e Hemoterapia"),
]

# Organizations
ORGANIZATIONS = [
    "01933f60-3333-7000-8000-000000000001",  # DGS
    "01933f60-4444-7000-8000-000000000002",  # IMBRAM
]


def generate_cpf() -> str:
    """Generate a valid CPF number."""
    cpf = [random.randint(0, 9) for _ in range(9)]

    # First verification digit
    sum1 = sum((10 - i) * cpf[i] for i in range(9))
    d1 = 11 - (sum1 % 11)
    d1 = 0 if d1 >= 10 else d1
    cpf.append(d1)

    # Second verification digit
    sum2 = sum((11 - i) * cpf[i] for i in range(10))
    d2 = 11 - (sum2 % 11)
    d2 = 0 if d2 >= 10 else d2
    cpf.append(d2)

    return "".join(map(str, cpf))


def generate_phone() -> str:
    """Generate a Brazilian phone number in E.164 format."""
    ddd = random.choice(["11", "21", "31", "41", "51", "61", "71", "81", "85", "27"])
    number = f"9{random.randint(10000000, 99999999)}"
    return f"+55{ddd}{number}"


def generate_birth_date() -> str:
    """Generate a birth date for someone between 25 and 65 years old."""
    year = random.randint(1960, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate_council_number(council_type: str) -> str:
    """Generate a council registration number."""
    if council_type == "CRM":
        return str(random.randint(100000, 999999))
    elif council_type == "COREN":
        return str(random.randint(100000, 999999))
    elif council_type == "CREFITO":
        return str(random.randint(10000, 99999))
    elif council_type == "CRF":
        return str(random.randint(10000, 99999))
    return str(random.randint(10000, 99999))


def generate_rqe_number() -> str:
    """Generate an RQE (specialty registration) number."""
    return str(random.randint(10000, 99999))


async def seed_professionals():
    """Seed 50 professionals into the database."""
    settings = Settings()
    db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Starting to seed 50 professionals...")

        # Generate 50 professionals (40 doctors = 80%, 10 others = 20%)
        professionals_data = []

        # 40 doctors
        for i in range(40):
            is_female = random.random() < 0.4  # 40% female doctors
            first_name = random.choice(
                FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE
            )
            last_name = f"{random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"

            professionals_data.append(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": "FEMALE" if is_female else "MALE",
                    "professional_type": "DOCTOR",
                    "council_type": "CRM",
                    "has_specialty": True,
                }
            )

        # 10 other healthcare professionals
        other_configs = [
            ("NURSE", "COREN", True),
            ("NURSE", "COREN", True),
            ("NURSE", "COREN", False),
            ("NURSING_TECH", "COREN", False),
            ("NURSING_TECH", "COREN", True),
            ("PHYSIOTHERAPIST", "CREFITO", False),
            ("PHYSIOTHERAPIST", "CREFITO", True),
            ("PHARMACIST", "CRF", False),
            ("PHARMACIST", "CRF", True),
            ("NURSE", "COREN", True),
        ]

        for prof_type, council, is_female in other_configs:
            first_name = random.choice(
                FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE
            )
            last_name = f"{random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"

            professionals_data.append(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": "FEMALE" if is_female else "MALE",
                    "professional_type": prof_type,
                    "council_type": council,
                    "has_specialty": False,  # Non-doctors don't have medical specialties
                }
            )

        # Shuffle to mix doctors and others
        random.shuffle(professionals_data)

        created_count = 0
        used_cpfs = set()
        used_emails = set()
        used_council_numbers = {}  # {(council_number, state): True}

        for idx, prof_data in enumerate(professionals_data):
            # Generate unique identifiers
            cpf = generate_cpf()
            while cpf in used_cpfs:
                cpf = generate_cpf()
            used_cpfs.add(cpf)

            full_name = f"{prof_data['first_name']} {prof_data['last_name']}"
            email_base = f"{prof_data['first_name'].lower()}.{prof_data['last_name'].split()[0].lower()}"
            email = f"{email_base}{random.randint(1, 999)}@email.com"
            while email in used_emails:
                email = f"{email_base}{random.randint(1, 9999)}@email.com"
            used_emails.add(email)

            # Generate unique council number
            state = random.choice(BRAZILIAN_STATES)
            council_number = generate_council_number(prof_data["council_type"])
            while (council_number, state) in used_council_numbers:
                council_number = generate_council_number(prof_data["council_type"])
            used_council_numbers[(council_number, state)] = True

            # Select organization (distribute evenly)
            org_id = ORGANIZATIONS[idx % len(ORGANIZATIONS)]

            # Create professional
            professional_id = uuid7()

            await session.execute(
                text("""
                    INSERT INTO organization_professionals (
                        id, organization_id, full_name, email, phone, cpf, 
                        birth_date, gender, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :org_id, :full_name, :email, :phone, :cpf,
                        :birth_date, :gender, true, NOW(), NOW()
                    )
                """),
                {
                    "id": str(professional_id),
                    "org_id": org_id,
                    "full_name": full_name,
                    "email": email,
                    "phone": generate_phone(),
                    "cpf": cpf,
                    "birth_date": generate_birth_date(),
                    "gender": prof_data["gender"],
                },
            )

            # Create qualification
            qualification_id = uuid7()
            graduation_year = random.randint(1990, 2020)

            await session.execute(
                text("""
                    INSERT INTO professional_qualifications (
                        id, organization_id, organization_professional_id,
                        professional_type, council_type, council_number, council_state,
                        graduation_year, is_primary, created_at, updated_at
                    ) VALUES (
                        :id, :org_id, :prof_id,
                        :prof_type, :council_type, :council_number, :council_state,
                        :graduation_year, true, NOW(), NOW()
                    )
                """),
                {
                    "id": str(qualification_id),
                    "org_id": org_id,
                    "prof_id": str(professional_id),
                    "prof_type": prof_data["professional_type"],
                    "council_type": prof_data["council_type"],
                    "council_number": council_number,
                    "council_state": state,
                    "graduation_year": graduation_year,
                },
            )

            # Create specialty for doctors (1-2 specialties each)
            if (
                prof_data["has_specialty"]
                and prof_data["professional_type"] == "DOCTOR"
            ):
                num_specialties = random.randint(1, 2)
                selected_specialties = random.sample(
                    MEDICAL_SPECIALTIES, num_specialties
                )

                for spec_idx, (spec_id, spec_name) in enumerate(selected_specialties):
                    specialty_link_id = uuid7()
                    rqe_number = generate_rqe_number()

                    await session.execute(
                        text("""
                            INSERT INTO professional_specialties (
                                id, qualification_id, specialty_id,
                                is_primary, rqe_number, rqe_state, residency_status,
                                created_at, updated_at
                            ) VALUES (
                                :id, :qual_id, :spec_id,
                                :is_primary, :rqe_number, :rqe_state, 'COMPLETED',
                                NOW(), NOW()
                            )
                        """),
                        {
                            "id": str(specialty_link_id),
                            "qual_id": str(qualification_id),
                            "spec_id": spec_id,
                            "is_primary": spec_idx == 0,
                            "rqe_number": rqe_number,
                            "rqe_state": state,
                        },
                    )

            created_count += 1
            if created_count % 10 == 0:
                print(f"  Created {created_count} professionals...")

        await session.commit()
        print(f"\n✅ Successfully created {created_count} professionals!")

        # Print summary
        result = await session.execute(
            text("""
                SELECT 
                    pq.professional_type,
                    COUNT(DISTINCT op.id) as count
                FROM organization_professionals op
                JOIN professional_qualifications pq ON pq.organization_professional_id = op.id
                WHERE op.deleted_at IS NULL
                GROUP BY pq.professional_type
                ORDER BY count DESC
            """)
        )

        print("\nProfessionals by type:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")

        # Count specialties
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM professional_specialties WHERE deleted_at IS NULL
            """)
        )
        specialty_count = result.scalar()
        print(f"\nTotal specialty links: {specialty_count}")


if __name__ == "__main__":
    asyncio.run(seed_professionals())
