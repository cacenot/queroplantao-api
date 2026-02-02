"""
Create screening process use case.

Handles Step 1 (Conversation/Creation) - Creates new screening with
minimal professional data and configured steps.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ProfessionalNotFoundError,
    ScreeningProcessActiveExistsError,
)
from src.modules.professionals.domain.models.organization_professional import (
    OrganizationProfessional,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)
from src.modules.screening.domain.models.enums import (
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.organization_screening_settings import (
    OrganizationScreeningSettings,
)
from src.modules.screening.domain.models.screening_process import ScreeningProcess
from src.modules.screening.domain.models.steps import (
    ClientValidationStep,
    ConversationStep,
    DocumentReviewStep,
    DocumentUploadStep,
    PaymentInfoStep,
    ProfessionalDataStep,
)
from src.modules.screening.domain.schemas import (
    ScreeningProcessCreate,
    ScreeningProcessDetailResponse,
)
from src.modules.screening.domain.schemas.screening_process import (
    OrganizationProfessionalSummary,
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
)
from src.modules.users.domain.schemas.organization_user import UserInfo
from src.modules.users.infrastructure.repositories import UserRepository
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)
from src.modules.professionals.domain.schemas import SpecialtySummary


class CreateScreeningProcessUseCase:
    """
    Create a new screening process (Step 1 - Conversation/Creation).

    This creates the screening process and professional with minimal data:
    - CPF, name, phone
    - Expected professional type and specialty
    - Assignee and client company (if required)

    The professional is linked if it already exists in the organization family.
    If it doesn't exist yet, `organization_professional_id` is left as `None` and
    will be filled later during the PROFESSIONAL_DATA step.

        Steps configuration:
        - Required steps (always created): CONVERSATION, PROFESSIONAL_DATA,
            DOCUMENT_UPLOAD, DOCUMENT_REVIEW
        - Optional steps (PAYMENT_INFO, CLIENT_VALIDATION) are temporarily disabled
            during creation and will be enabled again in a future iteration.

    Alert system:
    - Supervisor review is now handled via alerts, not as a step
    - Alerts can be created at any point during the screening
    - supervisor_id is required for alert resolution
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.settings_repository = OrganizationScreeningSettingsRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.user_repository = UserRepository(session)
        self.specialty_repository = SpecialtyRepository(session)
        # Step repositories
        self.conversation_step_repo = ConversationStepRepository(session)
        self.professional_data_step_repo = ProfessionalDataStepRepository(session)
        self.document_upload_step_repo = DocumentUploadStepRepository(session)
        self.document_review_step_repo = DocumentReviewStepRepository(session)
        self.payment_info_step_repo = PaymentInfoStepRepository(session)
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
        settings = await self._get_settings(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        existing_professional = await self._resolve_existing_professional(
            organization_id=organization_id,
            professional_id=data.organization_professional_id,
            family_org_ids=family_org_ids,
        )

        professional_cpf = self._get_professional_cpf(
            data=data,
            existing_professional=existing_professional,
        )

        await self._ensure_no_active_screening(
            organization_id=organization_id,
            professional_cpf=professional_cpf,
            family_org_ids=family_org_ids,
        )

        if existing_professional is None and professional_cpf is not None:
            existing_professional = await self._link_professional_by_cpf(
                organization_id=organization_id,
                professional_cpf=professional_cpf,
                family_org_ids=family_org_ids,
            )

        include_payment_info = False
        include_client_validation = False
        configured_step_types = self._build_configured_step_types(
            include_payment_info=include_payment_info,
            include_client_validation=include_client_validation,
        )

        access_token = self._generate_access_token()
        token_expires_at = datetime.now(UTC) + timedelta(
            hours=settings.token_expiry_hours
        )

        process = self._build_screening_process(
            organization_id=organization_id,
            data=data,
            created_by=created_by,
            existing_professional=existing_professional,
            professional_cpf=professional_cpf,
            configured_step_types=configured_step_types,
            access_token=access_token,
            token_expires_at=token_expires_at,
        )
        process = await self.repository.create(process)
        await self.session.flush()

        # Create steps based on configuration
        await self._create_steps(
            process=process,
            include_payment_info=include_payment_info,
            include_client_validation=include_client_validation,
        )

        await self.session.flush()
        await self.session.refresh(process)

        # Re-fetch with all related data for complete response
        process_with_details = await self.repository.get_by_id_with_details(
            id=process.id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        professional_summary: OrganizationProfessionalSummary | None = None
        if process_with_details and process_with_details.organization_professional:
            professional_summary = OrganizationProfessionalSummary.model_validate(
                process_with_details.organization_professional
            )

        response = ScreeningProcessDetailResponse.model_validate(process_with_details)
        if process_with_details:
            response = response.model_copy(
                update={"step_info": process_with_details.step_info}
            )
        return response.model_copy(
            update={
                "professional": professional_summary,
                "expected_specialty": await self._get_specialty_summary(
                    process_with_details.expected_specialty_id
                    if process_with_details
                    else None
                ),
                "owner": await self._get_user_summary(created_by),
                "current_actor": await self._get_user_summary(created_by),
                "supervisor": await self._get_user_summary(
                    process_with_details.supervisor_id if process_with_details else None
                ),
            }
        )

    async def _get_user_summary(self, user_id: UUID | None) -> UserInfo | None:
        if user_id is None:
            return None
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        return UserInfo.model_validate(user)

    async def _get_specialty_summary(
        self, specialty_id: UUID | None
    ) -> SpecialtySummary | None:
        if specialty_id is None:
            return None
        specialty = await self.specialty_repository.get_by_id(specialty_id)
        if specialty is None:
            return None
        return SpecialtySummary.model_validate(specialty)

    async def _get_settings(
        self,
        organization_id: UUID,
        family_org_ids: tuple[UUID, ...] | None,
    ) -> OrganizationScreeningSettings:
        return await self.settings_repository.get_or_create_default(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

    async def _resolve_existing_professional(
        self,
        organization_id: UUID,
        professional_id: UUID | None,
        family_org_ids: tuple[UUID, ...] | None,
    ) -> OrganizationProfessional | None:
        if professional_id is None:
            return None

        existing_professional = (
            await self.professional_repository.get_by_id_for_organization(
                id=professional_id,
                organization_id=organization_id,
                family_org_ids=family_org_ids,
            )
        )
        if not existing_professional:
            raise ProfessionalNotFoundError(
                details={"professional_id": str(professional_id)}
            )

        return existing_professional

    def _get_professional_cpf(
        self,
        data: ScreeningProcessCreate,
        existing_professional: OrganizationProfessional | None,
    ) -> str | None:
        if data.professional_cpf is not None:
            return str(data.professional_cpf)

        return existing_professional.cpf if existing_professional else None

    async def _ensure_no_active_screening(
        self,
        organization_id: UUID,
        professional_cpf: str | None,
        family_org_ids: tuple[UUID, ...] | None,
    ) -> None:
        if professional_cpf is None:
            return

        existing = await self.repository.get_active_by_cpf(
            organization_id=organization_id,
            cpf=professional_cpf,
            family_org_ids=family_org_ids,
        )
        if existing:
            raise ScreeningProcessActiveExistsError()

    async def _link_professional_by_cpf(
        self,
        organization_id: UUID,
        professional_cpf: str,
        family_org_ids: tuple[UUID, ...] | None,
    ) -> OrganizationProfessional | None:
        return await self.professional_repository.get_by_cpf(
            organization_id=organization_id,
            cpf=professional_cpf,
            family_org_ids=family_org_ids,
        )

    def _build_screening_process(
        self,
        organization_id: UUID,
        data: ScreeningProcessCreate,
        created_by: UUID,
        existing_professional: OrganizationProfessional | None,
        professional_cpf: str | None,
        configured_step_types: list[str],
        access_token: str,
        token_expires_at: datetime,
    ) -> ScreeningProcess:
        professional_name = (
            data.professional_name
            if data.professional_name is not None
            else (existing_professional.full_name if existing_professional else None)
        )
        professional_phone = str(data.professional_phone)
        professional_email = data.professional_email or (
            existing_professional.email if existing_professional else None
        )

        return ScreeningProcess(
            organization_id=organization_id,
            organization_professional_id=(
                existing_professional.id if existing_professional else None
            ),
            professional_cpf=professional_cpf,
            professional_name=professional_name,
            professional_phone=professional_phone,
            professional_email=professional_email,
            status=ScreeningStatus.IN_PROGRESS,
            current_step_type=StepType.CONVERSATION,
            configured_step_types=configured_step_types,
            step_info=self._build_step_info(configured_step_types),
            expected_professional_type=data.expected_professional_type,
            expected_specialty_id=data.expected_specialty_id,
            owner_id=created_by,
            current_actor_id=created_by,
            supervisor_id=data.supervisor_id,
            client_company_id=data.client_company_id,
            access_token=access_token,
            access_token_expires_at=token_expires_at,
            notes=data.notes,
            created_by=created_by,
            updated_by=created_by,
        )

    def _build_step_info(
        self, configured_step_types: list[str]
    ) -> dict[str, dict[str, object]]:
        step_info: dict[str, dict[str, object]] = {}
        for step_type in configured_step_types:
            is_current = step_type == StepType.CONVERSATION.value
            step_info[step_type] = {
                "status": StepStatus.IN_PROGRESS.value
                if is_current
                else StepStatus.PENDING.value,
                "completed": False,
                "current_step": is_current,
            }
        return step_info

    async def _create_steps(
        self,
        process: ScreeningProcess,
        include_payment_info: bool = True,
        include_client_validation: bool = False,
    ) -> None:
        """
        Create process steps based on configuration.

        Fixed order (6 possible steps):
        1. CONVERSATION (required) - Initial phone call
        2. PROFESSIONAL_DATA (required) - Personal + qualification + specialties
        3. DOCUMENT_UPLOAD (required) - Upload documents
        4. DOCUMENT_REVIEW (required) - Review documents
        5. PAYMENT_INFO (optional) - Bank account + company
        6. CLIENT_VALIDATION (optional) - Client approval
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

        # 6. Client Validation (optional)
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

    def _build_configured_step_types(
        self,
        include_payment_info: bool = True,
        include_client_validation: bool = False,
    ) -> list[str]:
        """
        Build list of configured step types based on options.

        Returns list of step type values as strings (for ARRAY(String) column).
        """
        step_types: list[str] = [
            StepType.CONVERSATION.value,
            StepType.PROFESSIONAL_DATA.value,
            StepType.DOCUMENT_UPLOAD.value,
            StepType.DOCUMENT_REVIEW.value,
        ]

        if include_payment_info:
            step_types.append(StepType.PAYMENT_INFO.value)

        if include_client_validation:
            step_types.append(StepType.CLIENT_VALIDATION.value)

        return step_types
