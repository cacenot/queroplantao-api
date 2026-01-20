# Módulo de Triagem (Screening)

## Visão Geral

O módulo de triagem gerencia o processo de coleta e validação de dados e documentos de profissionais de saúde. Permite criar templates configuráveis que definem quais etapas são necessárias para diferentes cenários (onboarding completo, verificação para contrato específico, etc.).

### Principais Funcionalidades

- **Templates configuráveis**: Cada organização pode ter múltiplos templates com diferentes etapas
- **Fluxo de conversa inicial**: Etapa de pré-triagem por telefone antes da coleta de dados
- **Verificação individual de documentos**: Cada documento é revisado separadamente
- **Escalação para supervisor**: Alertas podem ser escalados para revisão superior
- **Acesso por token**: Profissionais podem preencher via link seguro sem autenticação completa
- **Vinculação com contratos**: Triagem pode ser associada a contratos específicos

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                      TRIAGEM (SCREENING)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────┐      ┌─────────────────────┐                                      │
│  │   Organization   │──1:N─│  ScreeningTemplate  │                                      │
│  └──────────────────┘      └─────────────────────┘                                      │
│          │                          │                                                   │
│         1:N                        1:N                                                  │
│          │                          │                                                   │
│          │                 ┌────────────────────────┐                                   │
│          │                 │ ScreeningTemplateStep  │                                   │
│          │                 └────────────────────────┘                                   │
│          │                                                                              │
│          │                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐              │
│  │                        PROCESSO DE TRIAGEM                            │              │
│  │                                                                       │              │
│  │  ┌──────────────────┐      ┌───────────────────┐                      │              │
│  │  │   Organization   │──1:N─│  ScreeningProcess │                      │              │
│  │  └──────────────────┘      └───────────────────┘                      │              │
│  │                                    │                                  │              │
│  │           ┌────────────────────────┼────────────────────────┐         │              │
│  │          1:N                      1:N                      1:N        │              │
│  │           │                        │                        │         │              │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐ │              │
│  │  │ScreeningProcessStep│  │ScreeningRequired   │  │ScreeningDocument │ │              │
│  │  │                    │  │     Document       │  │     Review       │ │              │
│  │  └────────────────────┘  └────────────────────┘  └──────────────────┘ │              │
│  │           │                                              │            │              │
│  │          1:N                                            N:1           │              │
│  │           │                                              │            │              │
│  │           └──────────────────────┬───────────────────────┘            │              │
│  │                                  │                                    │              │
│  │                         ┌────────────────────┐                        │              │
│  │                         │ProfessionalDocument│                        │              │
│  │                         └────────────────────┘                        │              │
│  └───────────────────────────────────────────────────────────────────────┘              │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐              │
│  │                      VINCULAÇÕES OPCIONAIS                            │              │
│  │                                                                       │              │
│  │  ScreeningProcess ──N:1── OrganizationProfessional                    │              │
│  │  ScreeningProcess ──N:1── ProfessionalContract (opcional)             │              │
│  │  ScreeningProcess ──N:1── ClientContract (opcional)                   │              │
│  │  ScreeningProcess ──N:1── ScreeningTemplate                           │              │
│  └───────────────────────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Fluxo Principal

```
┌─────────┐
│  DRAFT  │ ─── Triagem criada, não iniciada
└────┬────┘
     │
     ▼ (iniciar conversa)
┌──────────────┐
│ CONVERSATION │ ─── Escalista conversa por telefone, registra notas
└──────┬───────┘
       │
       ├──(rejeitado)──► REJECTED
       │
       ▼ (aprovado na conversa)
┌─────────────┐
│ IN_PROGRESS │ ─── Coletando dados pessoais, formação, documentos
└──────┬──────┘
       │
       ▼ (dados preenchidos)
┌────────────────┐
│ PENDING_REVIEW │ ─── Aguardando verificação de documentos
└───────┬────────┘
        │
        ▼ (iniciar verificação)
┌──────────────┐
│ UNDER_REVIEW │ ─── Gestor verificando cada documento
└──────┬───────┘
       │
       ├──(docs reprovados)──► PENDING_CORRECTION ──► IN_PROGRESS
       │
       ├──(alerta)──► ESCALATED ──┬──(supervisor reprova)──► REJECTED
       │                          │
       │                          └──(supervisor aprova)──► APPROVED
       │
       └──(todos aprovados)──► APPROVED
```

## Enums

### StepType
Tipos fixos de etapas disponíveis para configuração.

