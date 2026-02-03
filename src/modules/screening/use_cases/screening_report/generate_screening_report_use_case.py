"""
Generate screening compliance report use case.

Generates a PDF compliance report for an approved screening process,
uploads it to Firebase Storage, and saves the URL.
"""

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dependencies.settings import get_settings
from src.app.exceptions import (
    ScreeningNotApprovedError,
    ScreeningProcessNotFoundError,
    ScreeningReportGenerationError,
)
from src.app.logging import get_logger
from src.modules.screening.domain.models import ScreeningProcess, ScreeningStatus
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepType,
    STEP_TYPE_METADATA,
)
from src.modules.screening.domain.schemas.screening_report import (
    DocumentData,
    EducationData,
    QualificationData,
    ScreeningReportContext,
    ScreeningReportResponse,
    SpecialtyData,
    StepHistoryData,
)
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository
from src.modules.users.infrastructure.repositories import UserRepository
from src.shared.infrastructure.firebase.storage_service import (
    FirebaseStorageService,
    get_storage_service,
)
from src.shared.infrastructure.pdf import PDFGeneratorService
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)


logger = get_logger(__name__)

# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "templates"


# Label mappings for enums
PROFESSIONAL_TYPE_LABELS: dict[str, str] = {
    "DOCTOR": "Médico",
    "NURSE": "Enfermeiro(a)",
    "NURSING_TECH": "Técnico(a) de Enfermagem",
    "PHARMACIST": "Farmacêutico(a)",
    "DENTIST": "Dentista",
    "PHYSIOTHERAPIST": "Fisioterapeuta",
    "PSYCHOLOGIST": "Psicólogo(a)",
    "NUTRITIONIST": "Nutricionista",
    "BIOMEDIC": "Biomédico(a)",
}

GENDER_LABELS: dict[str, str] = {
    "MALE": "Masculino",
    "FEMALE": "Feminino",
}

EDUCATION_LEVEL_LABELS: dict[str, str] = {
    "TECHNICAL": "Técnico",
    "UNDERGRADUATE": "Graduação",
    "SPECIALIZATION": "Especialização",
    "MASTERS": "Mestrado",
    "DOCTORATE": "Doutorado",
    "POSTDOC": "Pós-doutorado",
    "COURSE": "Curso",
    "FELLOWSHIP": "Fellowship",
}

RESIDENCY_STATUS_LABELS: dict[str, str] = {
    "R1": "R1 (1º ano)",
    "R2": "R2 (2º ano)",
    "R3": "R3 (3º ano)",
    "R4": "R4 (4º ano)",
    "R5": "R5 (5º ano)",
    "R6": "R6 (6º ano)",
    "COMPLETED": "Concluída",
}

STEP_STATUS_LABELS: dict[str, str] = {
    "PENDING": "Pendente",
    "IN_PROGRESS": "Em Andamento",
    "COMPLETED": "Concluído",
    "APPROVED": "Aprovado",
    "REJECTED": "Rejeitado",
    "SKIPPED": "Ignorado",
    "CANCELLED": "Cancelado",
    "CORRECTION_NEEDED": "Correção Necessária",
}

DOCUMENT_STATUS_LABELS: dict[str, str] = {
    "PENDING_UPLOAD": "Pendente Upload",
    "PENDING_REVIEW": "Pendente Revisão",
    "APPROVED": "Aprovado",
    "CORRECTION_NEEDED": "Correção Necessária",
    "SKIPPED": "Ignorado",
    "REUSED": "Reutilizado",
}


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    # Remove non-ASCII characters
    text = text.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text or "profissional"


