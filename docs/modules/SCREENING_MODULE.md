# Módulo de Triagem (Screening)

## Visão Geral

O módulo de triagem gerencia o processo de coleta e validação de dados e documentos de profissionais de saúde. Implementa um fluxo de **7 etapas fixas**, com suporte a **versionamento de dados** para rastreabilidade completa de alterações.

### Principais Funcionalidades

- **Fluxo de 7 etapas**: Conversa → Dados do Profissional → Upload de Documentos → Revisão de Documentos → Informações de Pagamento → Revisão do Supervisor → Validação do Cliente
- **Versionamento de dados**: Histórico completo de alterações do profissional via Event Sourcing simplificado
- **Documentos unificados**: Modelo único `ScreeningDocument` que gerencia requisitos, uploads e revisões
- **Steps tipados**: Cada tipo de step tem seu próprio modelo com campos específicos (não usa model genérico)
- **Acesso por token**: Profissionais podem preencher via link seguro sem autenticação completa
- **Vinculação com contratos**: Triagem pode ser associada a contratos específicos

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                      TRIAGEM (SCREENING)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────┐          │
│  │                        PROCESSO DE TRIAGEM                                │          │
│  │                                                                           │          │
│  │  ┌──────────────────┐        ┌───────────────────┐                        │          │
│  │  │   Organization   │───1:N──│  ScreeningProcess │                        │          │
│  │  └──────────────────┘        └───────────────────┘                        │          │
│  │                                      │                                    │          │
│  │         ┌────────────────────────────┼────────────────────────────────┐   │          │
│  │        1:1                          1:1                              1:1  │          │
│  │         │                            │                                │   │          │
│  │  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │   │          │
│  │  │Conversation  │  │ProfessionalData      │  │DocumentUpload        │ │   │          │
│  │  │    Step      │  │       Step           │  │      Step            │ │   │          │
│  │  └──────────────┘  └──────────────────────┘  └──────────────────────┘ │   │          │
│  │                            │                         │                │   │          │
│  │                           N:1                       1:N               │   │          │
│  │                            │                         │                │   │          │
│  │                  ┌─────────────────────┐   ┌─────────────────────┐    │   │          │
│  │                  │ ProfessionalVersion │   │  ScreeningDocument  │    │   │          │
│  │                  └─────────────────────┘   └─────────────────────┘    │   │          │
│  │                            │                                          │   │          │
│  │                           1:N                                         │   │          │
│  │                            │                                          │   │          │
│  │                  ┌─────────────────────────┐                          │   │          │
│  │                  │ ProfessionalChangeDiff  │                          │   │          │
│  │                  └─────────────────────────┘                          │   │          │
│  │                                                                       │   │          │
│  │  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │   │          │
│  │  │DocumentReview│  │   PaymentInfo        │  │  SupervisorReview    │ │   │          │
│  │  │    Step      │  │       Step           │  │       Step           │ │   │          │
│  │  └──────────────┘  └──────────────────────┘  └──────────────────────┘ │   │          │
│  │                                                                       │   │          │
│  │  ┌──────────────────────┐                                             │   │          │
│  │  │  ClientValidation    │                                             │   │          │
│  │  │       Step           │                                             │   │          │
│  │  └──────────────────────┘                                             │   │          │
│  └───────────────────────────────────────────────────────────────────────┘   │          │
│                                                                              │          │
│  ┌───────────────────────────────────────────────────────────────────────┐   │          │
│  │                      VINCULAÇÕES OPCIONAIS                            │   │          │
│  │                                                                       │   │          │
│  │  ScreeningProcess ──N:1── OrganizationProfessional                    │   │          │
│  │  ScreeningProcess ──N:1── ProfessionalContract (opcional)             │   │          │
│  │  ScreeningProcess ──N:1── ClientContract (opcional)                   │   │          │
│  └───────────────────────────────────────────────────────────────────────┘   │          │
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
│ IN_PROGRESS │ ─── Processo em andamento
└──────┬──────┘
       │
       │  Etapas (7 steps fixos):
       │
       │  ┌─────────────────────────────────────────────────────────────┐
       │  │ 1. CONVERSATION      - Conversa inicial (REQUIRED)         │
       │  │ 2. PROFESSIONAL_DATA - Dados completos (REQUIRED)          │
       │  │ 3. DOCUMENT_UPLOAD   - Upload de documentos (REQUIRED)     │
       │  │ 4. DOCUMENT_REVIEW   - Verificação de docs (REQUIRED)      │
       │  │ 5. PAYMENT_INFO      - Conta bancária/empresa (OPTIONAL)   │
       │  │ 6. SUPERVISOR_REVIEW - Revisão superior (OPTIONAL)         │
       │  │ 7. CLIENT_VALIDATION - Aprovação do cliente (OPTIONAL)     │
       │  └─────────────────────────────────────────────────────────────┘
       │
       ├──(rejeitado em qualquer etapa)──► REJECTED
       │
       ├──(expirado)──► EXPIRED
       │
       ├──(cancelado)──► CANCELLED
       │
       └──(todas etapas aprovadas)──► APPROVED
