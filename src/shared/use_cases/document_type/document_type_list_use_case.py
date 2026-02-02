"""Use case for listing document types with pagination."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models import DocumentType
from src.shared.infrastructure.filters.document_type import (
    DocumentTypeFilter,
    DocumentTypeSorting,
)
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)


class ListDocumentTypesUseCase:
    """Use case for listing document types with pagination."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        pagination: PaginationParams,
        *,
        filters: DocumentTypeFilter | None = None,
        sorting: DocumentTypeSorting | None = None,
    ) -> PaginatedResponse[DocumentType]:
        """
        List document types with pagination within organization scope.

        Args:
            organization_id: The current organization UUID.
            family_org_ids: All organization IDs in the family.
            pagination: Pagination parameters.
            filters: Optional filters (search, category, is_active).
            sorting: Optional sorting (id, name, display_order).

        Returns:
            Paginated list of document types.
        """
        return await self.repository.list_by_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            filters=filters,
            sorting=sorting,
            limit=pagination.limit,
            offset=pagination.offset,
        )
