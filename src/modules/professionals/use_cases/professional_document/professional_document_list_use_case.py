"""Use case for listing documents for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.filters import ListFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.domain.models import ProfessionalDocument
from src.shared.domain.models import DocumentType
from src.modules.professionals.infrastructure.filters import (
    ProfessionalDocumentFilter,
    ProfessionalDocumentSorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalDocumentRepository,
)


class ListProfessionalDocumentsUseCase:
    """Use case for listing documents for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalDocumentFilter | None = None,
        sorting: ProfessionalDocumentSorting | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """
        List documents for a professional.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, document_type, document_category, is_verified).
            sorting: Optional sorting (id, document_type, file_name, expires_at, created_at).

        Returns:
            Paginated list of documents.
        """
        # Verify professional exists in organization
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        if filters is None:
            filters = ProfessionalDocumentFilter()

        filters.organization_professional_id = ListFilter(values=[professional_id])
        base_query = self.repository.get_query()
        if filters.document_category and filters.document_category.values:
            base_query = base_query.join(DocumentType).options(
                selectinload(ProfessionalDocument.document_type)
            )

        return await self.repository.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=base_query,
        )
