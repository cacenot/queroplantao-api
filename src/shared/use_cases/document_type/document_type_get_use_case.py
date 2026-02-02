"""Use case for getting a document type by ID."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import DocumentTypeNotFoundError
from src.shared.domain.models import DocumentType
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)


class GetDocumentTypeUseCase:
    """Use case for getting a document type by ID."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        document_type_id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
    ) -> DocumentType:
        """
        Get a document type by ID within organization scope.

        Args:
            document_type_id: The document type UUID.
            organization_id: The current organization UUID.
            family_org_ids: All organization IDs in the family.

        Returns:
            The document type.

        Raises:
            DocumentTypeNotFoundError: If document type not found.
        """
        document_type = await self.repository.get_by_organization(
            id=document_type_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if document_type is None:
            raise DocumentTypeNotFoundError()

        return document_type
