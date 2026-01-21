"""Use case for retrieving a professional document."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalDocument
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)


class GetProfessionalDocumentUseCase:
    """Use case for retrieving a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        document_id: UUID,
        professional_id: UUID,
    ) -> ProfessionalDocument:
        """Get a document by ID."""
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(document_id),
            )

        return document