```

## Enums

### StepType
Tipos fixos de etapas no workflow de triagem (7 tipos).

| Valor | Obrigatório | Descrição |
|-------|-------------|-----------|
| CONVERSATION | ✅ | Conversa inicial/pré-triagem por telefone |
| PROFESSIONAL_DATA | ✅ | Dados completos: pessoais + qualificação + especialidades + formação |
| DOCUMENT_UPLOAD | ✅ | Upload de documentos obrigatórios pelo profissional |
| DOCUMENT_REVIEW | ✅ | Verificação de documentos pelo gestor |
| PAYMENT_INFO | ❌ | Conta bancária + empresa PJ (se aplicável) |
| SUPERVISOR_REVIEW | ❌ | Revisão superior para alertas/escalações |
| CLIENT_VALIDATION | ❌ | Validação final pelo cliente contratante |

### ScreeningStatus
Status macro do processo de triagem.

| Valor | Descrição |
|-------|-----------|
| DRAFT | Criado, não iniciado |
| IN_PROGRESS | Em andamento (qualquer etapa) |
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

### ScreeningDocumentStatus
Status unificado de um documento de triagem.

| Valor | Descrição |
|-------|-----------|
| PENDING_UPLOAD | Aguardando upload pelo profissional |
| PENDING_REVIEW | Upload feito, aguardando revisão |
| APPROVED | Documento aprovado |
| REJECTED | Documento rejeitado, precisa re-upload |
| ALERT | Documento com alerta, requer supervisor |
| REUSED | Documento reaproveitado de triagem anterior |
| SKIPPED | Documento não obrigatório, pulado |

### SourceType
Origem de uma alteração nos dados do profissional.

| Valor | Descrição |
|-------|-----------|
| DIRECT | Alteração direta via API/admin |
| SCREENING | Alteração via processo de triagem |
| IMPORT | Importação em lote |
| API | Integração externa |

### ChangeType
Tipo de mudança em um campo específico.

| Valor | Descrição |
|-------|-----------|
| ADDED | Campo/entidade adicionado |
| MODIFIED | Campo/entidade modificado |
| REMOVED | Campo/entidade removido |

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
| expected_professional_type | ProfessionalType | ✅ | Tipo esperado (DOCTOR, NURSE, etc.) |
| expected_specialty_id | UUID | ✅ | Especialidade esperada (para médicos) |
| **Status e Controle** | | | |
| status | ScreeningStatus | ❌ | Status atual (default: DRAFT) |
| **Acesso por Token** | | | |
| access_token | VARCHAR(64) | ✅ | Token para acesso do profissional |
| access_token_expires_at | TIMESTAMP | ✅ | Expiração do token |
| expires_at | TIMESTAMP | ✅ | Expiração do processo |
| **Atribuição** | | | |
| owner_id | UUID | ✅ | Responsável geral pelo processo |
| current_actor_id | UUID | ✅ | Responsável pela ação atual |
| **Rejeição** | | | |
| rejection_reason | VARCHAR(2000) | ✅ | Motivo da rejeição |
| rejected_at | TIMESTAMP | ✅ | Quando foi rejeitado |
| rejected_by | UUID | ✅ | Quem rejeitou |
| **Notas** | | | |
| notes | TEXT | ✅ | Notas gerais |
| **Timestamps de Workflow** | | | |
| completed_at | TIMESTAMP | ✅ | Quando foi finalizado |
| completed_by | UUID | ✅ | Quem finalizou |
| **Mixins** | | | |
| created_by, updated_by | UUID | ✅ | Tracking |
| created_at, updated_at | TIMESTAMP | | Timestamps |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(access_token) WHERE access_token IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(organization_id, professional_cpf) WHERE status NOT IN ('APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED') AND deleted_at IS NULL AND professional_cpf IS NOT NULL`

### Step Tables (7 tabelas)

Cada tipo de step tem sua própria tabela com campos específicos. Todas herdam do `ScreeningStepMixin`.

