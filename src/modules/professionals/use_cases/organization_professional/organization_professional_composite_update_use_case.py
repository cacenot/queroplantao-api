"""Use case for updating a professional with nested qualification, specialties, and educations."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi_restkit.filters import UUIDListFilter
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    CouncilRegistrationExistsError,
    CourseNameRequiredError,
    DuplicateSpecialtyIdsError,
    EducationNotFoundError,
    GlobalSpecialtyNotFoundError,
    InstitutionRequiredError,
    LevelRequiredError,
    ProfessionalCpfExistsError,
    ProfessionalEmailExistsError,
    ProfessionalNotFoundError,
    QualificationIdRequiredError,
    QualificationNotBelongsError,
    QualificationNotFoundError,
    SpecialtyAlreadyAssignedError,
    SpecialtyNotFoundError,
)
from src.modules.professionals.domain.models import (
    OrganizationProfessional,
    ProfessionalEducation,
    ProfessionalQualification,
    ProfessionalSpecialty,
)
from src.modules.professionals.domain.schemas.organization_professional_composite import (
    EducationNestedUpdate,
    OrganizationProfessionalCompositeUpdate,
    QualificationNestedUpdate,
    SpecialtyNestedUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalEducationFilter,
    ProfessionalSpecialtyFilter,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
    SpecialtyRepository,
)


class UpdateOrganizationProfessionalCompositeUseCase:
    """
    Use case for updating a professional with full nested data.

    Partial update strategy:
    - Professional fields: PATCH semantics (only update provided fields)
    - Qualification: identified by ID, update provided fields
    - Specialties/Educations:
      - With ID: update existing entity with PATCH semantics
      - Without ID: create new entity
      - IDs not in list: soft delete
      - None list: no changes to that entity type
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
        professional_id: UUID,
        data: OrganizationProfessionalCompositeUpdate,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        updated_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Update a professional with nested qualification, specialties, and educations.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID to update.
            data: The composite update data.
            family_org_ids: List of all organization IDs in the family.
            updated_by: UUID of the user performing the update.

        Returns:
            The updated professional with all nested relations loaded.

        Raises:
            ProfessionalNotFoundError: If professional doesn't exist in the family.
            ProfessionalCpfExistsError: If CPF conflicts in the family.
            ProfessionalEmailExistsError: If email conflicts in the family.
            CouncilRegistrationExistsError: If council registration conflicts in the family.
            DuplicateSpecialtyIdsError: If duplicate specialty_ids in request.
        """
        # 1. Get existing professional (with family scope)
        professional = await self.professional_repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # 2. Validate professional uniqueness within family (if updating cpf/email)
        await self._validate_professional_uniqueness(
            family_org_ids, professional_id, data
        )

        # 3. Update professional fields
        await self._update_professional(professional, data, updated_by)

        # 4. Handle qualification updates (if provided)
        if data.qualification is not None:
            await self._handle_qualification_update(
                organization_id, professional_id, data.qualification, family_org_ids
            )

        # 5. Commit and return with relations
        await self.session.commit()

        return await self.professional_repository.get_by_id_with_relations(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )  # type: ignore

    async def _validate_professional_uniqueness(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        professional_id: UUID,
        data: OrganizationProfessionalCompositeUpdate,
    ) -> None:
        """Validate CPF and email uniqueness within family (excluding current professional)."""
        if data.cpf:
            if await self.professional_repository.exists_by_cpf_in_family(
                cpf=data.cpf,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalCpfExistsError()

        if data.email:
            if await self.professional_repository.exists_by_email_in_family(
                email=data.email,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalEmailExistsError()

    async def _update_professional(
        self,
        professional: OrganizationProfessional,
        data: OrganizationProfessionalCompositeUpdate,
        updated_by: UUID | None,
    ) -> None:
        """Update professional fields with PATCH semantics."""
        # Get only the fields that were explicitly set (exclude qualification)
        update_data = data.model_dump(exclude_unset=True, exclude={"qualification"})

        for field, value in update_data.items():
            if field == "avatar_url" and value is not None:
                value = str(value)
            setattr(professional, field, value)

        professional.updated_by = updated_by
        professional.updated_at = datetime.now(timezone.utc)

        await self.session.flush()

    async def _handle_qualification_update(
        self,
        organization_id: UUID,
        professional_id: UUID,
        qualification_data: QualificationNestedUpdate,
        family_org_ids: list[UUID] | tuple[UUID, ...],
    ) -> None:
        """Handle qualification update with nested specialties and educations."""
        qualification_id = qualification_data.id

        if qualification_id is None:
            raise QualificationIdRequiredError()

        # Get existing qualification
        qualification = await self.qualification_repository.get_by_id_with_relations(
            qualification_id, organization_id
        )
        if qualification is None:
            raise QualificationNotFoundError()

        # Verify qualification belongs to this professional
        if qualification.organization_professional_id != professional_id:
            raise QualificationNotBelongsError()

        # Validate council uniqueness within family if updating
        await self._validate_council_uniqueness(
            family_org_ids, qualification_id, qualification_data, qualification
        )

        # Update qualification fields
        await self._update_qualification(qualification, qualification_data)

        # Handle specialties (if provided - None means no changes)
        if qualification_data.specialties is not None:
            await self._handle_specialties_update(
                qualification_id, qualification_data.specialties
            )

        # Handle educations (if provided - None means no changes)
        if qualification_data.educations is not None:
            await self._handle_educations_update(
                qualification_id, organization_id, qualification_data.educations
            )

    async def _validate_council_uniqueness(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        qualification_id: UUID,
        data: QualificationNestedUpdate,
        current: ProfessionalQualification,
    ) -> None:
        """Validate council registration uniqueness within family if updating."""
        council_number = data.council_number or current.council_number
        council_state = data.council_state or current.council_state

        # Only validate if council info is being changed
        if data.council_number is not None or data.council_state is not None:
            if await self.qualification_repository.council_exists_in_family(
                council_number=council_number,
                council_state=council_state,
                family_org_ids=family_org_ids,
                exclude_id=qualification_id,
            ):
                raise CouncilRegistrationExistsError()

    async def _update_qualification(
        self,
        qualification: ProfessionalQualification,
        data: QualificationNestedUpdate,
    ) -> None:
        """Update qualification fields with PATCH semantics."""
        # Exclude nested entities and id from update
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "specialties",
                "educations",
                "professional_type",
                "council_type",
            },
        )

        for field, value in update_data.items():
            setattr(qualification, field, value)

        qualification.updated_at = datetime.now(timezone.utc)

        await self.session.flush()

    async def _handle_specialties_update(
        self,
        qualification_id: UUID,
        specialties_data: list[SpecialtyNestedUpdate],
    ) -> None:
        """
        Handle specialties partial update.

        Strategy:
        - With ID + other fields: update existing
        - With ID only (no other fields): keep unchanged
        - Without ID: create new
        - Existing IDs not in list: soft delete
        """
        # Get existing specialties
        existing_specialties = await self._get_existing_specialties(qualification_id)
        existing_ids = {s.id for s in existing_specialties}

        # Track IDs in the update request
        provided_ids: set[UUID] = set()
        specialty_ids_to_create: list[UUID] = []

        for specialty_data in specialties_data:
            if specialty_data.id is not None:
                provided_ids.add(specialty_data.id)

                # Check if this is just an ID reference (keep unchanged) or an update
                update_fields = specialty_data.model_dump(
                    exclude_unset=True, exclude={"id"}
                )
                if update_fields:
                    # Update existing specialty
                    await self._update_specialty(
                        qualification_id, specialty_data.id, specialty_data
                    )
            else:
                # Create new specialty
                if specialty_data.specialty_id is None:
                    raise SpecialtyNotFoundError()
                specialty_ids_to_create.append(specialty_data.specialty_id)

        # Validate no duplicate specialty_ids in creates
        all_specialty_ids = specialty_ids_to_create.copy()
        for s in existing_specialties:
            if s.id in provided_ids:
                all_specialty_ids.append(s.specialty_id)

        if len(all_specialty_ids) != len(set(all_specialty_ids)):
            raise DuplicateSpecialtyIdsError()

        # Validate new specialty_ids exist
        for specialty_id in specialty_ids_to_create:
            specialty = await self.global_specialty_repository.get_by_id(specialty_id)
            if specialty is None:
                raise GlobalSpecialtyNotFoundError(specialty_id=str(specialty_id))

        # Check for specialty_id conflicts with existing
        for specialty_id in specialty_ids_to_create:
            if await self.specialty_repository.specialty_exists_for_qualification(
                qualification_id, specialty_id
            ):
                raise SpecialtyAlreadyAssignedError()

        # Create new specialties
        for specialty_data in specialties_data:
            if specialty_data.id is None:
                await self._create_specialty(qualification_id, specialty_data)

        # Soft delete specialties not in the list
        ids_to_delete = existing_ids - provided_ids
        for specialty_id in ids_to_delete:
            await self._soft_delete_specialty(specialty_id)

    async def _get_existing_specialties(
        self, qualification_id: UUID
    ) -> list[ProfessionalSpecialty]:
        """Get all existing specialties for a qualification."""
        filters = ProfessionalSpecialtyFilter(
            qualification_id=UUIDListFilter(values=[qualification_id])
        )
        result = await self.specialty_repository.list(
            filters=filters,
            limit=100,
            offset=0,
        )
        return result.items

    async def _update_specialty(
        self,
        qualification_id: UUID,
        specialty_id: UUID,
        data: SpecialtyNestedUpdate,
    ) -> None:
        """Update an existing specialty."""
        specialty = await self.specialty_repository.get_by_id_for_qualification(
            specialty_id, qualification_id
        )
        if specialty is None:
            raise SpecialtyNotFoundError()

        update_data = data.model_dump(
            exclude_unset=True, exclude={"id", "specialty_id"}
        )

        for field, value in update_data.items():
            setattr(specialty, field, value)

        specialty.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def _create_specialty(
        self,
        qualification_id: UUID,
        data: SpecialtyNestedUpdate,
    ) -> ProfessionalSpecialty:
        """Create a new specialty."""
        specialty_data = data.model_dump(exclude={"id"})

        specialty = ProfessionalSpecialty(
            qualification_id=qualification_id,
            **specialty_data,
        )

        self.session.add(specialty)
        await self.session.flush()
        return specialty

    async def _soft_delete_specialty(self, specialty_id: UUID) -> None:
        """Soft delete a specialty."""
        specialty = await self.specialty_repository.get_by_id(specialty_id)
        if specialty:
            specialty.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def _handle_educations_update(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        educations_data: list[EducationNestedUpdate],
    ) -> None:
        """
        Handle educations partial update.

        Strategy:
        - With ID + other fields: update existing
        - With ID only (no other fields): keep unchanged
        - Without ID: create new
        - Existing IDs not in list: soft delete
        """
        # Get existing educations
        existing_educations = await self._get_existing_educations(qualification_id)
        existing_ids = {e.id for e in existing_educations}

        # Track IDs in the update request
        provided_ids: set[UUID] = set()

        for education_data in educations_data:
            if education_data.id is not None:
                provided_ids.add(education_data.id)

                # Check if this is just an ID reference (keep unchanged) or an update
                update_fields = education_data.model_dump(
                    exclude_unset=True, exclude={"id"}
                )
                if update_fields:
                    # Update existing education
                    await self._update_education(
                        qualification_id, education_data.id, education_data
                    )
            else:
                # Create new education (validate required fields)
                if education_data.level is None:
                    raise LevelRequiredError()
                if education_data.course_name is None:
                    raise CourseNameRequiredError()
                if education_data.institution is None:
                    raise InstitutionRequiredError()

                await self._create_education(
                    qualification_id, organization_id, education_data
                )

        # Soft delete educations not in the list
        ids_to_delete = existing_ids - provided_ids
        for education_id in ids_to_delete:
            await self._soft_delete_education(education_id)

    async def _get_existing_educations(
        self, qualification_id: UUID
    ) -> list[ProfessionalEducation]:
        """Get all existing educations for a qualification."""
        filters = ProfessionalEducationFilter(
            qualification_id=UUIDListFilter(values=[qualification_id])
        )
        result = await self.education_repository.list(
            filters=filters,
            limit=100,
            offset=0,
        )
        return result.items

    async def _update_education(
        self,
        qualification_id: UUID,
        education_id: UUID,
        data: EducationNestedUpdate,
    ) -> None:
        """Update an existing education."""
        education = await self.education_repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise EducationNotFoundError()

        update_data = data.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            setattr(education, field, value)

        education.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def _create_education(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: EducationNestedUpdate,
    ) -> ProfessionalEducation:
        """Create a new education."""
        education_data = data.model_dump(exclude={"id"}, exclude_unset=True)

        # Set defaults for required fields if not provided
        if "is_completed" not in education_data:
            education_data["is_completed"] = False

        education = ProfessionalEducation(
            organization_id=organization_id,
            qualification_id=qualification_id,
            **education_data,
        )

        self.session.add(education)
        await self.session.flush()
        return education

    async def _soft_delete_education(self, education_id: UUID) -> None:
        """Soft delete an education."""
        education = await self.education_repository.get_by_id(education_id)
        if education:
            education.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()