| Valor | Descrição |
|-------|-----------|
| **Conversa** | |
| CONVERSATION | Conversa inicial/pré-triagem |
| **Coleta de Dados** | |
| PROFESSIONAL_DATA | Dados pessoais (CPF, endereço, etc.) |
| QUALIFICATION | Formação/registro em conselho |
| SPECIALTY | Especialidades médicas |
| EDUCATION | Educação complementar |
| DOCUMENTS | Upload de documentos |
| COMPANY | Dados da empresa PJ |
| BANK_ACCOUNT | Dados bancários |
| **Verificação** | |
| DOCUMENT_REVIEW | Verificação de documentos pelo gestor |
| SUPERVISOR_REVIEW | Revisão superior (para alertas) |

### ScreeningStatus
Status do processo de triagem.

| Valor | Descrição |
|-------|-----------|
| DRAFT | Criado, não iniciado |
| CONVERSATION | Em conversa inicial |
| IN_PROGRESS | Coletando dados |
| PENDING_REVIEW | Aguardando verificação de documentos |
| UNDER_REVIEW | Em verificação |
| PENDING_CORRECTION | Aguardando correção de dados/documentos |
| ESCALATED | Escalado para supervisor |
| APPROVED | Aprovado e finalizado |
| REJECTED | Rejeitado |
| EXPIRED | Expirado antes de conclusão |
| CANCELLED | Cancelado pela organização |

### StepStatus
Status de uma etapa individual.

| Valor | Descrição |
|-------|-----------|
| PENDING | Não iniciada |
| IN_PROGRESS | Em andamento |
| COMPLETED | Concluída, aguardando revisão |
| APPROVED | Aprovada |
| REJECTED | Rejeitada |
| SKIPPED | Pulada (para etapas opcionais) |
| CORRECTION_NEEDED | Precisa de correção |

### DocumentReviewStatus
Status da verificação de um documento individual.

| Valor | Descrição |
|-------|-----------|
| PENDING | Aguardando verificação |
| APPROVED | Documento aprovado |
| REJECTED | Documento rejeitado, precisa re-upload |
| ALERT | Alerta, requer atenção do supervisor |

### ConversationOutcome
Resultado da conversa inicial.

| Valor | Descrição |
|-------|-----------|
| PROCEED | Continuar para próximas etapas |
| REJECT | Rejeitar e encerrar triagem |

## Tabelas

### screening_templates

Templates configuráveis para processos de triagem.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (tenant isolation) |
| name | VARCHAR(255) | ❌ | Nome do template |
| description | VARCHAR(2000) | ✅ | Descrição do propósito |
| professional_type | ProfessionalType | ✅ | Tipo de profissional (filtro opcional) |
| is_default | BOOLEAN | ❌ | Se é o template padrão da org (único) |
| is_active | BOOLEAN | ❌ | Se está habilitado para uso |
| default_expiration_days | INTEGER | ❌ | Dias até expirar (1-365, default: 30) |
| metadata | JSON | ✅ | Configurações extras |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | Quem criou |
| updated_by | UUID | ✅ | Quem atualizou |
| **Timestamps & Soft Delete** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(organization_id, name) WHERE deleted_at IS NULL`
- UNIQUE PARTIAL INDEX: `(organization_id) WHERE is_default = true AND deleted_at IS NULL`

### screening_template_steps

Configuração de etapas dentro de um template.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| template_id | UUID | ❌ | FK para screening_templates |
| step_type | StepType | ❌ | Tipo da etapa |
| order | INTEGER | ❌ | Ordem de exibição (1-based) |
| is_required | BOOLEAN | ❌ | Se é obrigatória |
| is_enabled | BOOLEAN | ❌ | Se está habilitada |
| instructions | VARCHAR(2000) | ✅ | Instruções personalizadas |
| depends_on | JSON | ✅ | Lista de StepType dependentes |
| metadata | JSON | ✅ | Configurações extras |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(template_id, step_type)
- UNIQUE(template_id, order)

### screening_processes

Instância de um processo de triagem para um profissional.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (tenant isolation) |
| template_id | UUID | ❌ | FK para screening_templates |
| organization_professional_id | UUID | ✅ | FK para organization_professionals |
| professional_contract_id | UUID | ✅ | FK para professional_contracts |
| client_contract_id | UUID | ✅ | FK para client_contracts |
| **Identificação do Profissional** | | | |
| professional_cpf | VARCHAR(11) | ✅ | CPF do profissional |
| professional_email | VARCHAR(255) | ✅ | Email para envio do link |
| professional_name | VARCHAR(255) | ✅ | Nome (antes de criar registro) |
| professional_phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| **Status e Controle** | | | |
| status | ScreeningStatus | ❌ | Status atual (default: DRAFT) |
| current_step_type | StepType | ✅ | Etapa atual |
| **Acesso por Token** | | | |
| access_token | VARCHAR(64) | ✅ | Token hasheado (SHA-256) |
| access_token_expires_at | TIMESTAMP | ✅ | Expiração do token |
| expires_at | TIMESTAMP | ✅ | Expiração do processo |
| **Atribuição** | | | |
| assigned_to | UUID | ✅ | Usuário responsável atual |
| escalated_to | UUID | ✅ | Supervisor (quando escalado) |
| escalation_reason | VARCHAR(2000) | ✅ | Motivo da escalação |
| **Rejeição** | | | |
| rejection_reason | VARCHAR(2000) | ✅ | Motivo da rejeição |
| **Notas** | | | |
| notes | VARCHAR(2000) | ✅ | Notas gerais |
| review_notes | VARCHAR(2000) | ✅ | Notas da revisão |
| **Timestamps de Workflow** | | | |
| sent_at | TIMESTAMP | ✅ | Quando link foi enviado |
| started_at | TIMESTAMP | ✅ | Quando foi acessado |
| submitted_at | TIMESTAMP | ✅ | Quando etapas foram concluídas |
| reviewed_at | TIMESTAMP | ✅ | Quando foi revisado |
| reviewed_by | UUID | ✅ | Quem revisou |
| completed_at | TIMESTAMP | ✅ | Quando foi finalizado |
| **Mixins** | | | |
| metadata | JSON | ✅ | Dados extras |
| version | INTEGER | ❌ | Optimistic locking |
| created_by | UUID | ✅ | Quem criou |
| updated_by | UUID | ✅ | Quem atualizou |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(access_token) WHERE access_token IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(organization_id, professional_cpf) WHERE status NOT IN ('APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED') AND deleted_at IS NULL AND professional_cpf IS NOT NULL`

