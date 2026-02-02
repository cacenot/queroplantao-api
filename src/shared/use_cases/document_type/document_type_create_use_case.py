"""Use case for creating a document type."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models import DocumentType
from src.shared.domain.schemas.document_type import DocumentTypeCreate
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from src.shared.use_cases.document_type.cache import invalidate_document_types_cache


class CreateDocumentTypeUseCase:
    """Use case for creating a document type."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        parent_org_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        data: DocumentTypeCreate,
        created_by: UUID | None = None,
    ) -> DocumentType:
        """
        Create a new document type.

        Args:
            organization_id: The organization creating this document type.
            parent_org_id: The parent organization ID (for cache key).
            family_org_ids: All organization IDs in the family.
            data: Document type creation data.
            created_by: User ID creating this document type.

        Returns:
            The created document type.
        """
        # Create document type
        document_type = DocumentType(
            organization_id=organization_id,
            created_by=created_by,
            **data.model_dump(),
        )
        result = await self.repository.create(document_type)

        # Invalidate cache
        await invalidate_document_types_cache(parent_org_id)

        return result
