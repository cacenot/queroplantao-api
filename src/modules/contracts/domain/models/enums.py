"""Contracts module enums for PostgreSQL."""

from enum import Enum


class ContractStatus(str, Enum):
    """
    Status of a contract throughout its lifecycle.

    Tracks the contract from creation to termination.
    """

    DRAFT = "DRAFT"  # Rascunho - contrato em elaboração
    PENDING_SIGNATURES = "PENDING_SIGNATURES"  # Aguardando assinaturas
    ACTIVE = "ACTIVE"  # Contrato ativo e em vigor
    SUSPENDED = "SUSPENDED"  # Contrato suspenso temporariamente
    TERMINATED = "TERMINATED"  # Contrato rescindido/encerrado
    EXPIRED = "EXPIRED"  # Contrato expirado (fim da vigência)
