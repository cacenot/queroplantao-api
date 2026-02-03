"""Schemas for screening compliance report."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class QualificationData(BaseModel):
    """Data for professional qualification section."""

    professional_type: str
    professional_type_label: str
    council_type: str
    council_number: str
    council_state: str
    graduation_year: int | None = None


class SpecialtyData(BaseModel):
    """Data for specialty section."""

    name: str
    rqe_number: str | None = None
    rqe_state: str | None = None
    residency_status: str | None = None
    residency_status_label: str | None = None
    residency_institution: str | None = None


class EducationData(BaseModel):
    """Data for education/formation section."""

    level: str
    level_label: str
    course_name: str
    institution: str
    start_year: int | None = None
    end_year: int | None = None
    is_completed: bool = False


class DocumentData(BaseModel):
    """Data for verified document."""

    document_type_name: str
    status: str
    status_label: str
    uploaded_at: datetime | None = None
    uploaded_by_name: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by_name: str | None = None
    download_url: str | None = None


class StepHistoryData(BaseModel):
    """Data for screening step history."""

    step_type: str
    step_label: str
    status: str
    status_label: str
    completed_at: datetime | None = None
    completed_by_name: str | None = None


class ScreeningReportContext(BaseModel):
    """Full context for generating the compliance report PDF."""

    # Header
    screening_id: UUID
    generated_at: datetime
    logo_base64: str
    placeholder_base64: str

    # Personal Data
    professional_photo_base64: str | None = None
    professional_name: str
    professional_cpf: str
    professional_email: str | None = None
    professional_phone: str | None = None
    professional_birth_date: date | None = None
    professional_gender: str | None = None
    professional_gender_label: str | None = None
    professional_nationality: str | None = None
    professional_address: str | None = None
    professional_city: str | None = None
    professional_state: str | None = None
    professional_postal_code: str | None = None

    # Professional Data
    qualification: QualificationData | None = None
    specialty: SpecialtyData | None = None
    educations: list[EducationData] = []

    # Documents
    documents: list[DocumentData] = []

    # History
    created_at: datetime
    owner_name: str | None = None
    steps_history: list[StepHistoryData] = []
    completed_at: datetime | None = None
    completed_by_name: str | None = None


class ScreeningReportResponse(BaseModel):
    """Response for compliance report generation."""

    url: str
    generated_at: datetime
    screening_id: UUID
