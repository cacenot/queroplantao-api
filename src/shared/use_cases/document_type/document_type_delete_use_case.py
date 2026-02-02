"""Use case for deleting (soft delete) a document type."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import DocumentTypeInUseError, DocumentTypeNotFoundError
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from src.shared.use_cases.document_type.cache import invalidate_document_types_cache


class DeleteDocumentTypeUseCase:
    """Use case for soft deleting a document type."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        document_type_id: UUID,
        organization_id: UUID,
        parent_org_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
    ) -> None:
        """
        Soft delete a document type.

        Args:
            document_type_id: The document type UUID.
            organization_id: The current organization UUID.
            parent_org_id: The parent organization ID (for cache key).
            family_org_ids: All organization IDs in the family.

        Raises:
            DocumentTypeNotFoundError: If document type not found.
            DocumentTypeInUseError: If document type has linked documents.
        """
        # Verify document type exists in organization scope
        document_type = await self.repository.get_by_organization(
            id=document_type_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if document_type is None:
            raise DocumentTypeNotFoundError()

        # Check if document type is in use
        linked_count = await self.repository.count_documents_linked(document_type_id)
        if linked_count > 0:
            raise DocumentTypeInUseError(
                details={"linked_documents_count": linked_count}
            )

        # Soft delete
        await self.repository.delete(document_type_id)

        # Invalidate cache
        await invalidate_document_types_cache(parent_org_id)
