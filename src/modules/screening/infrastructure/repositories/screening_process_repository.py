"""ScreeningProcess repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.screening.domain.models import (
    DocumentUploadStep,
    ScreeningDocument,
    ScreeningProcess,
    ScreeningStatus,
)
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    ScopePolicy,
    SoftDeleteMixin,
)


class ScreeningProcessRepository(
    OrganizationScopeMixin[ScreeningProcess],
    SoftDeleteMixin[ScreeningProcess],
    BaseRepository[ScreeningProcess],
):
    """
    Repository for ScreeningProcess model.

    Provides CRUD operations with soft delete support and multi-tenancy filtering.
    """

    model = ScreeningProcess
    default_scope_policy = "ORGANIZATION_ONLY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_organization(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> Select[tuple[ScreeningProcess]]:
        """
        Get base query filtered by organization.

        Args:
            organization_id: The organization UUID.

        Returns:
            Query filtered by organization and excluding soft-deleted.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = super().get_query()  # type: ignore[misc]
        return self._apply_org_scope(base_query, org_ids)

    async def get_by_id_for_organization(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> ScreeningProcess | None:
        """
        Get screening process by ID for a specific organization.

        Args:
            id: The screening process UUID.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            ScreeningProcess if found, None otherwise.
        """
        query = self._base_query_for_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        ).where(ScreeningProcess.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> ScreeningProcess | None:
        """
        Get screening process with all related data (steps, documents).

        Args:
            id: The screening process UUID.
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            ScreeningProcess with loaded relationships.
        """
        query = (
            self._base_query_for_organization(
                organization_id=organization_id,
                family_org_ids=family_org_ids,
                scope_policy=scope_policy,
            )
            .where(ScreeningProcess.id == id)
            .options(
                # Load all step relationships
                selectinload(ScreeningProcess.conversation_step),
                selectinload(ScreeningProcess.professional_data_step),
                selectinload(ScreeningProcess.document_upload_step).options(
                    selectinload(DocumentUploadStep.documents).options(
                        selectinload(ScreeningDocument.document_type),
                    ),
                ),
                selectinload(ScreeningProcess.document_review_step),
                selectinload(ScreeningProcess.payment_info_step),
                selectinload(ScreeningProcess.client_validation_step),
                # Load alerts
                selectinload(ScreeningProcess.alerts),
                # Load other relationships
                selectinload(ScreeningProcess.client_company),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcess]:
        """
        List screening processes for an organization.

        Uses denormalized fields (current_step_type, configured_step_types)
        instead of loading step relationships, for efficient listing.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of screening processes.
        """
        base_query = self._base_query_for_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )
        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=base_query,
        )

    async def list_for_actor(
        self,
        organization_id: UUID,
        actor_id: UUID,
        pagination: PaginationParams,
        *,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcess]:
        """
        List screening processes assigned to a specific user.

        This is the "my pending screenings" filter.

        Uses denormalized fields (current_step_type, configured_step_types)
        instead of loading step relationships, for efficient listing.

        Args:
            organization_id: The organization UUID.
            actor_id: The current actor user UUID.
            pagination: Pagination parameters.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.
            filters: Optional additional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of screening processes.
        """
        base_query = self._base_query_for_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        ).where(ScreeningProcess.current_actor_id == actor_id)
        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=base_query,
        )

    async def get_active_by_cpf(
        self,
        organization_id: UUID,
        cpf: str,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> ScreeningProcess | None:
        """
        Get active screening for a professional by CPF.

        Active = not in terminal state (APPROVED, REJECTED, EXPIRED, CANCELLED).

        Args:
            organization_id: The organization UUID.
            cpf: The professional's CPF.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Active ScreeningProcess if found, None otherwise.
        """
        terminal_statuses = [
            ScreeningStatus.APPROVED,
            ScreeningStatus.REJECTED,
            ScreeningStatus.EXPIRED,
            ScreeningStatus.CANCELLED,
        ]
        query = (
            self._base_query_for_organization(
                organization_id=organization_id,
                family_org_ids=family_org_ids,
                scope_policy=scope_policy,
            )
            .where(ScreeningProcess.professional_cpf == cpf)
            .where(ScreeningProcess.status.not_in(terminal_statuses))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_access_token(
        self,
        access_token: str,
    ) -> ScreeningProcess | None:
        """
        Get screening process by access token (for public access).

        Args:
            access_token: The secure access token.

        Returns:
            ScreeningProcess if found and not deleted, None otherwise.
        """
        query = super().get_query().where(  # type: ignore[misc]
            ScreeningProcess.access_token == access_token
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_access_token_with_details(
        self,
        access_token: str,
    ) -> ScreeningProcess | None:
        """
        Get screening process by access token with all related data.

        Args:
            access_token: The secure access token.

        Returns:
            ScreeningProcess with loaded relationships if found, None otherwise.
        """
        query = (
            super().get_query()  # type: ignore[misc]
            .where(ScreeningProcess.access_token == access_token)
            .options(
                # Load all step relationships
                selectinload(ScreeningProcess.conversation_step),
                selectinload(ScreeningProcess.professional_data_step),
                selectinload(ScreeningProcess.document_upload_step).options(
                    selectinload(DocumentUploadStep.documents).options(
                        selectinload(ScreeningDocument.document_type),
                    ),
                ),
                selectinload(ScreeningProcess.document_review_step),
                selectinload(ScreeningProcess.payment_info_step),
                selectinload(ScreeningProcess.client_validation_step),
                # Load alerts
                selectinload(ScreeningProcess.alerts),
                # Load other relationships
                selectinload(ScreeningProcess.client_company),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_status(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> dict[ScreeningStatus, int]:
        """
        Count screening processes by status for an organization.

        Returns:
            Dict mapping status to count.
        """
        from sqlalchemy import func

        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = super().get_query()  # type: ignore[misc]
        base_query = self._apply_org_scope(base_query, org_ids)

        query = (
            select(
                ScreeningProcess.status,
                func.count(ScreeningProcess.id).label("count"),
            )
            .select_from(base_query.subquery())
            .group_by(ScreeningProcess.status)
        )
        result = await self.session.execute(query)
        rows = result.all()
        return {row.status: row.count for row in rows}
