# Módulo de Triagem (Screening)

## Visão Geral

O módulo de triagem gerencia o processo de coleta e validação de dados e documentos de profissionais de saúde. Implementa um fluxo de 10 etapas configuráveis.

### Principais Funcionalidades

- **Fluxo de 10 etapas**: Conversa → Dados Pessoais → Formação → Especialidade → Educação → Empresa → Conta Bancária → Documentos → Revisão → Validação do Cliente
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
│  └───────────────────────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Fluxo Principal

```
┌─────────┐
│  DRAFT  │ ─── Triagem criada, não iniciada
└────┬────┘
     │
     ▼ (iniciar)
┌─────────────┐
│ IN_PROGRESS │ ─── Processo em andamento (etapa atual indicada por current_step_type)
└──────┬──────┘
       │
       │  Etapas controladas por current_step_type + StepStatus:
       │  - CONVERSATION: Conversa inicial
       │  - PROFESSIONAL_DATA → BANK_ACCOUNT: Coleta de dados
       │  - DOCUMENT_REVIEW: Verificação de documentos
       │  - SUPERVISOR_REVIEW: Revisão superior (alertas)
       │  - CLIENT_VALIDATION: Validação pelo cliente
       │
       ├──(rejeitado em qualquer etapa)──► REJECTED
       │
       ├──(expirado)──► EXPIRED
       │
       ├──(cancelado)──► CANCELLED
       │
       └──(todas etapas aprovadas)──► APPROVED
```

**Nota:** O status detalhado do processo é determinado pela combinação de `status` + `current_step_type` + status da etapa atual.

## Enums

### StepType
Tipos fixos de etapas disponíveis no workflow de triagem.

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
| **Etapas Opcionais** | |
| CLIENT_VALIDATION | Validação pelo cliente (opcional, controlado por `is_required` no step) |

### ScreeningStatus
Status macro do processo de triagem. O estado detalhado é determinado por `current_step_type` + `StepStatus`.

| Valor | Descrição |
|-------|-----------|
| DRAFT | Criado, não iniciado |
| IN_PROGRESS | Em andamento (qualquer etapa) |
| APPROVED | Aprovado e finalizado |
| REJECTED | Rejeitado |
| EXPIRED | Expirado antes de conclusão |
| CANCELLED | Cancelado pela organização |

**Estados detalhados (derivados):**
| Cenário | Como identificar |
|---------|------------------|
| Em conversa inicial | `status=IN_PROGRESS` + `current_step_type=CONVERSATION` |
| Aguardando revisão | `status=IN_PROGRESS` + `current_step_type=DOCUMENT_REVIEW` + step `PENDING` |
| Em revisão | `status=IN_PROGRESS` + `current_step_type=DOCUMENT_REVIEW` + step `IN_PROGRESS` |
| Aguardando correção | `status=IN_PROGRESS` + step com `CORRECTION_NEEDED` |
| Escalado | `status=IN_PROGRESS` + `current_step_type=SUPERVISOR_REVIEW` |

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

### ClientValidationOutcome
Resultado da validação pelo cliente.

| Valor | Descrição |
|-------|-----------|
| APPROVED | Cliente aprovou o profissional |
| REJECTED | Cliente rejeitou o profissional |

## Tabelas

### screening_processes

Instância de um processo de triagem para um profissional.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (tenant isolation) |
| organization_professional_id | UUID | ✅ | FK para organization_professionals |
| professional_contract_id | UUID | ✅ | FK para professional_contracts |
| client_contract_id | UUID | ✅ | FK para client_contracts |
| client_company_id | UUID | ✅ | FK para companies (empresa contratante) |
| **Identificação do Profissional** | | | |
| professional_cpf | VARCHAR(11) | ✅ | CPF do profissional |
| professional_email | VARCHAR(255) | ✅ | Email para envio do link |
| professional_name | VARCHAR(255) | ✅ | Nome (antes de criar registro) |
| professional_phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| **Perfil Esperado** | | | |
| expected_professional_type | VARCHAR(50) | ✅ | Tipo esperado (DOCTOR, NURSE, etc.) |
| expected_specialty_id | UUID | ✅ | Especialidade esperada (para médicos) |
| **Status e Controle** | | | |
| status | ScreeningStatus | ❌ | Status atual (default: DRAFT) |
| current_step_type | StepType | ✅ | Etapa atual |
| **Acesso por Token** | | | |
| access_token | VARCHAR(64) | ✅ | Token para acesso do profissional |
| access_token_expires_at | TIMESTAMP | ✅ | Expiração do token |
| token_expires_at | TIMESTAMP | ✅ | Alias para expiração do token |
| expires_at | TIMESTAMP | ✅ | Expiração do processo |
| **Atribuição** | | | |
| owner_id | UUID | ✅ | Responsável geral pelo processo |
| current_actor_id | UUID | ✅ | Responsável pela ação atual (para filtros "minhas pendências") |
| **Rejeição** | | | |
| rejection_reason | VARCHAR(2000) | ✅ | Motivo da rejeição |
| **Notas** | | | |
| notes | VARCHAR(2000) | ✅ | Notas gerais |
| **Timestamps de Workflow** | | | |
| completed_at | TIMESTAMP | ✅ | Quando foi finalizado (aprovado/rejeitado/cancelado) |
| **Mixins** | | | |
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
| order | INTEGER | ❌ | Ordem da etapa no fluxo |
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
| **Campos de Validação do Cliente** | | | |
| client_validation_outcome | ClientValidationOutcome | ✅ | Decisão: APPROVED/REJECTED |
| client_validation_notes | VARCHAR(2000) | ✅ | Notas da validação pelo cliente |
| client_validated_by | VARCHAR(255) | ✅ | Nome de quem validou na empresa cliente |
| client_validated_at | TIMESTAMP | ✅ | Quando foi validado pelo cliente |
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

