"""Use cases for ProfessionalEducation."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import (
    EducationLevel,
    ProfessionalEducation,
)
from src.modules.professionals.domain.schemas import (
    ProfessionalEducationCreate,
    ProfessionalEducationUpdate,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
)


class CreateProfessionalEducationUseCase:
    """Use case for creating a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: ProfessionalEducationCreate,
    ) -> ProfessionalEducation:
        """
        Create a new education record for a qualification.

        Validates:
        - Qualification exists in organization
        """
        # Verify qualification exists
        qualification = await self.qualification_repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        education = ProfessionalEducation(
            qualification_id=qualification_id,
            **data.model_dump(),
        )

        return await self.repository.create(education)


class UpdateProfessionalEducationUseCase:
    """Use case for updating a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        education_id: UUID,
        qualification_id: UUID,
        data: ProfessionalEducationUpdate,
    ) -> ProfessionalEducation:
        """Update an existing education record (PATCH semantics)."""
        education = await self.repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise NotFoundError(
                resource="ProfessionalEducation",
                identifier=str(education_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(education, field, value)

        return await self.repository.update(education)


class DeleteProfessionalEducationUseCase:
    """Use case for soft-deleting a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        education_id: UUID,
        qualification_id: UUID,
    ) -> None:
        """Soft delete an education record."""
        education = await self.repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise NotFoundError(
                resource="ProfessionalEducation",
                identifier=str(education_id),
            )

        await self.repository.soft_delete(education_id)


class GetProfessionalEducationUseCase:
    """Use case for retrieving a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        education_id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalEducation:
        """Get an education record by ID."""
        education = await self.repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise NotFoundError(
                resource="ProfessionalEducation",
                identifier=str(education_id),
            )

        return education


class ListProfessionalEducationsUseCase:
    """Use case for listing education records for a qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
        *,
        level: EducationLevel | None = None,
        is_completed: bool | None = None,
    ) -> PaginatedResponse[ProfessionalEducation]:
        """List education records for a qualification."""
        return await self.repository.list_for_qualification(
            qualification_id,
            pagination,
            level=level,
            is_completed=is_completed,
        )
