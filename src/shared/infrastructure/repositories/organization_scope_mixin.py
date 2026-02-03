"""Mixin for organization-scoped queries with hierarchical support."""

from typing import TYPE_CHECKING, Generic, Literal, TypeVar
from uuid import UUID

from src.shared.domain.schemas import PaginatedResponse
from sqlalchemy import Select, select
from sqlmodel import SQLModel


if TYPE_CHECKING:
    from fastapi_restkit.filterset import FilterSet
    from fastapi_restkit.sortingset import SortingSet
    from sqlalchemy.ext.asyncio import AsyncSession


ModelT = TypeVar("ModelT", bound=SQLModel)

# Scope policy type alias for cleaner signatures
ScopePolicy = Literal["ORGANIZATION_ONLY", "FAMILY"]


class OrganizationScopeMixin(Generic[ModelT]):
    """
    Mixin that provides organization-scoped query functionality.

    Supports hierarchical data scope with two policies:
    - ORGANIZATION_ONLY: Query only the current organization
    - FAMILY: Query all organizations in the family (parent + children/siblings)

    This mixin assumes the model has an `organization_id` field.

    Usage:
        class ProfessionalRepository(
            OrganizationScopeMixin[Professional],
            SoftDeleteMixin[Professional],
            BaseRepository[Professional],
        ):
            model = Professional
            default_scope_policy = "FAMILY"

    Note:
        This mixin must be listed BEFORE SoftDeleteMixin and BaseRepository
        in the inheritance chain for proper method resolution.
    """

    model: type[ModelT]
    session: "AsyncSession"
    default_scope_policy: ScopePolicy = "ORGANIZATION_ONLY"

    def _get_effective_org_ids(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        scope_policy: ScopePolicy | None = None,
    ) -> list[UUID]:
        """
        Get the effective organization IDs based on scope policy.

        Args:
            organization_id: The current organization UUID.
            family_org_ids: List of all organization IDs in the family.
            scope_policy: The scope policy to apply. Uses default if None.

        Returns:
            List of organization IDs to include in the query.
        """
        policy = scope_policy if scope_policy is not None else self.default_scope_policy

        if policy == "ORGANIZATION_ONLY":
            return [organization_id]

        if policy == "FAMILY":
            # Use family_org_ids, but ensure at least the current org is included
            if family_org_ids:
                return list(family_org_ids)
            # Fallback to just the current organization if family_org_ids is empty
            return [organization_id]

        return [organization_id]

    def _apply_org_scope(
        self,
        query: Select[tuple[ModelT]],
        org_ids: list[UUID],
    ) -> Select[tuple[ModelT]]:
        """
        Apply organization filter to a query.

        Args:
            query: The query to filter.
            org_ids: List of organization IDs to include.

        Returns:
            Filtered query.
        """
        if len(org_ids) == 1:
            return query.where(self.model.organization_id == org_ids[0])  # type: ignore[attr-defined]
        return query.where(self.model.organization_id.in_(org_ids))  # type: ignore[attr-defined]

    async def get_by_organization(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        scope_policy: ScopePolicy | None = None,
    ) -> ModelT | None:
        """
        Get entity by ID within organization scope.

        Args:
            id: The entity UUID.
            organization_id: The current organization UUID.
            family_org_ids: List of all organization IDs in the family.
            scope_policy: The scope policy to apply. Uses default if None.

        Returns:
            The entity if found within scope, None otherwise.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )

        # Use parent's get_query() to respect soft-delete filter
        query = super().get_query()  # type: ignore[misc]
        query = self._apply_org_scope(query, org_ids)
        query = query.where(self.model.id == id)  # type: ignore[attr-defined]

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        filters: "FilterSet | None" = None,
        sorting: "SortingSet | None" = None,
        limit: int = 25,
        offset: int = 0,
        scope_policy: ScopePolicy | None = None,
    ) -> PaginatedResponse[ModelT]:
        """
        List entities within organization scope with pagination.

        Args:
            organization_id: The current organization UUID.
            family_org_ids: List of all organization IDs in the family.
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.
            limit: Maximum number of items to return (default: 25).
            offset: Number of items to skip (default: 0).
            scope_policy: The scope policy to apply. Uses default if None.

        Returns:
            PaginatedResponse with items filtered by organization scope.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )

        # Use parent's get_query() to respect soft-delete filter
        base_query = super().get_query()  # type: ignore[misc]
        base_query = self._apply_org_scope(base_query, org_ids)

        # Delegate to parent's list() method
        return await super().list(  # type: ignore[misc]
            filters=filters,
            sorting=sorting,
            limit=limit,
            offset=offset,
            base_query=base_query,
        )

    async def exists_in_family(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        **filters: object,
    ) -> bool:
        """
        Check if a record exists in any of the family organizations.

        Args:
            family_org_ids: List of all organization IDs in the family.
            **filters: Field filters to apply (e.g., cpf="12345678901").

        Returns:
            True if a matching record exists, False otherwise.
        """
        # Use parent's get_query() to respect soft-delete filter
        query = super().get_query()  # type: ignore[misc]
        query = query.where(self.model.organization_id.in_(list(family_org_ids)))  # type: ignore[attr-defined]

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def find_in_family(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
        **filters: object,
    ) -> ModelT | None:
        """
        Find a record in any of the family organizations.

        Args:
            family_org_ids: List of all organization IDs in the family.
            exclude_id: Optional ID to exclude from results.
            **filters: Field filters to apply (e.g., cpf="12345678901").

        Returns:
            The matching record or None.
        """
        # Use parent's get_query() to respect soft-delete filter
        query = super().get_query()  # type: ignore[misc]
        query = query.where(self.model.organization_id.in_(list(family_org_ids)))  # type: ignore[attr-defined]

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)  # type: ignore[attr-defined]

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all_by_organization(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        filters: "FilterSet | None" = None,
        sorting: "SortingSet | None" = None,
        scope_policy: ScopePolicy | None = None,
    ) -> list[ModelT]:
        """
        List all entities within organization scope without pagination.

        Use this method for dropdown lists, caching scenarios,
        or when the dataset is known to be small.

        Args:
            organization_id: The current organization UUID.
            family_org_ids: List of all organization IDs in the family.
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.
            scope_policy: The scope policy to apply. Uses default if None.

        Returns:
            List of all matching entities within organization scope.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )

        # Use parent's get_query() to respect soft-delete filter
        base_query = super().get_query()  # type: ignore[misc]
        base_query = self._apply_org_scope(base_query, org_ids)

        # Delegate to parent's list_all() method
        return await super().list_all(  # type: ignore[misc]
            filters=filters,
            sorting=sorting,
            base_query=base_query,
        )
