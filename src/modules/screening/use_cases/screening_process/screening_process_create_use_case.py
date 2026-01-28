"""
Create screening process use case.

Handles Step 1 (Conversation/Creation) - Creates new screening with
minimal professional data and configured steps.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningProcessActiveExistsError
from src.modules.professionals.domain.models.enums import ProfessionalType
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)
from src.modules.screening.domain.models.enums import (
    ScreeningStatus,
    StepStatus,
)
from src.modules.screening.domain.models.screening_process import ScreeningProcess
from src.modules.screening.domain.models.steps import (
    ClientValidationStep,
    ConversationStep,
    DocumentReviewStep,
    DocumentUploadStep,
    PaymentInfoStep,
    ProfessionalDataStep,
    SupervisorReviewStep,
)
from src.modules.screening.domain.schemas import (
    ScreeningProcessCreate,
    ScreeningProcessDetailResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ClientValidationStepRepository,
    ConversationStepRepository,
    DocumentReviewStepRepository,
    DocumentUploadStepRepository,
    OrganizationScreeningSettingsRepository,
    PaymentInfoStepRepository,
    ProfessionalDataStepRepository,
    ScreeningProcessRepository,
    SupervisorReviewStepRepository,
)
from src.shared.domain.value_objects import CPF


class CreateScreeningProcessUseCase:
    """
    Create a new screening process (Step 1 - Conversation/Creation).

    This creates the screening process and professional with minimal data:
    - CPF, name, phone
    - Expected professional type and specialty
    - Assignee and client company (if required)

    The professional is created or linked, and the screening steps
    are generated based on the configuration provided.

    Steps configuration:
    - Required steps (always created): CONVERSATION, PROFESSIONAL_DATA,
      DOCUMENT_UPLOAD, DOCUMENT_REVIEW
    - Optional steps (configurable via include_* fields):
      - PAYMENT_INFO (default: True)
      - SUPERVISOR_REVIEW (default: False)
      - CLIENT_VALIDATION (default: False, auto-enabled if client_company_id set)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.settings_repository = OrganizationScreeningSettingsRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        # Step repositories
        self.conversation_step_repo = ConversationStepRepository(session)
        self.professional_data_step_repo = ProfessionalDataStepRepository(session)
        self.document_upload_step_repo = DocumentUploadStepRepository(session)
        self.document_review_step_repo = DocumentReviewStepRepository(session)
        self.payment_info_step_repo = PaymentInfoStepRepository(session)
        self.supervisor_review_step_repo = SupervisorReviewStepRepository(session)
        self.client_validation_step_repo = ClientValidationStepRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        data: ScreeningProcessCreate,
        created_by: UUID,
        family_org_ids: tuple[UUID, ...] | None = None,
    ) -> ScreeningProcessDetailResponse:
        """
        Execute the screening process creation.

        Args:
            organization_id: The organization creating the screening.
            data: The screening creation data.
            created_by: The user creating the screening (initial assignee).
            family_org_ids: Organization family IDs for professional lookup.

        Returns:
            The created screening process response with steps.

        Raises:
            ScreeningProcessActiveExistsError: If professional has active screening.
        """
        # Get organization settings
        settings = await self.settings_repository.get_or_create_default(organization_id)

        # Check for existing active screening by CPF
        existing = await self.repository.get_active_by_cpf(
            organization_id=organization_id,
            cpf=data.professional_cpf,
        )
        if existing:
            raise ScreeningProcessActiveExistsError()

        # Check if professional exists or create new one
        professional = await self._get_or_create_professional(
            organization_id=organization_id,
            cpf=data.professional_cpf,
            name=data.professional_name,
            phone=data.professional_phone,
            family_org_ids=family_org_ids,
            created_by=created_by,
        )

        # Generate access token
        access_token = self._generate_access_token()
        token_expires_at = datetime.now(UTC) + timedelta(
            hours=settings.token_expiry_hours
        )

        # Create the screening process
        process = ScreeningProcess(
            organization_id=organization_id,
            organization_professional_id=professional.id,
            professional_cpf=data.professional_cpf,
            professional_name=data.professional_name,
            professional_phone=data.professional_phone,
            professional_email=data.professional_email,
            status=ScreeningStatus.IN_PROGRESS,
            expected_professional_type=data.expected_professional_type,
            expected_specialty_id=data.expected_specialty_id,
            owner_id=data.owner_id or created_by,
            current_actor_id=data.owner_id or created_by,
            client_company_id=data.client_company_id,
            access_token=access_token,
            access_token_expires_at=token_expires_at,
            notes=data.notes,
            created_by=created_by,
            updated_by=created_by,
        )
        process = await self.repository.create(process)
        await self.session.flush()

        # Create steps based on configuration
        # Client validation is auto-enabled if client company is provided
        include_client_validation = (
            data.include_client_validation or data.client_company_id is not None
        )

        await self._create_steps(
            process=process,
            include_payment_info=data.include_payment_info,
            include_supervisor_review=data.include_supervisor_review,
            include_client_validation=include_client_validation,
        )

        await self.session.flush()
        await self.session.refresh(process)

        # Re-fetch with all related data for complete response
        process_with_details = await self.repository.get_by_id_with_details(
            entity_id=process.id,
            organization_id=organization_id,
        )

        return ScreeningProcessDetailResponse.model_validate(process_with_details)

    async def _get_or_create_professional(
        self,
        organization_id: UUID,
        cpf: CPF,
        name: str,
        phone: str | None,
        family_org_ids: tuple[UUID, ...] | None,
        created_by: UUID,
    ):
        """Get existing professional or create new one with minimal data."""
        from src.modules.professionals.domain.models import OrganizationProfessional

        # Check if professional exists in family
        existing = await self.professional_repository.get_by_cpf(
            organization_id=organization_id,
            cpf=str(cpf),
            family_org_ids=family_org_ids,
        )
        if existing:
            return existing

        # Create new professional with minimal data
        professional = OrganizationProfessional(
            organization_id=organization_id,
            cpf=str(cpf),
            full_name=name,
            phone=phone,
            professional_type=ProfessionalType.MEDICO,  # Will be updated later
            is_complete=False,  # Mark as incomplete until full data
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.professional_repository.create(professional)

    async def _create_steps(
        self,
        process: ScreeningProcess,
        include_payment_info: bool = True,
        include_supervisor_review: bool = False,
        include_client_validation: bool = False,
    ) -> None:
        """
        Create process steps based on configuration.

        Fixed order (7 possible steps):
        1. CONVERSATION (required) - Initial phone call
        2. PROFESSIONAL_DATA (required) - Personal + qualification + specialties
        3. DOCUMENT_UPLOAD (required) - Upload documents
        4. DOCUMENT_REVIEW (required) - Review documents
        5. PAYMENT_INFO (optional) - Bank account + company
        6. SUPERVISOR_REVIEW (optional) - Escalated review
        7. CLIENT_VALIDATION (optional) - Client approval
        """
        current_order = 1

        # 1. Conversation (required) - starts IN_PROGRESS
        conversation_step = ConversationStep(
            process_id=process.id,
            order=current_order,
            status=StepStatus.IN_PROGRESS,
        )
        await self.conversation_step_repo.create(conversation_step)
        current_order += 1

        # 2. Professional Data (required)
        professional_data_step = ProfessionalDataStep(
            process_id=process.id,
            order=current_order,
            status=StepStatus.PENDING,
        )
        await self.professional_data_step_repo.create(professional_data_step)
        current_order += 1

        # 3. Document Upload (required)
        document_upload_step = DocumentUploadStep(
            process_id=process.id,
            order=current_order,
            status=StepStatus.PENDING,
        )
        await self.document_upload_step_repo.create(document_upload_step)
        current_order += 1

        # 4. Document Review (required)
        document_review_step = DocumentReviewStep(
            process_id=process.id,
            order=current_order,
            status=StepStatus.PENDING,
        )
        await self.document_review_step_repo.create(document_review_step)
        current_order += 1

        # 5. Payment Info (optional)
        if include_payment_info:
            payment_info_step = PaymentInfoStep(
                process_id=process.id,
                order=current_order,
                status=StepStatus.PENDING,
            )
            await self.payment_info_step_repo.create(payment_info_step)
            current_order += 1

        # 6. Supervisor Review (optional)
        if include_supervisor_review:
            supervisor_review_step = SupervisorReviewStep(
                process_id=process.id,
                order=current_order,
                status=StepStatus.PENDING,
            )
            await self.supervisor_review_step_repo.create(supervisor_review_step)
            current_order += 1

        # 7. Client Validation (optional)
        if include_client_validation:
            client_validation_step = ClientValidationStep(
                process_id=process.id,
                order=current_order,
                status=StepStatus.PENDING,
            )
            await self.client_validation_step_repo.create(client_validation_step)

    def _generate_access_token(self) -> str:
        """Generate a secure access token for professional self-service."""
        import secrets

        return secrets.token_urlsafe(32)