### screening_process_steps

Progresso de cada etapa dentro de um processo.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| process_id | UUID | ❌ | FK para screening_processes |
| step_type | StepType | ❌ | Tipo da etapa |
| order | INTEGER | ❌ | Ordem (do template) |
| is_required | BOOLEAN | ❌ | Se é obrigatória |
| status | StepStatus | ❌ | Status atual (default: PENDING) |
| assigned_to | UUID | ✅ | Responsável pela etapa |
| **Referências de Dados** | | | |
| data_references | JSON | ✅ | IDs das entidades criadas/atualizadas |
| **Campos de Conversa** | | | |
| conversation_notes | VARCHAR(4000) | ✅ | Notas da conversa (CONVERSATION) |
| conversation_outcome | ConversationOutcome | ✅ | Resultado: PROCEED/REJECT |
| **Campos de Revisão** | | | |
| review_notes | VARCHAR(2000) | ✅ | Notas da revisão |
| rejection_reason | VARCHAR(2000) | ✅ | Motivo da rejeição |
| **Timestamps de Workflow** | | | |
| started_at | TIMESTAMP | ✅ | Quando iniciou |
| submitted_at | TIMESTAMP | ✅ | Quando submeteu |
| submitted_by | UUID | ✅ | Quem submeteu |
| reviewed_at | TIMESTAMP | ✅ | Quando revisou |
| reviewed_by | UUID | ✅ | Quem revisou |
| **Mixins** | | | |
| metadata | JSON | ✅ | Dados extras |
| version | INTEGER | ❌ | Optimistic locking |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(process_id, step_type)

**Estrutura de data_references:**
```json
// PROFESSIONAL_DATA
{"professional_id": "uuid"}

// QUALIFICATION
{"qualification_id": "uuid"}

// SPECIALTY
{"specialty_ids": ["uuid1", "uuid2"]}

// EDUCATION
{"education_ids": ["uuid1", "uuid2"]}

// DOCUMENTS
{"document_ids": ["uuid1", "uuid2"]}

// COMPANY
{"company_id": "uuid", "professional_company_id": "uuid"}

// BANK_ACCOUNT
{"bank_account_id": "uuid"}
```

### screening_required_documents

Documentos obrigatórios configurados para um processo específico.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| process_id | UUID | ❌ | FK para screening_processes |
| document_type | DocumentType | ❌ | Tipo do documento |
| document_category | DocumentCategory | ❌ | PROFILE/QUALIFICATION/SPECIALTY |
| is_required | BOOLEAN | ❌ | Se é obrigatório |
| description | VARCHAR(500) | ✅ | Descrição/instruções específicas |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(process_id, document_type)

### screening_document_reviews