class GenerateScreeningReportUseCase:
    """Generate a compliance report PDF for an approved screening."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.user_repository = UserRepository(session)
        self.specialty_repository = SpecialtyRepository(session)
        self.pdf_service = PDFGeneratorService(TEMPLATES_DIR)
        self._storage_service: FirebaseStorageService | None = None

    @property
    def storage_service(self) -> FirebaseStorageService:
        """Get storage service, initializing if needed."""
        if self._storage_service is None:
            service = get_storage_service()
            if service is None:
                settings = get_settings()
                self._storage_service = FirebaseStorageService(settings)
            else:
                self._storage_service = service
        return self._storage_service

    async def _get_user_name(self, user_id: UUID | None) -> str | None:
        """Get user's full name by ID."""
        if user_id is None:
            return None
        user = await self.user_repository.get_by_id(user_id)
        return user.full_name if user else None

    def _build_qualification_data(
        self,
        process: ScreeningProcess,
    ) -> QualificationData | None:
        """Build qualification data for the expected professional type."""
        if not process.organization_professional:
            return None

        professional = process.organization_professional
        expected_type = process.expected_professional_type

        # Find the qualification matching the expected professional type
        for qual in professional.qualifications:
            if qual.professional_type.value == expected_type:
                return QualificationData(
                    professional_type=qual.professional_type.value,
                    professional_type_label=PROFESSIONAL_TYPE_LABELS.get(
                        qual.professional_type.value, qual.professional_type.value
                    ),
                    council_type=qual.council_type.value,
                    council_number=qual.council_number,
                    council_state=qual.council_state,
                    graduation_year=qual.graduation_year,
                )

        return None

    async def _build_specialty_data(
        self,
        process: ScreeningProcess,
    ) -> SpecialtyData | None:
        """Build specialty data for the expected specialty."""
        if not process.expected_specialty_id:
            return None

        if not process.organization_professional:
            return None

        professional = process.organization_professional

        # Get the specialty name from reference data
        specialty_ref = await self.specialty_repository.get_by_id(
            process.expected_specialty_id
        )
        if not specialty_ref:
            return None

        # Find the professional's specialty matching the expected one
        for qual in professional.qualifications:
            for spec in qual.specialties:
                if spec.specialty_id == process.expected_specialty_id:
                    return SpecialtyData(
                        name=specialty_ref.name,
                        rqe_number=spec.rqe_number,
                        rqe_state=spec.rqe_state,
                        residency_status=spec.residency_status.value if spec.residency_status else None,
                        residency_status_label=RESIDENCY_STATUS_LABELS.get(
                            spec.residency_status.value, None
                        ) if spec.residency_status else None,
                        residency_institution=spec.residency_institution,
                    )

        # If not found in qualifications, just return the specialty name
        return SpecialtyData(name=specialty_ref.name)

    def _build_educations_data(
        self,
        process: ScreeningProcess,
    ) -> list[EducationData]:
        """Build education data list."""
        if not process.organization_professional:
            return []

        professional = process.organization_professional
        educations = []

        for qual in professional.qualifications:
            for edu in qual.educations:
                educations.append(
                    EducationData(
                        level=edu.level.value,
                        level_label=EDUCATION_LEVEL_LABELS.get(
                            edu.level.value, edu.level.value
                        ),
                        course_name=edu.course_name,
                        institution=edu.institution,
                        start_year=edu.start_year,
                        end_year=edu.end_year,
                        is_completed=edu.is_completed or False,
                    )
                )

        return educations

    async def _build_documents_data(
        self,
        process: ScreeningProcess,
    ) -> list[DocumentData]:
        """Build documents data list."""
        documents = []

        if not process.document_upload_step:
            return documents

        for doc in process.document_upload_step.documents:
            reviewed_by_name = None
            if doc.review_history:
                # Get the last review action
                last_review = doc.review_history[-1]
                if last_review.get("user_id"):
                    reviewed_by_name = await self._get_user_name(
                        UUID(last_review["user_id"])
                    )

            # Get download URL from professional document if uploaded
            download_url = None
            if doc.professional_document_id and doc.professional_document:
                download_url = doc.professional_document.file_url

            documents.append(
                DocumentData(
                    document_type_name=doc.document_type.name if doc.document_type else "Documento",
                    status=doc.status.value,
                    status_label=DOCUMENT_STATUS_LABELS.get(
                        doc.status.value, doc.status.value
                    ),
                    uploaded_at=doc.professional_document.created_at if doc.professional_document else None,
                    uploaded_by_name=await self._get_user_name(doc.created_by) if doc.created_by else None,
                    reviewed_at=doc.updated_at if doc.status in [ScreeningDocumentStatus.APPROVED, ScreeningDocumentStatus.CORRECTION_NEEDED] else None,
                    reviewed_by_name=reviewed_by_name,
                    download_url=download_url,
                )
            )

        return documents

    async def _build_steps_history(
        self,
        process: ScreeningProcess,
    ) -> list[StepHistoryData]:
        """Build step history data list."""
        steps = []

        # Map step types to their step objects
        step_map = {
            StepType.CONVERSATION: process.conversation_step,
            StepType.PROFESSIONAL_DATA: process.professional_data_step,
            StepType.DOCUMENT_UPLOAD: process.document_upload_step,
            StepType.DOCUMENT_REVIEW: process.document_review_step,
            StepType.PAYMENT_INFO: process.payment_info_step,
            StepType.CLIENT_VALIDATION: process.client_validation_step,
        }

        for step_type in StepType:
            step = step_map.get(step_type)
            if step is None:
                continue

            metadata = STEP_TYPE_METADATA.get(step_type, {})
            steps.append(
                StepHistoryData(
                    step_type=step_type.value,
                    step_label=metadata.get("title", step_type.value),
                    status=step.status.value,
                    status_label=STEP_STATUS_LABELS.get(
                        step.status.value, step.status.value
                    ),
                    completed_at=step.completed_at,
                    completed_by_name=await self._get_user_name(step.completed_by),
                )
            )

        return steps

    async def _build_report_context(
        self,
        process: ScreeningProcess,
    ) -> ScreeningReportContext:
        """Build the full report context from screening data."""
        professional = process.organization_professional

        # Build address string
        address_parts = []
        if professional:
            if professional.street:
                addr = professional.street
                if professional.number:
                    addr += f", {professional.number}"
                if professional.complement:
                    addr += f" - {professional.complement}"
                address_parts.append(addr)
            if professional.neighborhood:
                address_parts.append(professional.neighborhood)

        address = ", ".join(address_parts) if address_parts else None

        return ScreeningReportContext(
            # Header
            screening_id=process.id,
            generated_at=datetime.now(timezone.utc),
            logo_base64=self.pdf_service.get_logo_base64(),
            placeholder_base64=self.pdf_service.get_placeholder_base64(),
            # Personal Data
            professional_photo_base64=None,  # TODO: Fetch from storage if available
            professional_name=professional.full_name if professional else process.professional_name or "Não informado",
            professional_cpf=professional.cpf if professional else process.professional_cpf or "",
            professional_email=professional.email if professional else process.professional_email,
            professional_phone=professional.phone if professional else process.professional_phone,
            professional_birth_date=professional.birth_date if professional else None,
            professional_gender=professional.gender.value if professional and professional.gender else None,
            professional_gender_label=GENDER_LABELS.get(
                professional.gender.value, None
            ) if professional and professional.gender else None,
            professional_nationality=professional.nationality if professional else None,
            professional_address=address,
            professional_city=professional.city if professional else None,
            professional_state=professional.state if professional else None,
            professional_postal_code=professional.postal_code if professional else None,
            # Professional Data
            qualification=self._build_qualification_data(process),
            specialty=await self._build_specialty_data(process),
            educations=self._build_educations_data(process),
            # Documents
            documents=await self._build_documents_data(process),
            # History
            created_at=process.created_at,
            owner_name=await self._get_user_name(process.owner_id),
            steps_history=await self._build_steps_history(process),
            completed_at=process.completed_at,
            completed_by_name=await self._get_user_name(process.updated_by),
        )

    async def _upload_report(
        self,
        pdf_bytes: bytes,
        process: ScreeningProcess,
    ) -> str:
        """Upload PDF to Firebase Storage and return URL."""
        professional_name = "profissional"
        if process.organization_professional:
            professional_name = slugify(process.organization_professional.full_name)
        elif process.professional_name:
            professional_name = slugify(process.professional_name)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        file_name = f"relatorio-compliance-{professional_name}-{timestamp}.pdf"

        # Upload path
        path = f"organizations/{process.organization_id}/screenings/{process.id}/reports/{file_name}"

        # Upload to storage
        bucket = self.storage_service._get_bucket()
        blob = bucket.blob(path)

        blob.upload_from_string(
            pdf_bytes,
            content_type="application/pdf",
        )

        # Generate signed URL (1 year validity)
        from datetime import timedelta

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=365),
            method="GET",
        )

        logger.info(
            "compliance_report_uploaded",
            screening_id=str(process.id),
            path=path,
            size_bytes=len(pdf_bytes),
        )

        return url

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
        *,
        force: bool = False,
    ) -> ScreeningReportResponse:
        """
        Generate compliance report for an approved screening.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            family_org_ids: Organization family IDs for scope validation.
            force: If True, regenerate even if URL already exists.

        Returns:
            ScreeningReportResponse with the report URL.

        Raises:
            ScreeningProcessNotFoundError: If screening not found.
            ScreeningNotApprovedError: If screening is not approved.
            ScreeningReportGenerationError: If PDF generation fails.
        """
        # Get screening with all related data
        process = await self.repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate status
        if process.status != ScreeningStatus.APPROVED:
            raise ScreeningNotApprovedError(
                screening_id=str(screening_id),
                current_status=process.status.value,
            )

        # Return existing URL if not forcing regeneration
        if process.compliance_report_url and not force:
            logger.info(
                "compliance_report_cached",
                screening_id=str(screening_id),
            )
            return ScreeningReportResponse(
                url=process.compliance_report_url,
                generated_at=process.updated_at or process.created_at,
                screening_id=screening_id,
            )

        try:
            # Build report context
            context = await self._build_report_context(process)

            # Generate PDF
            pdf_bytes = await self.pdf_service.generate_pdf(
                template_name="screening_report.html",
                context=context.model_dump(),
            )

            # Upload to storage
            report_url = await self._upload_report(pdf_bytes, process)

            # Save URL to database
            process.compliance_report_url = report_url
            await self.repository.update(process)

            logger.info(
                "compliance_report_generated",
                screening_id=str(screening_id),
                url=report_url,
            )

            return ScreeningReportResponse(
                url=report_url,
                generated_at=datetime.now(timezone.utc),
                screening_id=screening_id,
            )

        except Exception as e:
            logger.error(
                "compliance_report_generation_failed",
                screening_id=str(screening_id),
                error=str(e),
            )
            raise ScreeningReportGenerationError(error=str(e)) from e
