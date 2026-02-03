"""Brazilian Portuguese (pt-BR) translations."""

from src.app.i18n.messages import (
    AuthMessages,
    DocumentTypeMessages,
    OrganizationMessages,
    ProfessionalMessages,
    ResourceMessages,
    ScreeningMessages,
    UserMessages,
    ValidationMessages,
)

MESSAGES: dict[str, str] = {
    # ==========================================================================
    # Authentication messages
    # ==========================================================================
    AuthMessages.MISSING_TOKEN: "Token de autorização é obrigatório",
    AuthMessages.INVALID_TOKEN: "Token de autenticação inválido",
    AuthMessages.EXPIRED_TOKEN: "Token de autenticação expirado",
    AuthMessages.REVOKED_TOKEN: "Token de autenticação foi revogado",
    AuthMessages.FIREBASE_ERROR: "Falha na autenticação com Firebase",
    AuthMessages.FIREBASE_INIT_ERROR: "Falha na inicialização do serviço Firebase",
    AuthMessages.FIREBASE_SERVICE_UNAVAILABLE: "Serviço de autenticação indisponível",
    AuthMessages.FIREBASE_INTERNAL_ERROR: "Falha na autenticação devido a erro interno",
    AuthMessages.USER_NOT_FOUND: "Usuário não encontrado",
    AuthMessages.USER_INACTIVE: "Conta de usuário está inativa",
    AuthMessages.CPF_ALREADY_IN_USE: "Este CPF já está em uso por outro usuário",
    AuthMessages.CACHE_ERROR: "Falha na operação de cache",
    AuthMessages.AUTHENTICATION_FAILED: "Falha na autenticação",
    AuthMessages.INSUFFICIENT_PERMISSIONS: "Permissões insuficientes",
    # ==========================================================================
    # Organization messages
    # ==========================================================================
    OrganizationMessages.MISSING_ID: "ID da organização é obrigatório",
    OrganizationMessages.INVALID_ID: "ID da organização deve ser um UUID válido",
    OrganizationMessages.NOT_FOUND: "Organização não encontrada",
    OrganizationMessages.INACTIVE: "Organização está inativa",
    OrganizationMessages.INTERNAL_ERROR: "Falha na identificação da organização devido a erro interno",
    OrganizationMessages.USER_NOT_MEMBER: "Usuário não é membro desta organização",
    OrganizationMessages.MEMBERSHIP_INACTIVE: "Associação nesta organização está inativa",
    OrganizationMessages.MEMBERSHIP_PENDING: "Convite de associação aguardando aceitação",
    OrganizationMessages.MEMBERSHIP_EXPIRED: "Associação expirou",
    OrganizationMessages.INVALID_CHILD_ID: "ID da organização filha deve ser um UUID válido",
    OrganizationMessages.CHILD_NOT_FOUND: "Organização filha não encontrada",
    OrganizationMessages.CHILD_INACTIVE: "Organização filha está inativa",
    OrganizationMessages.CHILD_NOT_ALLOWED: "Esta organização não suporta organizações filhas",
    OrganizationMessages.NOT_CHILD_OF_PARENT: "A organização especificada não é filha da organização pai",
    # ==========================================================================
    # Resource messages
    # ==========================================================================
    ResourceMessages.NOT_FOUND: "{resource} não encontrado(a)",
    ResourceMessages.NOT_FOUND_WITH_ID: "{resource} com id '{identifier}' não encontrado(a)",
    ResourceMessages.CONFLICT: "Conflito de recurso",
    ResourceMessages.VALIDATION_ERROR: "Erro de validação",
    # ==========================================================================
    # Professional messages
    # ==========================================================================
    ProfessionalMessages.CPF_ALREADY_EXISTS: "Já existe um profissional com este CPF na organização",
    ProfessionalMessages.EMAIL_ALREADY_EXISTS: "Já existe um profissional com este e-mail na organização",
    ProfessionalMessages.COUNCIL_REGISTRATION_EXISTS: "Este registro de conselho já existe na organização",
    ProfessionalMessages.COMPANY_ALREADY_LINKED: "Este profissional já está vinculado a esta empresa",
    ProfessionalMessages.BANK_NOT_FOUND: "Banco não encontrado",
    ProfessionalMessages.SPECIALTY_ALREADY_ASSIGNED: "Esta especialidade já está atribuída a esta qualificação",
    ProfessionalMessages.DUPLICATE_SPECIALTY_IDS: "IDs de especialidade duplicados na requisição",
    ProfessionalMessages.INVALID_COUNCIL_TYPE: "Tipo de conselho {council_type} não é válido para o tipo profissional {professional_type}",
    ProfessionalMessages.QUALIFICATION_ID_REQUIRED: (
        "ID da qualificação é obrigatório para atualização. "
        "Para criar uma nova qualificação, use o endpoint específico de criação."
    ),
    ProfessionalMessages.QUALIFICATION_NOT_BELONGS: "Qualificação não pertence a este profissional",
    ProfessionalMessages.SPECIALTY_ID_REQUIRED: "specialty_id é obrigatório ao criar uma nova especialidade",
    ProfessionalMessages.LEVEL_REQUIRED: "level é obrigatório ao criar uma nova formação",
    ProfessionalMessages.COURSE_NAME_REQUIRED: "course_name é obrigatório ao criar uma nova formação",
    ProfessionalMessages.INSTITUTION_REQUIRED: "institution é obrigatório ao criar uma nova formação",
    ProfessionalMessages.DOCUMENT_QUALIFICATION_CATEGORY: "Documentos vinculados a uma qualificação devem ter categoria QUALIFICATION",
    ProfessionalMessages.DOCUMENT_SPECIALTY_CATEGORY: "Documentos vinculados a uma especialidade devem ter categoria SPECIALTY",
    ProfessionalMessages.PROFESSIONAL_NOT_FOUND: "Profissional não encontrado",
    ProfessionalMessages.QUALIFICATION_NOT_FOUND: "Qualificação não encontrada",
    ProfessionalMessages.DOCUMENT_NOT_FOUND: "Documento não encontrado",
    ProfessionalMessages.SPECIALTY_NOT_FOUND: "Especialidade não encontrada",
    ProfessionalMessages.COMPANY_NOT_FOUND: "Empresa não encontrada",
    ProfessionalMessages.EDUCATION_NOT_FOUND: "Formação não encontrada",
    # Version errors
    ProfessionalMessages.VERSION_NOT_FOUND: "Versão do profissional não encontrada",
    ProfessionalMessages.VERSION_ALREADY_APPLIED: "Esta versão já foi aplicada",
    ProfessionalMessages.VERSION_ALREADY_REJECTED: "Esta versão já foi rejeitada",
    ProfessionalMessages.VERSION_NOT_PENDING: "Esta versão não está pendente de aprovação",
    ProfessionalMessages.VERSION_FEATURE_NOT_SUPPORTED: "Funcionalidade do snapshot ainda não suportada: {feature}",
    # ==========================================================================
    # User messages
    # ==========================================================================
    UserMessages.USER_NOT_FOUND: "Usuário não encontrado",
    UserMessages.USER_ALREADY_MEMBER: "Usuário já é membro desta organização",
    UserMessages.USER_NOT_MEMBER: "Usuário não é membro desta organização",
    UserMessages.INVITATION_SENT: "Convite enviado com sucesso",
    UserMessages.INVITATION_ALREADY_SENT: "Já existe um convite pendente para este e-mail",
    UserMessages.INVITATION_NOT_FOUND: "Convite não encontrado",
    UserMessages.INVITATION_EXPIRED: "O convite expirou",
    UserMessages.INVITATION_ALREADY_ACCEPTED: "Este convite já foi aceito",
    UserMessages.INVITATION_INVALID_TOKEN: "Token de convite inválido",
    UserMessages.INVITATION_ACCEPTED: "Convite aceito com sucesso! Bem-vindo(a) à {organization_name}",
    UserMessages.MEMBERSHIP_NOT_FOUND: "Associação não encontrada",
    UserMessages.MEMBERSHIP_UPDATED: "Associação atualizada com sucesso",
    UserMessages.MEMBERSHIP_REMOVED: "Usuário removido da organização",
    UserMessages.CANNOT_REMOVE_OWNER: "Não é possível remover o dono da organização",
    UserMessages.CANNOT_REMOVE_SELF: "Não é possível remover a si mesmo da organização",
    UserMessages.ROLE_NOT_FOUND: "Função não encontrada",
    UserMessages.INVALID_ROLE: "Função inválida para esta operação",
    # ==========================================================================
    # Validation messages
    # ==========================================================================
    ValidationMessages.CPF_MUST_BE_STRING: "CPF deve ser uma string",
    ValidationMessages.CPF_INVALID_LENGTH: "CPF deve ter 11 dígitos, encontrado {length}",
    ValidationMessages.CPF_ALL_SAME_DIGITS: "CPF não pode ter todos os dígitos iguais",
    ValidationMessages.CPF_INVALID_CHECK_DIGIT: "Dígito verificador do CPF inválido",
    ValidationMessages.CNPJ_MUST_BE_STRING: "CNPJ deve ser uma string",
    ValidationMessages.CNPJ_INVALID_LENGTH: "CNPJ deve ter 14 dígitos, encontrado {length}",
    ValidationMessages.CNPJ_ALL_SAME_DIGITS: "CNPJ não pode ter todos os dígitos iguais",
    ValidationMessages.CNPJ_INVALID_CHECK_DIGIT: "Dígito verificador do CNPJ inválido",
    ValidationMessages.CPF_CNPJ_MUST_BE_STRING: "CPF/CNPJ deve ser uma string",
    ValidationMessages.CPF_CNPJ_INVALID: "Documento deve ser um CPF válido (11 dígitos) ou CNPJ válido (14 dígitos)",
    ValidationMessages.PHONE_MUST_BE_STRING: "Número de telefone deve ser uma string",
    ValidationMessages.PHONE_INVALID: "Número de telefone inválido",
    ValidationMessages.PHONE_INVALID_FORMAT: "Formato de número de telefone inválido: {error}",
    ValidationMessages.PHONE_UNABLE_TO_EXTRACT_DDI: "Não foi possível extrair o DDI do número de telefone: {phone}",
    ValidationMessages.PHONE_UNABLE_TO_EXTRACT_DDD: "Não foi possível extrair o DDD do número de telefone: {phone}",
    ValidationMessages.PHONE_UNABLE_TO_FORMAT: "Não foi possível formatar o número de telefone: {phone}",
    ValidationMessages.CEP_MUST_BE_STRING: "CEP deve ser uma string",
    ValidationMessages.CEP_INVALID_LENGTH: "CEP deve ter 8 dígitos, encontrado {length}",
    ValidationMessages.CEP_ALL_ZEROS: "CEP inválido: não pode ser todos zeros",
    ValidationMessages.UF_MUST_BE_STRING: "UF deve ser uma string",
    ValidationMessages.UF_INVALID_LENGTH: "UF deve ter 2 letras, encontrado {length}",
    ValidationMessages.UF_INVALID_CODE: "UF inválida: '{code}' não é um estado brasileiro válido",
    # ==========================================================================
    # Screening messages
    # ==========================================================================
    # Process
    ScreeningMessages.PROCESS_NOT_FOUND: "Processo de triagem não encontrado",
    ScreeningMessages.PROCESS_ACTIVE_EXISTS: "Já existe uma triagem ativa para este profissional",
    ScreeningMessages.PROCESS_INVALID_STATUS: "Processo de triagem não pode ser alterado no status {status}",
    ScreeningMessages.PROCESS_ALREADY_COMPLETED: "Processo de triagem já foi finalizado",
    ScreeningMessages.PROCESS_CANNOT_APPROVE: "Processo de triagem não pode ser aprovado no status {status}",
    ScreeningMessages.PROCESS_CANNOT_REJECT: "Processo de triagem não pode ser rejeitado no status {status}",
    ScreeningMessages.PROCESS_CANNOT_CANCEL: "Processo de triagem não pode ser cancelado no status {status}",
    ScreeningMessages.PROCESS_HAS_REJECTED_DOCUMENTS: "Existem documentos rejeitados pendentes de correção",
    ScreeningMessages.PROCESS_INCOMPLETE_STEPS: "Nem todas as etapas obrigatórias foram concluídas",
    # Step
    ScreeningMessages.STEP_NOT_FOUND: "Etapa de triagem não encontrada",
    ScreeningMessages.STEP_ALREADY_COMPLETED: "Esta etapa já foi concluída",
    ScreeningMessages.STEP_SKIPPED: "Esta etapa foi ignorada e não pode ser alterada",
    ScreeningMessages.STEP_NOT_IN_PROGRESS: "Esta etapa não está em andamento",
    ScreeningMessages.STEP_NOT_PENDING: (
        "Esta etapa deve estar em PENDING ou IN_PROGRESS. Status atual: {status}"
    ),
    ScreeningMessages.STEP_INVALID_TYPE: "Tipo de etapa inválido para esta operação. Esperado: {expected}, recebido: {received}",
    ScreeningMessages.STEP_CANNOT_GO_BACK: "Não é possível voltar para a etapa {step_type}",
    ScreeningMessages.STEP_NOT_ASSIGNED_TO_USER: "Esta etapa não está atribuída ao usuário atual",
    ScreeningMessages.STEP_NOT_CONFIGURED: "Esta etapa precisa ser configurada antes de prosseguir",
    ScreeningMessages.STEP_ALREADY_CONFIGURED: "Esta etapa já foi configurada e não pode ser reconfigurada",
    # Conversation
    ScreeningMessages.CONVERSATION_REJECTED: "Profissional rejeitado na conversa inicial",
    # Professional data
    ScreeningMessages.PROFESSIONAL_NOT_LINKED: "Nenhum profissional vinculado ao processo de triagem",
    ScreeningMessages.PROFESSIONAL_NO_QUALIFICATION: "O profissional não possui qualificação cadastrada",
    ScreeningMessages.PROFESSIONAL_TYPE_MISMATCH: "Tipo de profissional não corresponde ao esperado. Esperado: {expected}, encontrado: {found}",
    ScreeningMessages.SPECIALTY_MISMATCH: "O profissional não possui a especialidade requerida para esta triagem",
    # Documents
    ScreeningMessages.DOCUMENTS_NOT_UPLOADED: "Documentos obrigatórios pendentes de envio: {documents}",
    ScreeningMessages.DOCUMENTS_MISSING_REQUIRED: "Documentos obrigatórios não foram enviados: {missing}",
    ScreeningMessages.DOCUMENTS_PENDING_REVIEW: "Documentos pendentes de verificação: {documents}",
    ScreeningMessages.DOCUMENT_NOT_FOUND: "Documento de triagem não encontrado",
    ScreeningMessages.DOCUMENT_INVALID_STATUS: "Documento não pode ser reutilizado no status {status}",
    ScreeningMessages.DOCUMENT_TYPE_MISMATCH: "Tipo de documento não corresponde ao requisitado. Esperado: {expected}, encontrado: {found}",
    ScreeningMessages.DOCUMENT_REUSE_PENDING: "Documento pendente não pode ser reutilizado. Apenas documentos aprovados podem ser reutilizados.",
    # Alert
    ScreeningMessages.ALERT_NOT_FOUND: "Alerta de triagem não encontrado",
    ScreeningMessages.ALERT_ALREADY_EXISTS: "Já existe um alerta pendente para esta triagem",
    ScreeningMessages.ALERT_ALREADY_RESOLVED: "Este alerta já foi resolvido",
    ScreeningMessages.PROCESS_BLOCKED_BY_ALERT: "Processo de triagem bloqueado por alerta pendente",
    # Report
    ScreeningMessages.NOT_APPROVED: "O relatório de compliance só pode ser gerado para triagens aprovadas",
    ScreeningMessages.REPORT_GENERATION_FAILED: "Falha ao gerar o relatório de compliance: {error}",
    # ==========================================================================
    # Document Type messages
    # ==========================================================================
    DocumentTypeMessages.DOCUMENT_TYPE_NOT_FOUND: "Tipo de documento não encontrado",
    DocumentTypeMessages.DOCUMENT_TYPE_IN_USE: "Tipo de documento não pode ser excluído pois está em uso",
}

# =============================================================================
# Resource name translations (for NotFoundError)
# =============================================================================
RESOURCE_NAMES: dict[str, str] = {
    # Auth module
    "User": "Usuário",
    # Organizations module
    "Organization": "Organização",
    "OrganizationMembership": "Associação à organização",
    # Professionals module
    "OrganizationProfessional": "Profissional",
    "ProfessionalQualification": "Qualificação",
    "ProfessionalSpecialty": "Especialidade do profissional",
    "ProfessionalDocument": "Documento",
    "ProfessionalEducation": "Formação",
    "ProfessionalCompany": "Vínculo com empresa",
    "ProfessionalVersion": "Versão do profissional",
    "Specialty": "Especialidade",
    # Contracts module
    "ProfessionalContract": "Contrato de profissional",
    "ClientContract": "Contrato de cliente",
    # Units module
    "Unit": "Unidade",
    # Screening module
    "ScreeningProcess": "Processo de triagem",
    "ScreeningTemplate": "Modelo de triagem",
    # Shared
    "Company": "Empresa",
    "BankAccount": "Conta bancária",
    "DocumentType": "Tipo de documento",
}
