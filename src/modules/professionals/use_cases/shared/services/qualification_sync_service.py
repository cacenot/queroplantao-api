"""Service for syncing qualifications from version snapshots.

This service handles the sync of qualifications including nested specialties
and educations. It uses council_type + council_number + council_state as the
natural key for matching qualifications.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi_restkit.filters import ListFilter
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    CouncilRegistrationExistsError,
    CourseNameRequiredError,
    DuplicateSpecialtyIdsError,
    GlobalSpecialtyNotFoundError,
    InstitutionRequiredError,
    LevelRequiredError,
)
from src.modules.professionals.domain.models import (
    ProfessionalEducation,
    ProfessionalQualification,
    ProfessionalSpecialty,
)
from src.modules.professionals.domain.schemas.professional_version import (
    EducationInput,
    QualificationInput,
    SpecialtyInput,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalEducationFilter,
    ProfessionalQualificationFilter,
    ProfessionalSpecialtyFilter,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
    SpecialtyRepository,
)


class QualificationSyncService:
    """
    Service for syncing qualification data from version snapshots.

    Handles create/update/delete logic for qualifications and their
    nested entities (specialties, educations).

    Matching strategy for qualifications:
    - Match by council_type + council_number + council_state (natural key)
    - If match found: update existing qualification
    - If no match: create new qualification
    - Existing qualifications not in snapshot: soft delete
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = ProfessionalSpecialtyRepository(session)
        self.education_repository = ProfessionalEducationRepository(session)
        self.global_specialty_repository = SpecialtyRepository(session)

    async def sync_qualifications(
        self,
        professional_id: UUID,
        organization_id: UUID,
        qualifications_data: list[QualificationInput],
        family_org_ids: list[UUID] | tuple[UUID, ...],
        updated_by: UUID,
    ) -> list[ProfessionalQualification]:
        """
        Sync qualifications from snapshot to database.

        Args:
            professional_id: The professional UUID.
            organization_id: The organization UUID.
            qualifications_data: List of qualifications from the snapshot.
            family_org_ids: Family org IDs for council uniqueness validation.
            updated_by: UUID of user performing the sync.

        Returns:
            List of synced qualifications.

        Raises:
            CouncilRegistrationExistsError: If council registration conflicts.
            DuplicateSpecialtyIdsError: If duplicate specialty_ids in request.
            GlobalSpecialtyNotFoundError: If referenced specialty doesn't exist.
        """
        # Get existing qualifications for this professional
        existing_qualifications = await self._get_existing_qualifications(
            professional_id
        )

        # Build lookup by natural key: (council_type, council_number, council_state)
        existing_by_council: dict[tuple[str, str, str], ProfessionalQualification] = {}
        for qual in existing_qualifications:
            key = (
                qual.council_type.value,
                qual.council_number,
                qual.council_state,
            )
            existing_by_council[key] = qual

        # Track which existing qualifications were matched
        matched_ids: set[UUID] = set()
        result: list[ProfessionalQualification] = []

        for qual_data in qualifications_data:
            # Build natural key from input
            council_key = (
                qual_data.council_type.value,
                qual_data.council_number,
                str(qual_data.council_state),
            )

            existing_qual = existing_by_council.get(council_key)

            if existing_qual:
                # Update existing qualification
                matched_ids.add(existing_qual.id)
                updated_qual = await self._update_qualification(
                    qualification=existing_qual,
                    data=qual_data,
                    updated_by=updated_by,
                )
                result.append(updated_qual)
            else:
                # Validate council uniqueness in family before creating
                if await self.qualification_repository.council_exists_in_family(
                    council_number=qual_data.council_number,
                    council_state=str(qual_data.council_state),
                    family_org_ids=family_org_ids,
                ):
                    raise CouncilRegistrationExistsError()

                # Create new qualification
                new_qual = await self._create_qualification(
                    professional_id=professional_id,
                    organization_id=organization_id,
                    data=qual_data,
                    updated_by=updated_by,
                )
                result.append(new_qual)

        # Soft delete qualifications not in snapshot
        for qual in existing_qualifications:
            if qual.id not in matched_ids:
                await self._soft_delete_qualification(qual)

        await self.session.flush()
        return result

    async def _get_existing_qualifications(
        self,
        professional_id: UUID,
    ) -> list[ProfessionalQualification]:
        """Get all existing qualifications for a professional."""
        filters = ProfessionalQualificationFilter(
            organization_professional_id=ListFilter(values=[professional_id])
        )
        paginated = await self.qualification_repository.list(
            filters=filters,
            limit=100,
            offset=0,
        )
        return paginated.items

    async def _create_qualification(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: QualificationInput,
        updated_by: UUID,
    ) -> ProfessionalQualification:
        """Create a new qualification with nested entities."""
        qualification = ProfessionalQualification(
            organization_id=organization_id,
            organization_professional_id=professional_id,
            professional_type=data.professional_type,
            is_primary=data.is_primary,
            graduation_year=data.graduation_year,
            council_type=data.council_type,
            council_number=data.council_number,
            council_state=str(data.council_state),
            created_by=updated_by,
            updated_by=updated_by,
        )
        self.session.add(qualification)
        await self.session.flush()

        # Sync nested entities
        await self._sync_specialties(
            qualification_id=qualification.id,
            specialties_data=data.specialties,
            updated_by=updated_by,
        )
        await self._sync_educations(
            qualification_id=qualification.id,
            organization_id=organization_id,
            educations_data=data.educations,
            updated_by=updated_by,
        )

        return qualification

    async def _update_qualification(
        self,
        qualification: ProfessionalQualification,
        data: QualificationInput,
        updated_by: UUID,
    ) -> ProfessionalQualification:
        """Update an existing qualification with nested entities."""
        # Update qualification fields (council fields are natural key, don't update)
        qualification.professional_type = data.professional_type
        qualification.is_primary = data.is_primary
        qualification.graduation_year = data.graduation_year
        qualification.updated_by = updated_by
        qualification.updated_at = datetime.now(timezone.utc)

        await self.session.flush()

        # Sync nested entities
        await self._sync_specialties(
            qualification_id=qualification.id,
            specialties_data=data.specialties,
            updated_by=updated_by,
        )
        await self._sync_educations(
            qualification_id=qualification.id,
            organization_id=qualification.organization_id,
            educations_data=data.educations,
            updated_by=updated_by,
        )

        return qualification

    async def _soft_delete_qualification(
        self,
        qualification: ProfessionalQualification,
    ) -> None:
        """Soft delete a qualification and its nested entities."""
        qualification.deleted_at = datetime.now(timezone.utc)

        # Also soft delete nested entities
        existing_specialties = await self._get_existing_specialties(qualification.id)
        for specialty in existing_specialties:
            specialty.deleted_at = datetime.now(timezone.utc)

        existing_educations = await self._get_existing_educations(qualification.id)
        for education in existing_educations:
            education.deleted_at = datetime.now(timezone.utc)

        await self.session.flush()

    # =========================================================================
    # Specialties Sync
    # =========================================================================

    async def _sync_specialties(
        self,
        qualification_id: UUID,
        specialties_data: list[SpecialtyInput],
        updated_by: UUID,
    ) -> list[ProfessionalSpecialty]:
        """
        Sync specialties for a qualification.

        Strategy:
        - Match by specialty_id (reference to global specialty)
        - If match found: update existing
        - If no match: create new
        - Existing not in snapshot: soft delete
        """
        existing_specialties = await self._get_existing_specialties(qualification_id)

        # Build lookup by specialty_id
        existing_by_specialty_id: dict[UUID, ProfessionalSpecialty] = {
            s.specialty_id: s for s in existing_specialties
        }

        # Track matched and validate duplicates
        matched_ids: set[UUID] = set()
        specialty_ids_in_request: list[UUID] = []
        result: list[ProfessionalSpecialty] = []

        for spec_data in specialties_data:
            specialty_ids_in_request.append(spec_data.specialty_id)

        # Validate no duplicate specialty_ids
        if len(specialty_ids_in_request) != len(set(specialty_ids_in_request)):
            raise DuplicateSpecialtyIdsError()

        for spec_data in specialties_data:
            # Validate global specialty exists
            global_specialty = await self.global_specialty_repository.get_by_id(
                spec_data.specialty_id
            )
            if global_specialty is None:
                raise GlobalSpecialtyNotFoundError(
                    specialty_id=str(spec_data.specialty_id)
                )

            existing_spec = existing_by_specialty_id.get(spec_data.specialty_id)

            if existing_spec:
                # Update existing
                matched_ids.add(existing_spec.id)
                updated_spec = await self._update_specialty(
                    specialty=existing_spec,
                    data=spec_data,
                    updated_by=updated_by,
                )
                result.append(updated_spec)
            else:
                # Create new
                new_spec = await self._create_specialty(
                    qualification_id=qualification_id,
                    data=spec_data,
                    updated_by=updated_by,
                )
                result.append(new_spec)

        # Soft delete specialties not in snapshot
        for spec in existing_specialties:
            if spec.id not in matched_ids:
                spec.deleted_at = datetime.now(timezone.utc)

        await self.session.flush()
        return result

    async def _get_existing_specialties(
        self,
        qualification_id: UUID,
    ) -> list[ProfessionalSpecialty]:
        """Get all existing specialties for a qualification."""
        filters = ProfessionalSpecialtyFilter(
            qualification_id=ListFilter(values=[qualification_id])
        )
        paginated = await self.specialty_repository.list(
            filters=filters,
            limit=100,
            offset=0,
        )
        return paginated.items

    async def _create_specialty(
        self,
        qualification_id: UUID,
        data: SpecialtyInput,
        updated_by: UUID,
    ) -> ProfessionalSpecialty:
        """Create a new specialty."""
        from src.modules.professionals.domain.models.enums import ResidencyStatus

        specialty = ProfessionalSpecialty(
            qualification_id=qualification_id,
            specialty_id=data.specialty_id,
            is_primary=data.is_primary,
            rqe_number=data.rqe_number,
            rqe_state=str(data.rqe_state) if data.rqe_state else None,
            residency_status=data.residency_status or ResidencyStatus.COMPLETED,
            residency_institution=data.residency_institution,
            residency_expected_completion=(
                data.residency_expected_completion.isoformat()
                if data.residency_expected_completion
                else None
            ),
            certificate_url=str(data.certificate_url) if data.certificate_url else None,
            created_by=updated_by,
            updated_by=updated_by,
        )
        self.session.add(specialty)
        await self.session.flush()
        return specialty

    async def _update_specialty(
        self,
        specialty: ProfessionalSpecialty,
        data: SpecialtyInput,
        updated_by: UUID,
    ) -> ProfessionalSpecialty:
        """Update an existing specialty."""
        from src.modules.professionals.domain.models.enums import ResidencyStatus

        specialty.is_primary = data.is_primary
        specialty.rqe_number = data.rqe_number
        specialty.rqe_state = str(data.rqe_state) if data.rqe_state else None
        specialty.residency_status = data.residency_status or ResidencyStatus.COMPLETED
        specialty.residency_institution = data.residency_institution
        specialty.residency_expected_completion = (
            data.residency_expected_completion.isoformat()
            if data.residency_expected_completion
            else None
        )
        specialty.certificate_url = (
            str(data.certificate_url) if data.certificate_url else None
        )
        specialty.updated_by = updated_by
        specialty.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        return specialty

    # =========================================================================
    # Educations Sync
    # =========================================================================

    async def _sync_educations(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        educations_data: list[EducationInput],
        updated_by: UUID,
    ) -> list[ProfessionalEducation]:
        """
        Sync educations for a qualification.

        Strategy:
        - Match by (level, course_name, institution) as natural key
        - If match found: update existing
        - If no match: create new
        - Existing not in snapshot: soft delete
        """
        existing_educations = await self._get_existing_educations(qualification_id)

        # Build lookup by natural key: (level, course_name, institution)
        existing_by_key: dict[tuple[str, str, str], ProfessionalEducation] = {}
        for edu in existing_educations:
            key = (
                edu.level.value,
                edu.course_name,
                edu.institution,
            )
            existing_by_key[key] = edu

        matched_ids: set[UUID] = set()
        result: list[ProfessionalEducation] = []

        for edu_data in educations_data:
            # Validate required fields
            if edu_data.level is None:
                raise LevelRequiredError()
            if not edu_data.course_name:
                raise CourseNameRequiredError()
            if not edu_data.institution:
                raise InstitutionRequiredError()

            # Build natural key from input
            edu_key = (
                edu_data.level.value,
                edu_data.course_name,
                edu_data.institution,
            )

            existing_edu = existing_by_key.get(edu_key)

            if existing_edu:
                # Update existing
                matched_ids.add(existing_edu.id)
                updated_edu = await self._update_education(
                    education=existing_edu,
                    data=edu_data,
                    updated_by=updated_by,
                )
                result.append(updated_edu)
            else:
                # Create new
                new_edu = await self._create_education(
                    qualification_id=qualification_id,
                    organization_id=organization_id,
                    data=edu_data,
                    updated_by=updated_by,
                )
                result.append(new_edu)

        # Soft delete educations not in snapshot
        for edu in existing_educations:
            if edu.id not in matched_ids:
                edu.deleted_at = datetime.now(timezone.utc)

        await self.session.flush()
        return result

    async def _get_existing_educations(
        self,
        qualification_id: UUID,
    ) -> list[ProfessionalEducation]:
        """Get all existing educations for a qualification."""
        filters = ProfessionalEducationFilter(
            qualification_id=ListFilter(values=[qualification_id])
        )
        paginated = await self.education_repository.list(
            filters=filters,
            limit=100,
            offset=0,
        )
        return paginated.items

    async def _create_education(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: EducationInput,
        updated_by: UUID,
    ) -> ProfessionalEducation:
        """Create a new education."""
        education = ProfessionalEducation(
            organization_id=organization_id,
            qualification_id=qualification_id,
            level=data.level,
            course_name=data.course_name,
            institution=data.institution,
            start_year=data.start_year,
            end_year=data.end_year,
            is_completed=data.is_completed,
            workload_hours=data.workload_hours,
            certificate_url=str(data.certificate_url) if data.certificate_url else None,
            notes=data.notes,
            created_by=updated_by,
            updated_by=updated_by,
        )
        self.session.add(education)
        await self.session.flush()
        return education

    async def _update_education(
        self,
        education: ProfessionalEducation,
        data: EducationInput,
        updated_by: UUID,
    ) -> ProfessionalEducation:
        """Update an existing education."""
        education.start_year = data.start_year
        education.end_year = data.end_year
        education.is_completed = data.is_completed
        education.workload_hours = data.workload_hours
        education.certificate_url = (
            str(data.certificate_url) if data.certificate_url else None
        )
        education.notes = data.notes
        education.updated_by = updated_by
        education.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        return education
