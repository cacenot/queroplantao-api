"""
Value objects compartilhados.
"""

from src.shared.domain.value_objects.address import PostalCode
from src.shared.domain.value_objects.contact import Phone
from src.shared.domain.value_objects.documents import CNPJ, CPF, CPFOrCNPJ
from src.shared.domain.value_objects.state import BRAZILIAN_STATES, StateUF

__all__ = [
    "BRAZILIAN_STATES",
    "CNPJ",
    "CPF",
    "CPFOrCNPJ",
    "Phone",
    "PostalCode",
    "StateUF",
]
