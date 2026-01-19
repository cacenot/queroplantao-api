"""
Value objects compartilhados.
"""

from src.shared.domain.value_objects.address import PostalCode
from src.shared.domain.value_objects.contact import Phone
from src.shared.domain.value_objects.coordinate import Coordinate
from src.shared.domain.value_objects.documents import CNPJ, CPF, CPFOrCNPJ

__all__ = [
    "CNPJ",
    "CPF",
    "CPFOrCNPJ",
    "Coordinate",
    "Phone",
    "PostalCode",
]
