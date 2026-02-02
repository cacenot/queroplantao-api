"""OrganizationProfessional repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.models.professional_company import (
    ProfessionalCompany,
)
from src.modules.professionals.domain.models.professional_qualification import (
    ProfessionalQualification,
)
from src.modules.professionals.domain.models.professional_specialty import (
    ProfessionalSpecialty,
)
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.shared.domain.models.bank_account import BankAccount
from src.shared.domain.models.company import Company
from src.shared.domain.models.specialty import Specialty
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    ScopePolicy,
    SoftDeleteMixin,
)


class OrganizationProfessionalRepository(
    OrganizationScopeMixin[OrganizationProfessional],
    SoftDeleteMixin[OrganizationProfessional],
    BaseRepository[OrganizationProfessional],
):
    """
    Repository for OrganizationProfessional model.

    Provides CRUD operations with soft delete support and multi-tenancy filtering.
    Supports hierarchical data scope (ORGANIZATION_ONLY or FAMILY).
    """

    model = OrganizationProfessional
    # Professionals are shared across the family by default
    default_scope_policy: ScopePolicy = "FAMILY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id_for_organization(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationProfessional | None:
        """
        Get professional by ID with scope support.

        Args:
            id: The professional UUID.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Professional if found in scope, None otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]
        result = await self.session.execute(
            base_query.where(OrganizationProfessional.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationProfessional | None:
        """
        Get professional by ID with all related data loaded.

        Loads the full nested graph:
        - qualifications → specialties → specialty (reference data)
        - qualifications → specialties → documents
        - qualifications → educations
        - qualifications → documents
        - professional_companies → company → bank_accounts
        - bank_accounts → bank
        - documents (profile-level, filtered in response schema)

        Args:
            id: The professional UUID.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Professional with all nested data loaded.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = (
            super()
            .get_query()
            .options(
                # Qualifications with nested specialties, educations, and documents
                selectinload(OrganizationProfessional.qualifications).options(
                    selectinload(ProfessionalQualification.specialties).options(
                        selectinload(ProfessionalSpecialty.specialty),  # Specialty name
                        selectinload(ProfessionalSpecialty.documents),  # Specialty docs
                    ),
                    selectinload(ProfessionalQualification.educations),
                    selectinload(
                        ProfessionalQualification.documents
                    ),  # Qualification docs
                ),
                # All documents (will filter profile-level in response schema)
                selectinload(OrganizationProfessional.documents),
                # Professional companies with company and bank accounts
                selectinload(OrganizationProfessional.professional_companies).options(
                    selectinload(ProfessionalCompany.company).options(
                        selectinload(Company.bank_accounts),
                    ),
                ),
                # Professional's direct bank accounts with bank info
                selectinload(OrganizationProfessional.bank_accounts).options(
                    selectinload(BankAccount.bank),
                ),
            )
        )
        base_query = self._apply_org_scope(base_query, org_ids)
        result = await self.session.execute(
            base_query.where(OrganizationProfessional.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(
        self,
        cpf: str,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationProfessional | None:
        """
        Get professional by CPF with scope support.

        Args:
            cpf: The CPF (11 digits, no formatting).
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Professional if found, None otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]
        result = await self.session.execute(
            base_query.where(OrganizationProfessional.cpf == cpf)
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationProfessional | None:
        """
        Get professional by email with scope support.

        Args:
            email: The email address.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Professional if found, None otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]
        result = await self.session.execute(
            base_query.where(OrganizationProfessional.email == email)
        )
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals with pagination, filtering, sorting, and scope support.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            filters: Optional filters (search, gender, marital_status, professional_type).
            sorting: Optional sorting (id, full_name, email, created_at).

        Returns:
            Paginated list of professionals.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]

        # Apply professional_type filter via subquery (field is in ProfessionalQualification)
        if (
            filters
            and filters.professional_type
            and filters.professional_type.is_active()
        ):
            subquery = select(
                ProfessionalQualification.organization_professional_id
            ).where(
                ProfessionalQualification.professional_type.in_(
                    filters.professional_type.values
                )
            )
            query = query.where(OrganizationProfessional.id.in_(subquery))

        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.limit,
            offset=pagination.offset,
            base_query=query,
        )

    async def list_for_organization_with_summary(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals with primary qualification and specialties loaded.

        Eagerly loads only the columns needed for summary response:
        - Professional: id, avatar_url, full_name, city, state_code, cpf, phone, email
        - Qualification: professional_type, council_type, council_number, council_state
        - Specialty: id, name

        Only loads primary qualification (is_primary=True) and filters deleted records.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            filters: Optional filters (including professional_type).
            sorting: Optional sorting.

        Returns:
            Paginated list of professionals with minimal data loaded.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]

        # Apply professional_type filter via subquery (field is in ProfessionalQualification)
        if (
            filters
            and filters.professional_type
            and filters.professional_type.is_active()
        ):
            subquery = select(
                ProfessionalQualification.organization_professional_id
            ).where(
                ProfessionalQualification.professional_type.in_(
                    filters.professional_type.values
                )
            )
            query = query.where(OrganizationProfessional.id.in_(subquery))

        query = query.options(
            # Load only needed columns from OrganizationProfessional
            load_only(
                OrganizationProfessional.id,
                OrganizationProfessional.avatar_url,
                OrganizationProfessional.full_name,
                OrganizationProfessional.city,
                OrganizationProfessional.state_code,
                OrganizationProfessional.cpf,
                OrganizationProfessional.phone,
                OrganizationProfessional.email,
            ),
            # Load primary qualification with only needed columns
            selectinload(
                OrganizationProfessional.qualifications.and_(
                    ProfessionalQualification.is_primary.is_(True),
                )
            )
            .load_only(
                ProfessionalQualification.id,
                ProfessionalQualification.professional_type,
                ProfessionalQualification.council_type,
                ProfessionalQualification.council_number,
                ProfessionalQualification.council_state,
            )
            .selectinload(ProfessionalQualification.specialties)
            .load_only(ProfessionalSpecialty.id, ProfessionalSpecialty.specialty_id)
            .selectinload(ProfessionalSpecialty.specialty)
            .load_only(Specialty.id, Specialty.name),
        )

        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.limit,
            offset=pagination.offset,
            base_query=query,
        )

    async def exists_by_cpf(
        self,
        cpf: str,
        organization_id: UUID,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given CPF exists with scope support.

        Args:
            cpf: The CPF to check.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if CPF exists, False otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]
        query = query.where(OrganizationProfessional.cpf == cpf)
        if exclude_id:
            query = query.where(OrganizationProfessional.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def exists_by_email(
        self,
        email: str,
        organization_id: UUID,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given email exists with scope support.

        Args:
            email: The email to check.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if email exists, False otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        query = self._apply_org_scope(super().get_query(), org_ids)  # type: ignore[misc]
        query = query.where(OrganizationProfessional.email == email)
        if exclude_id:
            query = query.where(OrganizationProfessional.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def exists_by_cpf_in_family(
        self,
        cpf: str,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given CPF exists in any family organization.

        Args:
            cpf: The CPF to check.
            family_org_ids: List of all organization IDs in the family.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if CPF exists in the family, False otherwise.
        """
        return (
            await self.exists_in_family(
                family_org_ids=family_org_ids,
                cpf=cpf,
            )
            if exclude_id is None
            else await self._exists_in_family_with_exclude(
                family_org_ids=family_org_ids,
                exclude_id=exclude_id,
                cpf=cpf,
            )
        )

    async def exists_by_email_in_family(
        self,
        email: str,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a professional with the given email exists in any family organization.

        Args:
            email: The email to check.
            family_org_ids: List of all organization IDs in the family.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if email exists in the family, False otherwise.
        """
        return (
            await self.exists_in_family(
                family_org_ids=family_org_ids,
                email=email,
            )
            if exclude_id is None
            else await self._exists_in_family_with_exclude(
                family_org_ids=family_org_ids,
                exclude_id=exclude_id,
                email=email,
            )
        )

    async def _exists_in_family_with_exclude(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        exclude_id: UUID,
        **filters,
    ) -> bool:
        """
        Check if a record exists in family organizations, excluding a specific ID.

        Args:
            family_org_ids: List of all organization IDs in the family.
            exclude_id: ID to exclude from the check.
            **filters: Field filters to apply.

        Returns:
            True if a matching record exists, False otherwise.
        """
        query = self.get_query().where(
            OrganizationProfessional.organization_id.in_(list(family_org_ids)),
            OrganizationProfessional.id != exclude_id,
        )

        for field, value in filters.items():
            if hasattr(OrganizationProfessional, field) and value is not None:
                query = query.where(getattr(OrganizationProfessional, field) == value)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()