#### Campos Comuns (ScreeningStepMixin)

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| process_id | UUID | ❌ | FK para screening_processes (unique) |
| step_type | StepType | ❌ | Tipo do step (fixo por tabela) |
| order | INTEGER | ❌ | Ordem no fluxo |
| status | StepStatus | ❌ | Status atual (default: PENDING) |
| assigned_to | UUID | ✅ | Responsável pela etapa |
| review_notes | VARCHAR(2000) | ✅ | Notas da revisão |
| rejection_reason | VARCHAR(2000) | ✅ | Motivo da rejeição |
| **Timestamps de Workflow** | | | |
| started_at | TIMESTAMP | ✅ | Quando iniciou |
| completed_at | TIMESTAMP | ✅ | Quando completou |
| completed_by | UUID | ✅ | Quem completou |
| reviewed_at | TIMESTAMP | ✅ | Quando revisou |
| reviewed_by | UUID | ✅ | Quem revisou |
| **Mixins** | | | |
| version | INTEGER | ❌ | Optimistic locking |
| created_at, updated_at | TIMESTAMP | | Timestamps |

#### screening_conversation_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| conversation_notes | TEXT | ✅ | Notas da conversa |
| outcome | ConversationOutcome | ✅ | Resultado: PROCEED/REJECT |

#### screening_professional_data_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| organization_professional_id | UUID | ✅ | FK para profissional criado/atualizado |
| professional_version_id | UUID | ✅ | FK para versão criada |
| qualification_ids | JSONB | ❌ | Lista de IDs de qualificações |
| specialty_ids | JSONB | ❌ | Lista de IDs de especialidades |
| education_ids | JSONB | ❌ | Lista de IDs de formações |

#### screening_document_upload_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| total_required | INTEGER | ❌ | Total de documentos obrigatórios |
| total_uploaded | INTEGER | ❌ | Total de documentos enviados |
| total_optional | INTEGER | ❌ | Total de documentos opcionais |

**Relationship:** `documents` → lista de `ScreeningDocument`

#### screening_document_review_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| upload_step_id | UUID | ❌ | FK para screening_document_upload_steps |
| total_documents | INTEGER | ❌ | Total a revisar |
| approved_count | INTEGER | ❌ | Quantidade aprovada |
| rejected_count | INTEGER | ❌ | Quantidade rejeitada |
| alert_count | INTEGER | ❌ | Quantidade com alerta |
| pending_count | INTEGER | ❌ | Quantidade pendente |

#### screening_payment_info_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| is_pj | BOOLEAN | ❌ | Se é pessoa jurídica |
| company_id | UUID | ✅ | FK para companies |
| professional_company_id | UUID | ✅ | FK para professional_companies |
| bank_account_id | UUID | ✅ | FK para bank_accounts |
| payment_version_id | UUID | ✅ | FK para versão de pagamento |

#### screening_supervisor_review_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| escalation_reason | TEXT | ✅ | Motivo da escalação |
| escalated_by | UUID | ✅ | Quem escalou |
| escalated_at | TIMESTAMP | ✅ | Quando escalou |

#### screening_client_validation_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| outcome | ClientValidationOutcome | ✅ | Resultado: APPROVED/REJECTED |
| validation_notes | TEXT | ✅ | Notas da validação |
| validated_by_name | VARCHAR(255) | ✅ | Nome de quem validou |
| validated_at | TIMESTAMP | ✅ | Quando foi validado |

### screening_documents

Documento unificado que combina requisito + upload + revisão.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| upload_step_id | UUID | ❌ | FK para screening_document_upload_steps |
| document_type_config_id | UUID | ❌ | FK para document_type_configs |
| professional_document_id | UUID | ✅ | FK para professional_documents (após upload) |
| **Configuração** | | | |
| document_category | DocumentCategory | ❌ | PROFILE/QUALIFICATION/SPECIALTY |
| is_required | BOOLEAN | ❌ | Se é obrigatório |
| description | VARCHAR(500) | ✅ | Descrição/instruções |
| **Status** | | | |
| status | ScreeningDocumentStatus | ❌ | Status atual |
| **Revisão** | | | |
| review_notes | VARCHAR(2000) | ✅ | Notas do revisor |
| rejection_reason | VARCHAR(1000) | ✅ | Motivo da rejeição |
| alert_reason | VARCHAR(1000) | ✅ | Motivo do alerta |
| status_history | JSONB | ❌ | Histórico de mudanças de status |
| **Upload Tracking** | | | |
| uploaded_at | TIMESTAMP | ✅ | Quando foi enviado |
| uploaded_by | UUID | ✅ | Quem enviou |
| **Review Tracking** | | | |
| reviewed_at | TIMESTAMP | ✅ | Quando foi revisado |
| reviewed_by | UUID | ✅ | Quem revisou |
| **Mixins** | | | |
| created_by, updated_by | UUID | ✅ | Tracking |
| created_at, updated_at | TIMESTAMP | | Timestamps |