### Fluxo Fixo de Etapas

1. O sistema utiliza um fluxo fixo de 10 etapas (definido em `STEP_DEFINITIONS`)
2. Etapas opcionais podem ser puladas (SPECIALTY, EDUCATION, COMPANY, CLIENT_VALIDATION)
3. Etapas têm dependências: ex: SPECIALTY depende de QUALIFICATION
4. Configurações por organização são armazenadas em `OrganizationScreeningSettings`

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
4. Token expira após período configurado em `OrganizationScreeningSettings.token_expiry_hours`
5. Profissional pode preencher etapas via link com token

### Fluxo de Verificação de Documentos

1. **Durante DOCUMENTS step**: Profissional/escalista faz upload dos documentos
2. **Durante DOCUMENT_REVIEW step**: Gestor verifica cada documento individualmente
3. **Cada documento pode ter status:**
   - `APPROVED`: Documento válido
   - `REJECTED`: Documento inválido, precisa re-upload → step volta para `CORRECTION_NEEDED`
   - `ALERT`: Documento com pendência, requer revisão superior
4. **Triagem só é aprovada quando todos os documentos obrigatórios estão APPROVED**

### Revisão Superior

1. Quando um documento tem status `ALERT`, a triagem vai para step `SUPERVISOR_REVIEW`
2. O `current_step_type` passa a ser `SUPERVISOR_REVIEW`
3. Supervisor pode aprovar ou rejeitar, finalizando o fluxo

### Documentos Obrigatórios

1. Ao criar uma triagem, o escalista define quais documentos são obrigatórios
2. Lista é armazenada em `screening_required_documents`
3. Permite customização por processo

### Dependências entre Etapas

As etapas seguem uma ordem fixa definida em `STEP_DEFINITIONS`. Sugestão de dependências lógicas:

| Etapa | Depende de |
|-------|------------|
| CONVERSATION | - |
| PROFESSIONAL_DATA | CONVERSATION |
| QUALIFICATION | PROFESSIONAL_DATA |
| SPECIALTY | QUALIFICATION |
| EDUCATION | QUALIFICATION |
| COMPANY | PROFESSIONAL_DATA |
| BANK_ACCOUNT | PROFESSIONAL_DATA |
| DOCUMENTS | PROFESSIONAL_DATA |
| DOCUMENT_REVIEW | DOCUMENTS |
| CLIENT_VALIDATION | DOCUMENT_REVIEW |

## Arquivos de Implementação

```
src/modules/screening/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py                        # StepType, ScreeningStatus, etc.
│   │   ├── document_type.py                # Configuração de tipos de documento
│   │   ├── organization_screening_settings.py  # Configurações por organização
│   │   ├── screening_process.py            # Processo de triagem
│   │   ├── screening_process_step.py       # Progresso de etapas
│   │   ├── screening_required_document.py  # Documentos obrigatórios
│   │   └── screening_document_review.py    # Verificação de documentos
│   └── schemas/
│       ├── __init__.py
│       ├── document_type.py
│       ├── organization_screening_settings.py
│       ├── screening_document_review.py
│       ├── screening_process.py
│       ├── screening_process_step.py
│       └── screening_required_document.py
├── infrastructure/
│   ├── __init__.py
│   ├── filters.py                          # FilterSet/SortingSet
│   └── repositories/
│       ├── __init__.py
│       ├── screening_process_repository.py
│       ├── screening_process_step_repository.py
│       ├── screening_document_review_repository.py
│       ├── screening_required_document_repository.py
│       └── organization_screening_settings_repository.py
├── presentation/
│   ├── __init__.py
│   ├── routes_module.py                    # Agregação de routers
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── screening.py                    # Use case factories
│   └── routes/
│       ├── __init__.py
│       ├── screening_process_routes.py     # CRUD de processos
│       ├── screening_step_routes.py        # Avanço de etapas
│       ├── screening_document_routes.py    # Upload e revisão de docs
│       └── screening_public_routes.py      # Acesso por token
└── use_cases/
    ├── __init__.py
    ├── screening_process/
    │   ├── __init__.py
    │   ├── screening_process_create_use_case.py
    │   ├── screening_process_get_use_case.py
    │   ├── screening_process_list_use_case.py
    │   ├── screening_process_advance_use_case.py
    │   └── screening_process_complete_use_case.py
    ├── screening_document/
    │   ├── __init__.py
    │   ├── screening_document_select_use_case.py
    │   ├── screening_document_upload_use_case.py
    │   └── screening_document_review_use_case.py
    └── screening_validation/
        ├── __init__.py
        └── screening_client_validation_use_case.py
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | ScreeningProcess |
| TrackingMixin | created_by, updated_by | ScreeningProcess, OrganizationScreeningSettings |
| MetadataMixin | metadata | ScreeningProcess, ScreeningProcessStep |
| VersionMixin | version | ScreeningProcess, ScreeningProcessStep, OrganizationScreeningSettings |

## Relacionamentos com Outros Módulos

### Organizations
- `Organization.screening_settings` → configurações de triagem (1:1)
- `Organization.screening_processes` → lista de processos

### Professionals
- `OrganizationProfessional.screening_processes` → processos vinculados
- `ProfessionalDocument.screening_reviews` → revisões do documento

### Contracts
- `ProfessionalContract.screening_processes` → processos vinculados
- `ClientContract.screening_processes` → processos vinculados
