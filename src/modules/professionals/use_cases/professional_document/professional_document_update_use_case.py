"""Use case for updating a professional document."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalDocument
from src.modules.professionals.domain.schemas import ProfessionalDocumentUpdate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)


class UpdateProfessionalDocumentUseCase:
    """Use case for updating a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        document_id: UUID,
        professional_id: UUID,
        data: ProfessionalDocumentUpdate,
        organization_id: UUID | None = None,
        updated_by: UUID | None = None,
    ) -> ProfessionalDocument:
        """
        Update an existing document (PATCH semantics).

        Args:
            document_id: The document UUID to update.
            professional_id: The professional UUID.
            data: The partial update data.
            organization_id: The organization UUID (unused, for API consistency).
            updated_by: UUID of the user updating this record (unused, for future audit).
        """
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(document_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(document, field, value)

        return await self.repository.update(document)
