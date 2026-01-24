"""Mixin for organization-scoped queries with hierarchical support."""

from typing import Generic, Literal, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlmodel import SQLModel


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

            async def list_for_organization(
                self,
                organization_id: UUID,
                family_org_ids: list[UUID],
                pagination: PaginationParams,
                *,
                scope_policy: ScopePolicy | None = None,
            ):
                query = self._base_query_for_scope(
                    organization_id=organization_id,
                    family_org_ids=family_org_ids,
                    scope_policy=scope_policy,
                )
                return await self.paginate(pagination, query)
    """

    model: type[ModelT]
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
            return query.where(self.model.organization_id == org_ids[0])
        return query.where(self.model.organization_id.in_(org_ids))

    def _base_query_for_scope(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        scope_policy: ScopePolicy | None = None,
        base_query: Select[tuple[ModelT]] | None = None,
    ) -> Select[tuple[ModelT]]:
        """
        Get base query filtered by organization scope.

        Args:
            organization_id: The current organization UUID.
            family_org_ids: List of all organization IDs in the family.
            scope_policy: The scope policy to apply. Uses default if None.
            base_query: Optional base query to start from. Creates new if None.

        Returns:
            Query filtered by organization scope.
        """
        if base_query is None:
            base_query = select(self.model)

        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )

        return self._apply_org_scope(base_query, org_ids)

    async def exists_in_family(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        **filters,
    ) -> bool:
        """
        Check if a record exists in any of the family organizations.

        Args:
            family_org_ids: List of all organization IDs in the family.
            **filters: Field filters to apply (e.g., cpf="12345678901").

        Returns:
            True if a matching record exists, False otherwise.
        """
        query = select(self.model).where(
            self.model.organization_id.in_(list(family_org_ids))
        )

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        # Add soft delete filter if model has deleted_at
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def find_in_family(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
        **filters,
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
        query = select(self.model).where(
            self.model.organization_id.in_(list(family_org_ids))
        )

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        # Add soft delete filter if model has deleted_at
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
