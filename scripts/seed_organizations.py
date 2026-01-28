"""Seed script to create DGS (parent) and INBRAM (child) organizations."""

import asyncio
from uuid import uuid7

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app.config import Settings
from src.modules.organizations.domain.models.organization import Organization
from src.modules.organizations.domain.models.enums import OrganizationType
from src.shared.domain.models.company import Company


async def seed_organizations() -> None:
    """Create DGS (parent) and INBRAM (child) organizations with their companies."""
    settings = Settings()
    engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Generate UUIDs for consistency
        dgs_company_id = uuid7()
        inbram_company_id = uuid7()
        dgs_org_id = uuid7()
        inbram_org_id = uuid7()

        # Create Company for DGS
        dgs_company = Company(
            id=dgs_company_id,
            cnpj="12345678000190",  # Mock CNPJ
            legal_name="DGS Serviços Médicos LTDA",
            trade_name="DGS",
            email="contato@dgs.com.br",
            phone="+5547999999999",
            is_active=True,
            # Address
            address="Rua Hercílio Luz",
            number="100",
            neighborhood="Centro",
            city="Itajaí",
            state_code="SC",
            postal_code="88301001",
        )
        session.add(dgs_company)

        # Create Company for INBRAM
        inbram_company = Company(
            id=inbram_company_id,
            cnpj="98765432000199",  # Mock CNPJ
            legal_name="INBRAM Saúde LTDA",
            trade_name="INBRAM",
            email="contato@inbram.com.br",
            phone="+5547988888888",
            is_active=True,
            # Address
            address="Avenida Brasil",
            number="1000",
            neighborhood="Fazenda",
            city="Itajaí",
            state_code="SC",
            postal_code="88302100",
        )
        session.add(inbram_company)

        # Flush to ensure companies are created before organizations
        await session.flush()

        # Create DGS organization (parent - no parent_id)
        dgs_org = Organization(
            id=dgs_org_id,
            name="DGS",
            organization_type=OrganizationType.OUTSOURCING_COMPANY,
            is_active=True,
            company_id=dgs_company_id,
            parent_id=None,  # Parent organization
        )
        session.add(dgs_org)

        # Create INBRAM organization (child - parent_id = DGS)
        inbram_org = Organization(
            id=inbram_org_id,
            name="INBRAM",
            organization_type=OrganizationType.HOSPITAL,
            is_active=True,
            company_id=inbram_company_id,
            parent_id=dgs_org_id,  # Child of DGS
        )
        session.add(inbram_org)

        await session.commit()

        print("=" * 60)
        print("Organizations created successfully!")
        print("=" * 60)
        print(f"\n🏢 Parent Organization:")
        print(f"   Name: DGS")
        print(f"   ID: {dgs_org_id}")
        print(f"   Type: OUTSOURCING_COMPANY")
        print(f"   Company CNPJ: 12.345.678/0001-90")
        print(f"\n🏥 Child Organization:")
        print(f"   Name: INBRAM")
        print(f"   ID: {inbram_org_id}")
        print(f"   Parent ID: {dgs_org_id}")
        print(f"   Type: HOSPITAL")
        print(f"   Company CNPJ: 98.765.432/0001-99")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_organizations())
