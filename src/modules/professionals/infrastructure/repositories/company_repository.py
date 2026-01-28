"""Company repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.schemas.professional_version import CompanyInput
from src.shared.domain.models import Company
from src.shared.infrastructure.repositories import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """
    Repository for Company model.

    Provides lookup and upsert helpers based on CNPJ.
    """

    model = Company

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_cnpj(self, cnpj: str) -> Company | None:
        """Get a company by CNPJ."""
        result = await self.session.execute(select(Company).where(Company.cnpj == cnpj))
        return result.scalar_one_or_none()

    async def get_or_create_by_cnpj(
        self,
        cnpj: str,
        company_data: CompanyInput,
        created_by: UUID,
    ) -> tuple[Company, bool]:
        """
        Get existing company by CNPJ or create a new one.

        Returns:
            (company, was_created)
        """
        company = await self.get_by_cnpj(cnpj)
        if company:
            # Update existing data if provided
            company.legal_name = company_data.razao_social
            company.trade_name = company_data.nome_fantasia
            company.state_registration = company_data.inscricao_estadual
            company.municipal_registration = company_data.inscricao_municipal
            company.address = company_data.address
            company.number = company_data.number
            company.complement = company_data.complement
            company.neighborhood = company_data.neighborhood
            company.city = company_data.city
            company.state_code = (
                str(company_data.state_code) if company_data.state_code else None
            )
            company.postal_code = company_data.postal_code
            company.updated_by = created_by
            await self.session.flush()
            return company, False

        new_company = Company(
            cnpj=cnpj,
            legal_name=company_data.razao_social,
            trade_name=company_data.nome_fantasia,
            state_registration=company_data.inscricao_estadual,
            municipal_registration=company_data.inscricao_municipal,
            address=company_data.address,
            number=company_data.number,
            complement=company_data.complement,
            neighborhood=company_data.neighborhood,
            city=company_data.city,
            state_code=str(company_data.state_code)
            if company_data.state_code
            else None,
            postal_code=company_data.postal_code,
            created_by=created_by,
            updated_by=created_by,
        )
        self.session.add(new_company)
        await self.session.flush()
        return new_company, True