### professional_versions

Versionamento de dados do profissional (Event Sourcing simplificado).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| professional_id | UUID | ✅ | FK para organization_professionals (null = novo) |
| organization_id | UUID | ❌ | FK para organizations |
| version_number | INTEGER | ❌ | Número sequencial (DB sequence) |
| data_snapshot | JSONB | ❌ | Snapshot completo dos dados |
| is_current | BOOLEAN | ❌ | Se é a versão ativa |
| **Origem** | | | |
| source_type | SourceType | ❌ | DIRECT/SCREENING/IMPORT/API |
| source_id | UUID | ✅ | ID da origem (screening_process_id, etc.) |
| **Aplicação** | | | |
| applied_at | TIMESTAMP | ✅ | Quando foi aplicada |
| applied_by | UUID | ✅ | Quem aplicou |
| rejected_at | TIMESTAMP | ✅ | Quando foi rejeitada |
| rejected_by | UUID | ✅ | Quem rejeitou |
| rejection_reason | TEXT | ✅ | Motivo da rejeição |
| **Mixins** | | | |
| created_by, updated_by | UUID | ✅ | Tracking |
| created_at, updated_at | TIMESTAMP | | Timestamps |

**Índices:**
- `ix_professional_versions_professional_id`
- `ix_professional_versions_organization_id`
- `ix_professional_versions_current WHERE is_current = TRUE`
- `ix_professional_versions_pending WHERE applied_at IS NULL AND rejected_at IS NULL`
- `ix_professional_versions_source (source_type, source_id)`

**Estrutura do data_snapshot:**
```json
{
  "personal_info": {
    "full_name": "João Silva",
    "email": "joao@email.com",
    "phone": "+5511999999999",
    "cpf": "12345678901",
    "birth_date": "1990-01-15",
    "gender": "MALE",
    "address": "Rua Example, 123",
    "city": "São Paulo",
    "state_code": "SP",
    "postal_code": "01234567"
  },
  "qualifications": [
    {
      "id": "uuid",
      "professional_type": "DOCTOR",
      "council_type": "CRM",
      "council_number": "123456",
      "council_state": "SP",
      "is_primary": true
    }
  ],
  "specialties": [
    {
      "id": "uuid",
      "qualification_id": "uuid",
      "specialty_id": "uuid",
      "specialty_code": "CARDIOLOGIA",
      "specialty_name": "Cardiologia",
      "is_primary": true,
      "rqe_number": "12345",
      "residency_status": "COMPLETED"
    }
  ],
  "educations": [
    {
      "id": "uuid",
      "qualification_id": "uuid",
      "level": "SPECIALIZATION",
      "course_name": "Residência em Cardiologia",
      "institution": "USP",
      "is_completed": true
    }
  ],
  "companies": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "cnpj": "12345678000199",
      "legal_name": "Empresa Médica LTDA"
    }
  ],
  "bank_accounts": [
    {
      "id": "uuid",
      "bank_code": "001",
      "agency": "1234",
      "account_number": "12345-6",
      "is_primary": true,
      "pix_key": "joao@email.com"
    }
  ]
}
```

### professional_change_diffs

Registro granular de cada alteração feita em uma versão.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| version_id | UUID | ❌ | FK para professional_versions |
| field_path | VARCHAR(255) | ❌ | Caminho do campo alterado |
| old_value | JSONB | ✅ | Valor anterior |
| new_value | JSONB | ✅ | Novo valor |
| change_type | ChangeType | ❌ | ADDED/MODIFIED/REMOVED |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |

**Exemplos de field_path:**
- `personal_info.full_name`
- `qualifications[0].council_number`
- `specialties[1]` (quando adicionado/removido)
- `bank_accounts[0].pix_key`

**Índices:**
- `ix_professional_change_diffs_version_id`
- `ix_professional_change_diffs_field_path`
- `ix_professional_change_diffs_version_field (version_id, field_path)`

## Regras de Negócio

### Fluxo de 7 Etapas

