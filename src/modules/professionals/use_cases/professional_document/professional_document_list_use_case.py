"""Use case for listing documents for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import (
    DocumentCategory,
    DocumentType,
    ProfessionalDocument,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)


class ListProfessionalDocumentsUseCase:
    """Use case for listing documents for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        category: DocumentCategory | None = None,
        document_type: DocumentType | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """List documents for a professional."""
        return await self.repository.list_for_professional(
            professional_id,
            pagination,
            category=category,
            document_type=document_type,
        )
