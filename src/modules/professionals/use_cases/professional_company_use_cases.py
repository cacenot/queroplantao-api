"""Use cases for ProfessionalCompany."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError
from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.domain.schemas import (
    ProfessionalCompanyCreate,
    ProfessionalCompanyUpdate,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalCompanyRepository,
)


class CreateProfessionalCompanyUseCase:
    """Use case for creating a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalCompanyCreate,
        created_by: UUID | None = None,
    ) -> ProfessionalCompany:
        """
        Create a new company link for a professional.

        Validates:
        - Professional exists in organization
        - Company link doesn't already exist
        """
        # Verify professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        # Check link doesn't already exist
        if await self.repository.company_link_exists(professional_id, data.company_id):
            raise ConflictError(
                resource="ProfessionalCompany",
                field="company_id",
                value=str(data.company_id),
                message="This professional is already linked to this company",
            )

        professional_company = ProfessionalCompany(
            organization_professional_id=professional_id,
            created_by=created_by,
            **data.model_dump(),
        )

        return await self.repository.create(professional_company)


class UpdateProfessionalCompanyUseCase:
    """Use case for updating a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
        data: ProfessionalCompanyUpdate,
        updated_by: UUID | None = None,
    ) -> ProfessionalCompany:
        """Update an existing company link (PATCH semantics)."""
        professional_company = await self.repository.get_by_id_for_professional(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise NotFoundError(
                resource="ProfessionalCompany",
                identifier=str(professional_company_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(professional_company, field, value)

        if updated_by:
            professional_company.updated_by = updated_by

        return await self.repository.update(professional_company)


class DeleteProfessionalCompanyUseCase:
    """Use case for soft-deleting a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
    ) -> None:
        """Soft delete a company link."""
        professional_company = await self.repository.get_by_id_for_professional(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise NotFoundError(
                resource="ProfessionalCompany",
                identifier=str(professional_company_id),
            )

        await self.repository.soft_delete(professional_company_id)


class GetProfessionalCompanyUseCase:
    """Use case for retrieving a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
    ) -> ProfessionalCompany:
        """Get a company link by ID with company data loaded."""
        professional_company = await self.repository.get_by_id_with_company(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise NotFoundError(
                resource="ProfessionalCompany",
                identifier=str(professional_company_id),
            )

        return professional_company


class ListProfessionalCompaniesUseCase:
    """Use case for listing company links for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        active_only: bool = False,
    ) -> PaginatedResponse[ProfessionalCompany]:
        """List company links for a professional."""
        if active_only:
            return await self.repository.list_active_companies(
                professional_id, pagination
            )
        return await self.repository.list_for_professional(professional_id, pagination)
