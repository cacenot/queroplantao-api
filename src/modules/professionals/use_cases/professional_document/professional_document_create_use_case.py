"""Use case for creating a professional document."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    DocumentQualificationCategoryError,
    DocumentSpecialtyCategoryError,
    ProfessionalNotFoundError,
    QualificationNotFoundError,
    SpecialtyNotFoundError,
)
from src.modules.professionals.domain.models import ProfessionalDocument
from src.modules.professionals.domain.schemas import ProfessionalDocumentCreate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalDocumentRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
)
from src.shared.domain.models import DocumentCategory


class CreateProfessionalDocumentUseCase:
    """Use case for creating a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalDocumentCreate,
    ) -> ProfessionalDocument:
        """
        Create a new document for a professional.

        Validates:
        - Professional exists in organization
        - If qualification_id provided, it exists
        - If specialty_id provided, it exists
        - Document category matches the linked entity
        """
        # Verify professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Validate qualification if provided
        if data.qualification_id:
            qualification = (
                await self.qualification_repository.get_by_id_for_organization(
                    data.qualification_id, organization_id
                )
            )
            if qualification is None:
                raise QualificationNotFoundError()
            if data.document_category != DocumentCategory.QUALIFICATION:
                raise DocumentQualificationCategoryError()

        # Validate specialty if provided
        if data.specialty_id:
            # Note: specialty_id here refers to professional_specialty, not the specialty table
            professional_specialty = await self.specialty_repository.get_by_id(
                data.specialty_id
            )
            if professional_specialty is None:
                raise SpecialtyNotFoundError()
            if data.document_category != DocumentCategory.SPECIALTY:
                raise DocumentSpecialtyCategoryError()

        document = ProfessionalDocument(
            organization_professional_id=professional_id,
            **data.model_dump(),
        )

        return await self.repository.create(document)