1. **CONVERSATION** (Obrigatório): Conversa inicial por telefone
2. **PROFESSIONAL_DATA** (Obrigatório): Coleta de todos os dados do profissional
   - Se profissional existe (por CPF): permite complementar/revisar dados
   - Se não existe: cria novo profissional
   - Cria `ProfessionalVersion` com snapshot completo
   - Ao completar: aplica versão ao profissional real
3. **DOCUMENT_UPLOAD** (Obrigatório): Upload de documentos obrigatórios
4. **DOCUMENT_REVIEW** (Obrigatório): Revisão individual de cada documento
5. **PAYMENT_INFO** (Opcional): Dados bancários e empresa PJ
6. **SUPERVISOR_REVIEW** (Opcional): Ativado quando há documentos com ALERT
7. **CLIENT_VALIDATION** (Opcional): Aprovação final pelo cliente contratante

### Versionamento de Dados

1. **Toda alteração cria uma versão**: Ao modificar dados do profissional via triagem, uma nova `ProfessionalVersion` é criada
2. **Snapshot completo**: Cada versão contém todos os dados, não apenas os alterados
3. **Diffs calculados automaticamente**: O use case calcula as diferenças e popula `ProfessionalChangeDiff`
4. **Aplicação controlada**:
   - No screening: versão é aplicada ao completar o step `PROFESSIONAL_DATA`
   - Via API direta: pode ser aplicada imediatamente ou aguardar aprovação
5. **Rastreabilidade**: `source_type` + `source_id` indicam a origem da alteração
6. **Apenas uma versão corrente**: `is_current = true` marca a versão ativa

### Modelo Unificado de Documentos

1. **ScreeningDocument** combina 3 conceitos anteriores:
   - Requisito de documento (o que precisa ser enviado)
   - Upload (arquivo enviado)
   - Revisão (resultado da verificação)
2. **Fluxo de status**:
   ```
   PENDING_UPLOAD → PENDING_REVIEW → APPROVED/REJECTED/ALERT
                         ↓
                    (se rejeitado)
                         ↓
                  PENDING_UPLOAD (re-upload)
   ```
3. **Histórico de status**: `status_history` mantém auditoria de todas as transições

### Acesso por Token

1. Token é gerado quando a triagem é enviada ao profissional
2. Token permite preencher steps sem autenticação completa
3. Token expira após período configurado
4. Apenas steps de coleta de dados são acessíveis por token

## Arquivos de Implementação

```
src/modules/screening/
├── domain/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py                              # StepType, ScreeningStatus, SourceType, ChangeType
│   │   ├── document_type_config.py               # Configuração de tipos de documento
│   │   ├── organization_screening_settings.py   # Configurações por organização
│   │   ├── screening_process.py                  # Processo de triagem
│   │   ├── screening_document.py                 # Documento unificado
│   │   └── steps/
│   │       ├── __init__.py
│   │       ├── base_step.py                      # ScreeningStepMixin
│   │       ├── conversation_step.py
│   │       ├── professional_data_step.py
│   │       ├── document_upload_step.py
│   │       ├── document_review_step.py
│   │       ├── payment_info_step.py
│   │       ├── supervisor_review_step.py
│   │       └── client_validation_step.py
│   └── schemas/
│       └── ...
├── infrastructure/
│   ├── repositories/
│   │   └── ...
│   └── filters/
│       └── ...
├── presentation/
│   ├── routes/
│   │   └── ...
│   └── dependencies/
│       └── ...
└── use_cases/
    └── ...

src/modules/professionals/domain/models/
├── professional_version.py         # Versionamento de dados
├── professional_change_diff.py     # Diffs granulares
└── version_snapshot.py             # TypedDict para data_snapshot
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| VersionMixin | version | Steps, ScreeningProcess |
| SoftDeleteMixin | deleted_at | ScreeningProcess |
| TrackingMixin | created_by, updated_by | ScreeningProcess, ScreeningDocument, ProfessionalVersion |
| ScreeningStepMixin | order, status, assigned_to, review_notes, rejection_reason, timestamps | Todas as tabelas de steps |

## Relacionamentos com Outros Módulos

### Organizations
- `Organization.screening_settings` → configurações de triagem (1:1)
- `Organization.screening_processes` → lista de processos

### Professionals
- `OrganizationProfessional.screening_processes` → processos vinculados
- `OrganizationProfessional.versions` → histórico de versões
- `ProfessionalDocument` ← `ScreeningDocument.professional_document_id`

### Contracts
- `ProfessionalContract.screening_processes` → processos vinculados
- `ClientContract.screening_processes` → processos vinculados
