"""ProfessionalCompany repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.infrastructure.filters import (
    ProfessionalCompanyFilter,
    ProfessionalCompanySorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class ProfessionalCompanyRepository(
    SoftDeletePaginationMixin[ProfessionalCompany],
    BaseRepository[ProfessionalCompany],
):
    """
    Repository for ProfessionalCompany model.

    Provides CRUD operations with soft delete support.
    Manages N:N relationship between professionals and companies.
    """

    model = ProfessionalCompany

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_professional(
        self,
        professional_id: UUID,
    ) -> Select[tuple[ProfessionalCompany]]:
        """
        Get base query filtered by professional.

        Args:
            professional_id: The organization professional UUID.

        Returns:
            Query filtered by professional and excluding soft-deleted.
        """
        return self._exclude_deleted().where(
            ProfessionalCompany.organization_professional_id == professional_id
        )

    async def get_by_id_for_professional(
        self,
        id: UUID,
        professional_id: UUID,
    ) -> ProfessionalCompany | None:
        """
        Get professional company link by ID.

        Args:
            id: The professional company UUID.
            professional_id: The organization professional UUID.

        Returns:
            Professional company link if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                ProfessionalCompany.id == id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_company(
        self,
        id: UUID,
        professional_id: UUID,
    ) -> ProfessionalCompany | None:
        """
        Get professional company link with company data loaded.

        Args:
            id: The professional company UUID.
            professional_id: The organization professional UUID.

        Returns:
            Professional company link with company loaded.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id)
            .where(ProfessionalCompany.id == id)
            .options(selectinload(ProfessionalCompany.company))
        )
        return result.scalar_one_or_none()

    async def list_for_professional(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalCompanyFilter | None = None,
        sorting: ProfessionalCompanySorting | None = None,
    ) -> PaginatedResponse[ProfessionalCompany]:
        """
        List company links for a professional with pagination, filtering, and sorting.

        Args:
            professional_id: The organization professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (currently empty - company_name is in related table).
            sorting: Optional sorting (id, joined_at, created_at).

        Returns:
            Paginated list of professional company links.
        """
        query = self._base_query_for_professional(professional_id).options(
            selectinload(ProfessionalCompany.company)
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def get_by_company_id(
        self,
        professional_id: UUID,
        company_id: UUID,
    ) -> ProfessionalCompany | None:
        """
        Get professional company link by company ID.

        Args:
            professional_id: The organization professional UUID.
            company_id: The company UUID.

        Returns:
            Professional company link if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                ProfessionalCompany.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def company_link_exists(
        self,
        professional_id: UUID,
        company_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a company link already exists for the professional.

        Args:
            professional_id: The organization professional UUID.
            company_id: The company UUID.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if link exists, False otherwise.
        """
        query = self._base_query_for_professional(professional_id).where(
            ProfessionalCompany.company_id == company_id
        )
        if exclude_id:
            query = query.where(ProfessionalCompany.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def list_active_companies(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProfessionalCompany]:
        """
        List active company links (not left) for a professional.

        Args:
            professional_id: The organization professional UUID.
            pagination: Pagination parameters.

        Returns:
            Paginated list of active professional company links.
        """
        query = (
            self._base_query_for_professional(professional_id)
            .where(ProfessionalCompany.left_at.is_(None))
            .options(selectinload(ProfessionalCompany.company))
        )
        return await self.paginate(pagination, query)
