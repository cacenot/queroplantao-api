"""DocumentType repository for database operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models import DocumentType
from src.shared.infrastructure.repositories.base import BaseRepository
from src.shared.infrastructure.repositories.mixins import SoftDeleteMixin
from src.shared.infrastructure.repositories.organization_scope_mixin import (
    OrganizationScopeMixin,
)


class DocumentTypeRepository(
    OrganizationScopeMixin[DocumentType],
    SoftDeleteMixin[DocumentType],
    BaseRepository[DocumentType],
):
    """
    Repository for DocumentType model.

    Provides CRUD operations with soft delete and organization scope support.
    Document types are scoped by organization and visible within the family.
    """

    model = DocumentType
    default_scope_policy = "FAMILY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def count_documents_linked(self, document_type_id: UUID) -> int:
        """
        Count total documents linked to this document type.

        Counts both professional_documents and screening_documents
        to validate if the type can be safely deleted.

        Args:
            document_type_id: The document type UUID.

        Returns:
            Total count of linked documents.
        """
        # Import here to avoid circular imports
        from src.modules.professionals.domain.models.professional_document import (
            ProfessionalDocument,
        )
        from src.modules.screening.domain.models.screening_document import (
            ScreeningDocument,
        )

        # Count professional documents
        prof_query = select(func.count()).where(
            ProfessionalDocument.document_type_id == document_type_id  # type: ignore[arg-type]
        )
        prof_result = await self.session.execute(prof_query)
        prof_count = prof_result.scalar_one()

        # Count screening documents
        screening_query = select(func.count()).where(
            ScreeningDocument.document_type_id == document_type_id  # type: ignore[arg-type]
        )
        screening_result = await self.session.execute(screening_query)
        screening_count = screening_result.scalar_one()

        return prof_count + screening_count