Verificação individual de cada documento uploadado.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| process_id | UUID | ❌ | FK para screening_processes |
| process_step_id | UUID | ✅ | FK para screening_process_steps (DOCUMENT_REVIEW) |
| professional_document_id | UUID | ❌ | FK para professional_documents |
| required_document_id | UUID | ✅ | FK para screening_required_documents |
| status | DocumentReviewStatus | ❌ | Status (default: PENDING) |
| review_notes | VARCHAR(2000) | ✅ | Notas/feedback do revisor |
| rejection_reason | VARCHAR(1000) | ✅ | Motivo da rejeição |
| alert_reason | VARCHAR(1000) | ✅ | Motivo do alerta |
| reviewed_at | TIMESTAMP | ✅ | Quando foi revisado |
| reviewed_by | UUID | ✅ | Quem revisou |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(process_id, professional_document_id)

## Regras de Negócio

### Templates

1. Cada organização pode ter múltiplos templates
2. Apenas **um template** pode ser marcado como `is_default` por organização
3. Templates definem quais etapas são necessárias e em qual ordem
4. Etapas podem ter dependências (ex: SPECIALTY depende de QUALIFICATION)

### Criação de Profissional

1. Quando uma triagem inicia e o profissional **não existe** na organização:
   - Sistema cria automaticamente um registro com dados mínimos (CPF)
   - `is_active = false` até a triagem ser aprovada
2. Se o profissional **já existe**, a triagem é vinculada ao registro existente
3. Busca é feita por `(organization_id, cpf)`

### Acesso por Token

1. Token é gerado quando a triagem é enviada ao profissional
2. Token é armazenado como hash SHA-256
3. Token permite acesso sem autenticação completa
4. Token expira após período configurado no template
5. Profissional pode preencher etapas via link com token

### Fluxo de Verificação de Documentos

1. **Durante DOCUMENTS step**: Profissional/escalista faz upload dos documentos
2. **Durante DOCUMENT_REVIEW step**: Gestor verifica cada documento individualmente
3. **Cada documento pode ter status:**
   - `APPROVED`: Documento válido
   - `REJECTED`: Documento inválido, precisa re-upload → processo volta para `PENDING_CORRECTION`
   - `ALERT`: Documento com pendência, requer supervisor → processo vai para `ESCALATED`
4. **Triagem só é aprovada quando todos os documentos obrigatórios estão APPROVED**

### Escalação para Supervisor

1. Quando um documento tem status `ALERT`, a triagem vai para status `ESCALATED`
2. Campo `escalated_to` recebe o UUID do supervisor
3. Campo `escalation_reason` registra o motivo
4. Supervisor pode aprovar ou rejeitar, finalizando o fluxo

### Documentos Obrigatórios

1. Ao criar uma triagem, o escalista define quais documentos são obrigatórios
2. Lista é armazenada em `screening_required_documents`
3. Permite customização por processo, não apenas por template

### Dependências entre Etapas

Configurável via campo `depends_on` no template step. Sugestão padrão:

| Etapa | Depende de |
|-------|------------|
| PROFESSIONAL_DATA | - |
| QUALIFICATION | PROFESSIONAL_DATA |
| SPECIALTY | QUALIFICATION |
| EDUCATION | QUALIFICATION |
| DOCUMENTS | PROFESSIONAL_DATA |
| COMPANY | PROFESSIONAL_DATA |
| BANK_ACCOUNT | PROFESSIONAL_DATA |
| DOCUMENT_REVIEW | DOCUMENTS |
| SUPERVISOR_REVIEW | DOCUMENT_REVIEW |

## Arquivos de Implementação

```
src/modules/screening/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── enums.py                        # StepType, ScreeningStatus, etc.
│       ├── screening_template.py           # Template configurável
│       ├── screening_template_step.py      # Configuração de etapas
│       ├── screening_process.py            # Processo de triagem
│       ├── screening_process_step.py       # Progresso de etapas
│       ├── screening_required_document.py  # Documentos obrigatórios
│       └── screening_document_review.py    # Verificação de documentos
├── infrastructure/
│   └── repositories/
│       └── __init__.py                     # TODO: Repositories
├── presentation/
│   └── routes.py                           # TODO: Endpoints
└── use_cases/
    └── __init__.py                         # TODO: Use cases
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | ScreeningTemplate, ScreeningProcess |
| TrackingMixin | created_by, updated_by | ScreeningTemplate, ScreeningProcess |
| MetadataMixin | metadata | ScreeningTemplate, ScreeningTemplateStep, ScreeningProcess, ScreeningProcessStep |
| VersionMixin | version | ScreeningProcess, ScreeningProcessStep |

## Relacionamentos com Outros Módulos

### Organizations
- `Organization.screening_templates` → lista de templates
- `Organization.screening_processes` → lista de processos

### Professionals
- `OrganizationProfessional.screening_processes` → processos vinculados
- `ProfessionalDocument.screening_reviews` → revisões do documento

### Contracts
- `ProfessionalContract.screening_processes` → processos vinculados
- `ClientContract.screening_processes` → processos vinculados
