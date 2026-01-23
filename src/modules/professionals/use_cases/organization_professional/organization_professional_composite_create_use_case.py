"""Use case for creating a professional with nested qualification, specialties, and educations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    CouncilRegistrationExistsError,
    DuplicateSpecialtyIdsError,
    GlobalSpecialtyNotFoundError,
    ProfessionalCpfExistsError,
    ProfessionalEmailExistsError,
)
from src.modules.professionals.domain.models import (
    OrganizationProfessional,
    ProfessionalEducation,
    ProfessionalQualification,
    ProfessionalSpecialty,
)
from src.modules.professionals.domain.schemas.organization_professional_composite import (
    OrganizationProfessionalCompositeCreate,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
    SpecialtyRepository,
)


class CreateOrganizationProfessionalCompositeUseCase:
    """
    Use case for creating a professional with full nested data.

    Creates in a single transaction:
    - Professional (basic info + address)
    - One qualification (council registration)
    - Specialties for the qualification
    - Educations for the qualification

    Validates:
    - CPF uniqueness within the organization
    - Email uniqueness within the organization
    - Council registration uniqueness within the organization
    - All specialty_ids exist in global specialties table
    - No duplicate specialty_ids in the request
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = ProfessionalSpecialtyRepository(session)
        self.education_repository = ProfessionalEducationRepository(session)
        self.global_specialty_repository = SpecialtyRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
        created_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Create a professional with nested qualification, specialties, and educations.

        Args:
            organization_id: The organization UUID.
            data: The composite creation data.
            created_by: UUID of the user creating this record.

        Returns:
            The created professional with all nested relations loaded.

        Raises:
            ProfessionalCpfExistsError: If CPF already exists.
            ProfessionalEmailExistsError: If email already exists.
            CouncilRegistrationExistsError: If council registration already exists.
            GlobalSpecialtyNotFoundError: If any specialty_id does not exist.
            DuplicateSpecialtyIdsError: If duplicate specialty_ids in request.
        """
        # 1. Validate professional uniqueness
        await self._validate_professional_uniqueness(organization_id, data)

        # 2. Validate qualification uniqueness
        await self._validate_qualification_uniqueness(organization_id, data)

        # 3. Validate specialties exist and no duplicates
        await self._validate_specialties(data)

        # 4. Create professional
        professional = await self._create_professional(
            organization_id, data, created_by
        )

        # 5. Create qualification
        qualification = await self._create_qualification(
            organization_id, professional.id, data
        )

        # 6. Create specialties
        await self._create_specialties(qualification.id, data)

        # 7. Create educations
        await self._create_educations(qualification.id, data)

        # 8. Commit and return with relations
        await self.session.commit()

        # Reload with relations
        return await self.professional_repository.get_by_id_with_relations(
            professional.id, organization_id
        )  # type: ignore

    async def _validate_professional_uniqueness(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
    ) -> None:
        """Validate CPF and email uniqueness within organization."""
        if data.cpf:
            if await self.professional_repository.exists_by_cpf(
                data.cpf, organization_id
            ):
                raise ProfessionalCpfExistsError()

        if data.email:
            if await self.professional_repository.exists_by_email(
                data.email, organization_id
            ):
                raise ProfessionalEmailExistsError()

    async def _validate_qualification_uniqueness(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
    ) -> None:
        """Validate council registration uniqueness within organization."""
        qualification_data = data.qualification

        if await self.qualification_repository.council_exists_in_organization(
            council_number=qualification_data.council_number,
            council_state=qualification_data.council_state,
            organization_id=organization_id,
        ):
            raise CouncilRegistrationExistsError()

    async def _validate_specialties(
        self,
        data: OrganizationProfessionalCompositeCreate,
    ) -> None:
        """Validate all specialty_ids exist and no duplicates in request."""
        specialty_ids = [s.specialty_id for s in data.qualification.specialties]

        # Check for duplicates in request
        if len(specialty_ids) != len(set(specialty_ids)):
            raise DuplicateSpecialtyIdsError()

        # Validate each specialty exists
        for specialty_id in specialty_ids:
            specialty = await self.global_specialty_repository.get_by_id(specialty_id)
            if specialty is None:
                raise GlobalSpecialtyNotFoundError(specialty_id=str(specialty_id))

    async def _create_professional(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
        created_by: UUID | None,
    ) -> OrganizationProfessional:
        """Create the professional entity."""
        # Extract professional fields (exclude qualification)
        professional_data = data.model_dump(exclude={"qualification"})

        professional = OrganizationProfessional(
            organization_id=organization_id,
            created_by=created_by,
            **professional_data,
        )

        self.session.add(professional)
        await self.session.flush()  # Get the ID without committing

        return professional

    async def _create_qualification(
        self,
        organization_id: UUID,
        professional_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
    ) -> ProfessionalQualification:
        """Create the qualification entity."""
        qualification_data = data.qualification.model_dump(
            exclude={"specialties", "educations"}
        )

        qualification = ProfessionalQualification(
            organization_id=organization_id,
            organization_professional_id=professional_id,
            **qualification_data,
        )

        self.session.add(qualification)
        await self.session.flush()  # Get the ID without committing

        return qualification

    async def _create_specialties(
        self,
        qualification_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
    ) -> list[ProfessionalSpecialty]:
        """Create specialty entities."""
        specialties = []

        for specialty_data in data.qualification.specialties:
            specialty = ProfessionalSpecialty(
                qualification_id=qualification_id,
                **specialty_data.model_dump(),
            )
            self.session.add(specialty)
            specialties.append(specialty)

        if specialties:
            await self.session.flush()

        return specialties

    async def _create_educations(
        self,
        qualification_id: UUID,
        data: OrganizationProfessionalCompositeCreate,
    ) -> list[ProfessionalEducation]:
        """Create education entities."""
        educations = []

        for education_data in data.qualification.educations:
            education = ProfessionalEducation(
                qualification_id=qualification_id,
                **education_data.model_dump(),
            )
            self.session.add(education)
            educations.append(education)

        if educations:
            await self.session.flush()

        return educations
