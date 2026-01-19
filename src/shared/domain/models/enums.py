"""Shared enums for multiple modules."""

from enum import Enum


class AccountType(str, Enum):
    """
    Bank account types.

    Defines the type of bank account for payment purposes.
    """

    CHECKING = "CHECKING"  # Conta Corrente
    SAVINGS = "SAVINGS"  # Conta Poupança


class PixKeyType(str, Enum):
    """
    PIX key types.

    Defines the type of PIX key for instant payments.
    """

    CPF = "CPF"  # CPF do titular
    CNPJ = "CNPJ"  # CNPJ da empresa
    EMAIL = "EMAIL"  # E-mail
    PHONE = "PHONE"  # Telefone celular
    RANDOM = "RANDOM"  # Chave aleatória (EVP)
