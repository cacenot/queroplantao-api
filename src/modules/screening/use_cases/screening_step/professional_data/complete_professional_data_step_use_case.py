"""Use case for completing professional data step."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningProfessionalNoQualificationError,
    ScreeningProfessionalNotLinkedError,
    ScreeningProfessionalTypeMismatchError,
    ScreeningSpecialtyMismatchError,
    ScreeningStepNotFoundError,
)
from src.modules.professionals.domain.models import ProfessionalType
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)
from src.modules.screening.domain.models import ScreeningProcess, ScreeningStatus
from src.modules.screening.domain.models.enums import StepStatus
from src.modules.screening.domain.schemas.steps import (
    ProfessionalDataStepCompleteRequest,
    ProfessionalDataStepResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ProfessionalDataStepRepository,
)
from src.modules.screening.use_cases.screening_step.helpers import StepWorkflowService


class CompleteProfessionalDataStepUseCase:
    """
    Complete the professional data step (Step 2).

    This step validates that the professional's data is complete and correct.
    The frontend shows the professional's data for the user to review.
    The user can create/edit the professional using the /composite endpoints
    before completing this step.

    Validations:
    - Process must exist and belong to organization
    - Professional data step must exist for the process
    - Step must be IN_PROGRESS
    - User must be assigned to the step (if assigned_to is set)
    - Professional must be linked to the process (organization_professional_id)
    - Professional must have at least one qualification
    - If expected_professional_type is set, it must match
    - If expected_specialty_id is set, professional must have that specialty
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.step_repository = ProfessionalDataStepRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        data: ProfessionalDataStepCompleteRequest,  # noqa: ARG002
        completed_by: UUID,
    ) -> ProfessionalDataStepResponse:
        """
        Complete the professional data step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            data: Request data (empty - only validates state).
            completed_by: User completing the step.

        Returns:
            The completed step response.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist.
            ScreeningStepNotFoundError: If professional data step doesn't exist.
            ScreeningStepAlreadyCompletedError: If step is already completed.
            ScreeningStepNotInProgressError: If step is not in progress.
            ScreeningStepNotAssignedToUserError: If step is not assigned to user.
            ScreeningProfessionalNotLinkedError: If no professional is linked.
            ScreeningProfessionalNoQualificationError: If professional has no qualifications.
            ScreeningProfessionalTypeMismatchError: If professional type doesn't match expected.
            ScreeningSpecialtyMismatchError: If professional doesn't have expected specialty.
        """
        # 1. Load process with steps
        process = await self._load_process_with_steps(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get professional data step
        step = process.professional_data_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="professional-data")

        # 3. Validate step can be completed
        StepWorkflowService.validate_step_can_complete(
            step=step,
            user_id=completed_by,
            check_assignment=True,
        )

        # 4. Validate professional is linked
        if not process.organization_professional_id:
            raise ScreeningProfessionalNotLinkedError(screening_id=str(screening_id))

        professional_id = process.organization_professional_id

        # 5. Load and validate qualifications
        qualifications = await self._get_professional_qualifications(
            organization_id=organization_id,
            professional_id=professional_id,
        )

        if not qualifications:
            raise ScreeningProfessionalNoQualificationError(
                professional_id=str(professional_id)
            )

        # 6. Validate professional type if expected
        if process.expected_professional_type:
            await self._validate_professional_type(
                qualifications=qualifications,
                expected_type=process.expected_professional_type,
            )

        # 7. Validate specialty if expected
        if process.expected_specialty_id:
            await self._validate_specialty(
                qualifications=qualifications,
                expected_specialty_id=process.expected_specialty_id,
                professional_id=professional_id,
            )

        # 8. Update step with professional reference
        step.professional_id = professional_id

        # 9. Complete the step
        StepWorkflowService.complete_step(
            step=step,
            completed_by=completed_by,
            status=StepStatus.APPROVED,
        )

        # Start process if not in progress (legacy, should not happen)
        if process.status != ScreeningStatus.IN_PROGRESS:
            process.status = ScreeningStatus.IN_PROGRESS

        # Advance to next step (document_upload_step)
        StepWorkflowService.advance_to_next_step(
            process=process,
            current_step=step,
            next_step=process.document_upload_step,
        )

        # 10. Persist changes
        await self.session.flush()
        await self.session.refresh(step)

        return ProfessionalDataStepResponse.model_validate(step)

    async def _load_process_with_steps(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with step relationships."""
        from sqlmodel import select

        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .options(
                selectinload(ScreeningProcess.professional_data_step),
                selectinload(ScreeningProcess.document_upload_step),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_professional_qualifications(
        self,
        organization_id: UUID,
        professional_id: UUID,
    ) -> list:
        """
        Get all qualifications for a professional with specialties and educations.

        Args:
            organization_id: Organization ID.
            professional_id: Professional ID.

        Returns:
            List of qualifications with specialties and educations loaded.
        """
        from sqlalchemy import select

        from src.modules.professionals.domain.models import ProfessionalQualification

        query = (
            select(ProfessionalQualification)
            .where(
                ProfessionalQualification.organization_professional_id
                == professional_id
            )
            .where(ProfessionalQualification.organization_id == organization_id)
            .where(ProfessionalQualification.deleted_at.is_(None))
            .options(
                selectinload(ProfessionalQualification.specialties),
                selectinload(ProfessionalQualification.educations),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _validate_professional_type(
        self,
        qualifications: list,
        expected_type: str,
    ) -> None:
        """
        Validate that at least one qualification matches the expected type.

        Args:
            qualifications: List of professional qualifications.
            expected_type: Expected professional type (DOCTOR, NURSE, etc.).

        Raises:
            ScreeningProfessionalTypeMismatchError: If no qualification matches.
        """
        expected_enum = ProfessionalType(expected_type)

        for qualification in qualifications:
            if qualification.professional_type == expected_enum:
                return

        # No matching type found
        found_types = ", ".join(q.professional_type.value for q in qualifications)
        raise ScreeningProfessionalTypeMismatchError(
            expected=expected_type,
            found=found_types,
        )

    async def _validate_specialty(
        self,
        qualifications: list,
        expected_specialty_id: UUID,
        professional_id: UUID,
    ) -> None:
        """
        Validate that professional has the expected specialty.

        Args:
            qualifications: List of professional qualifications.
            expected_specialty_id: Expected specialty ID.
            professional_id: Professional ID.

        Raises:
            ScreeningSpecialtyMismatchError: If specialty not found.
        """
        for qualification in qualifications:
            for specialty in qualification.specialties:
                if specialty.specialty_id == expected_specialty_id:
                    return

        # Specialty not found
        raise ScreeningSpecialtyMismatchError(
            specialty_id=str(expected_specialty_id),
            professional_id=str(professional_id),
        )
