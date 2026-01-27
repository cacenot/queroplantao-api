"""
Create screening process use case.

Handles Step 1 (Conversation/Creation) - Creates new screening with
minimal professional data.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models.enums import ProfessionalType
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)
from src.modules.screening.domain.models import (
    ScreeningProcess,
    ScreeningProcessStep,
    ScreeningRequiredDocument,
)
from src.modules.screening.domain.models.enums import (
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.schemas import (
    ScreeningProcessCreate,
    ScreeningProcessDetailResponse,
)
from src.modules.screening.infrastructure.repositories import (
    OrganizationScreeningSettingsRepository,
    ScreeningProcessRepository,
    ScreeningProcessStepRepository,
    ScreeningRequiredDocumentRepository,
)


class CreateScreeningProcessUseCase:
    """
    Create a new screening process (Step 1 - Conversation/Creation).

    This creates the screening process and professional with minimal data:
    - CPF, name, phone
    - Expected professional type and specialty
    - Assignee and client company (if required)

    The professional is created or linked, and the screening steps
    are generated based on the fixed workflow.
    """

    # Fixed step definitions for the screening workflow
    # Order: Conversa -> Coleta de Dados -> Documentos -> Revisão -> Validação Cliente
    STEP_DEFINITIONS = [
        # 1. Conversa inicial
        {
            "step_type": StepType.CONVERSATION,
            "name": "Conversa Inicial",
            "description": "Coleta de dados básicos por telefone",
            "is_required": True,
        },
        # 2-7. Coleta de dados
        {
            "step_type": StepType.PROFESSIONAL_DATA,
            "name": "Dados Pessoais",
            "description": "Dados pessoais (CPF, endereço, etc.)",
            "is_required": True,
        },
        {
            "step_type": StepType.QUALIFICATION,
            "name": "Registro em Conselho",
            "description": "Formação e registro profissional (CRM, COREN, etc.)",
            "is_required": True,
        },
        {
            "step_type": StepType.SPECIALTY,
            "name": "Especialidades",
            "description": "Especialidades médicas",
            "is_required": False,
        },
        {
            "step_type": StepType.EDUCATION,
            "name": "Formação Complementar",
            "description": "Educação e certificações complementares",
            "is_required": False,
        },
        {
            "step_type": StepType.COMPANY,
            "name": "Empresa PJ",
            "description": "Dados da empresa PJ (se aplicável)",
            "is_required": False,
        },
        {
            "step_type": StepType.BANK_ACCOUNT,
            "name": "Dados Bancários",
            "description": "Dados bancários para pagamento",
            "is_required": True,
        },
        # 8. Upload de documentos
        {
            "step_type": StepType.DOCUMENT_UPLOAD,
            "name": "Upload de Documentos",
            "description": "Upload de documentos obrigatórios",
            "is_required": True,
        },
        # 9. Revisão de documentos
        {
            "step_type": StepType.DOCUMENT_REVIEW,
            "name": "Revisão de Documentos",
            "description": "Verificação de documentos pelo gestor",
            "is_required": True,
        },
        # 10. Validação do cliente (opcional)
        {
            "step_type": StepType.CLIENT_VALIDATION,
            "name": "Validação do Cliente",
            "description": "Validação pela empresa contratante",
            "is_required": False,
        },
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.step_repository = ScreeningProcessStepRepository(session)
        self.settings_repository = OrganizationScreeningSettingsRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.document_repository = ScreeningRequiredDocumentRepository(session)

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

        # Check if professional exists or create new one
        professional = await self._get_or_create_professional(
            organization_id=organization_id,
            cpf=data.professional_cpf,
            name=data.professional_name,
            phone=data.professional_phone,
            family_org_ids=family_org_ids,
            created_by=created_by,
        )

        # Check for existing active screening by CPF
        existing = await self.repository.get_active_by_cpf(
            organization_id=organization_id,
            cpf=data.professional_cpf,
        )
        if existing:
            from src.app.exceptions import ConflictError

            raise ConflictError(
                message="Profissional já possui triagem ativa",
            )

        # Generate access token
        access_token = str(uuid4())
        token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.token_expiry_hours
        )

        # Create the screening process
        # First step is always CONVERSATION
        process = ScreeningProcess(
            organization_id=organization_id,
            professional_id=professional.id,
            professional_cpf=data.professional_cpf,
            professional_name=data.professional_name,
            status=ScreeningStatus.IN_PROGRESS,
            current_step_type=StepType.CONVERSATION,
            expected_professional_type=data.expected_professional_type,
            expected_specialty_id=data.expected_specialty_id,
            owner_id=data.owner_id or created_by,
            current_actor_id=data.owner_id or created_by,
            client_company_id=data.client_company_id,
            access_token=access_token,
            token_expires_at=token_expires_at,
            created_by=created_by,
            updated_by=created_by,
        )
        process = await self.repository.create(process)
        await self.session.flush()  # Ensure process.id is generated

        # Create steps based on fixed workflow
        await self._create_steps(
            process=process,
            settings=settings,
            created_by=created_by,
        )

        await self.session.flush()
        await self.session.refresh(process)

        # Re-fetch with all related data for complete response
        process_with_details = await self.repository.get_by_id_with_details(
            id=process.id,
            organization_id=organization_id,
        )

        return ScreeningProcessDetailResponse.model_validate(process_with_details)

    async def _get_or_create_professional(
        self,
        organization_id: UUID,
        cpf: str,
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
            cpf=cpf,
            family_org_ids=family_org_ids,
        )
        if existing:
            return existing

        # Create new professional with minimal data
        professional = OrganizationProfessional(
            organization_id=organization_id,
            cpf=cpf,
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
        settings,
        created_by: UUID,
    ) -> list[ScreeningProcessStep]:
        """Create process steps from fixed step definitions."""
        steps = []

        for i, step_def in enumerate(self.STEP_DEFINITIONS):
            step_type = step_def["step_type"]

            step = ScreeningProcessStep(
                process_id=process.id,
                step_type=step_type,
                order=len(steps) + 1,
                status=StepStatus.PENDING if len(steps) > 0 else StepStatus.IN_PROGRESS,
                is_required=step_def["is_required"],
            )
            steps.append(step)

        # Create steps individually
        created_steps = []
        for step in steps:
            created_step = await self.step_repository.create(step)
            created_steps.append(created_step)

        return created_steps

    async def _create_required_documents(
        self,
        process: ScreeningProcess,
        document_type_ids: list[UUID],
        created_by: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """Create required document entries."""
        documents = []

        for doc_type_id in document_type_ids:
            doc = ScreeningRequiredDocument(
                screening_process_id=process.id,
                document_type_config_id=doc_type_id,
                is_required=True,
                created_by=created_by,
                updated_by=created_by,
            )
            documents.append(doc)

        for doc in documents:
            await self.document_repository.create(doc)

        return documents
