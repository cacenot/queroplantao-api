"""Domain value objects."""

from app.domain.value_objects.address import PostalCode
from app.domain.value_objects.contact import Phone
from app.domain.value_objects.documents import CNPJ, CPF, CPFOrCNPJ

__all__ = [
    "CPF",
    "CNPJ",
    "CPFOrCNPJ",
    "Phone",
    "PostalCode",
]
