"""Use cases for ProfessionalEducation."""

from src.modules.professionals.use_cases.professional_education.professional_education_create_use_case import (
    CreateProfessionalEducationUseCase,
)
from src.modules.professionals.use_cases.professional_education.professional_education_delete_use_case import (
    DeleteProfessionalEducationUseCase,
)
from src.modules.professionals.use_cases.professional_education.professional_education_get_use_case import (
    GetProfessionalEducationUseCase,
)
from src.modules.professionals.use_cases.professional_education.professional_education_list_use_case import (
    ListProfessionalEducationsUseCase,
)
from src.modules.professionals.use_cases.professional_education.professional_education_update_use_case import (
    UpdateProfessionalEducationUseCase,
)

__all__ = [
    "CreateProfessionalEducationUseCase",
    "DeleteProfessionalEducationUseCase",
    "GetProfessionalEducationUseCase",
    "ListProfessionalEducationsUseCase",
    "UpdateProfessionalEducationUseCase",
]
