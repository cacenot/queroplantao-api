"""OrganizationProfessional repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class OrganizationProfessionalRepository(
    SoftDeletePaginationMixin[OrganizationProfessional],
    BaseRepository[OrganizationProfessional],
):
    """
    Repository for OrganizationProfessional model.

    Provides CRUD operations with soft delete support and multi-tenancy filtering.
    """

    model = OrganizationProfessional

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_organization(
        self,
        organization_id: UUID,
    ) -> Select[tuple[OrganizationProfessional]]:
        """
        Get base query filtered by organization (multi-tenancy).

        Args:
            organization_id: The organization UUID.

        Returns:
            Query filtered by organization and excluding soft-deleted.
        """
        return self._exclude_deleted().where(
            OrganizationProfessional.organization_id == organization_id
        )

    async def get_by_id_for_organization(
        self,
        id: UUID,
        organization_id: UUID,
    ) -> OrganizationProfessional | None:
        """
        Get professional by ID for a specific organization.

        Args:
            id: The professional UUID.
            organization_id: The organization UUID.

        Returns:
            Professional if found in organization, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_organization(organization_id).where(
                OrganizationProfessional.id == id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self,
        id: UUID,
        organization_id: UUID,
    ) -> OrganizationProfessional | None:
        """
        Get professional by ID with all related data loaded.

        Args:
            id: The professional UUID.
            organization_id: The organization UUID.

        Returns:
            Professional with qualifications, documents, etc. loaded.
        """
        result = await self.session.execute(
            self._base_query_for_organization(organization_id)
            .where(OrganizationProfessional.id == id)
            .options(
                selectinload(OrganizationProfessional.qualifications),
                selectinload(OrganizationProfessional.documents),
                selectinload(OrganizationProfessional.professional_companies),
                selectinload(OrganizationProfessional.bank_accounts),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(
        self,
        cpf: str,
        organization_id: UUID,
    ) -> OrganizationProfessional | None:
        """
        Get professional by CPF within an organization.

        Args:
            cpf: The CPF (11 digits, no formatting).
            organization_id: The organization UUID.

        Returns:
            Professional if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_organization(organization_id).where(
                OrganizationProfessional.cpf == cpf
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
        organization_id: UUID,
    ) -> OrganizationProfessional | None:
        """
        Get professional by email within an organization.

        Args:
            email: The email address.
            organization_id: The organization UUID.

        Returns:
            Professional if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_organization(organization_id).where(
                OrganizationProfessional.email == email
            )
        )
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals for an organization with pagination, filtering, and sorting.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, is_active, gender, marital_status).
            sorting: Optional sorting (id, full_name, email, created_at).

        Returns:
            Paginated list of professionals.
        """
        query = self._base_query_for_organization(organization_id)

        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def exists_by_cpf(
        self,
        cpf: str,
        organization_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given CPF exists in the organization.

        Args:
            cpf: The CPF to check.
            organization_id: The organization UUID.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if CPF exists, False otherwise.
        """
        query = self._base_query_for_organization(organization_id).where(
            OrganizationProfessional.cpf == cpf
        )
        if exclude_id:
            query = query.where(OrganizationProfessional.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def exists_by_email(
        self,
        email: str,
        organization_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given email exists in the organization.

        Args:
            email: The email to check.
            organization_id: The organization UUID.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if email exists, False otherwise.
        """
        query = self._base_query_for_organization(organization_id).where(
            OrganizationProfessional.email == email
        )
        if exclude_id:
            query = query.where(OrganizationProfessional.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()
