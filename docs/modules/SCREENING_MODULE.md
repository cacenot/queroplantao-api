# Módulo de Triagem (Screening)

## Visão Geral

O módulo de triagem gerencia o processo de coleta e validação de dados e documentos de profissionais de saúde. Implementa um fluxo de **6 etapas fixas**, com suporte a **versionamento de dados** para rastreabilidade completa de alterações.

### Principais Funcionalidades

- **Fluxo de 6 etapas**: Conversa → Dados do Profissional → Upload de Documentos → Revisão de Documentos → Informações de Pagamento → Validação do Cliente
- **Sistema de Alertas**: Alertas podem ser criados a qualquer momento para escalar ao supervisor
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
│  │        1:1                          1:1                              1:N  │          │
│  │         │                            │                                │   │          │
│  │  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │   │          │
│  │  │Conversation  │  │ProfessionalData      │  │  ScreeningAlert      │ │   │          │
│  │  │    Step      │  │       Step           │  │    (Alertas)         │ │   │          │
│  │  └──────────────┘  └──────────────────────┘  └──────────────────────┘ │   │          │
│  │                            │                                          │   │          │
│  │                           N:1                                         │   │          │
│  │                            │                                          │   │          │
│  │                  ┌─────────────────────┐   ┌─────────────────────┐    │   │          │
│  │                  │ ProfessionalVersion │   │  DocumentUploadStep │    │   │          │
│  │                  └─────────────────────┘   └─────────────────────┘    │   │          │
│  │                            │                        │                 │   │          │
│  │                           1:N                      1:N                │   │          │
│  │                            │                        │                 │   │          │
│  │                  ┌─────────────────────────┐ ┌─────────────────────┐  │   │          │
│  │                  │ ProfessionalChangeDiff  │ │ ScreeningDocument   │  │   │          │
│  │                  └─────────────────────────┘ └─────────────────────┘  │   │          │
│  │                                                                       │   │          │
│  │  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │   │          │
│  │  │DocumentReview│  │   PaymentInfo        │  │  ClientValidation   │ │   │          │
│  │  │    Step      │  │       Step           │  │       Step          │ │   │          │
│  │  └──────────────┘  └──────────────────────┘  └──────────────────────┘ │   │          │
│  │                                                                       │   │          │
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
┌─────────────┐
│ IN_PROGRESS │ ─── Processo criado e em andamento
└──────┬──────┘
       │
       │  Etapas (6 steps fixos):
       │
       │  ┌─────────────────────────────────────────────────────────────┐
       │  │ 1. CONVERSATION      - Conversa inicial (REQUIRED)         │
       │  │ 2. PROFESSIONAL_DATA - Dados completos (REQUIRED)          │
       │  │ 3. DOCUMENT_UPLOAD   - Upload de documentos (REQUIRED)     │
       │  │ 4. DOCUMENT_REVIEW   - Verificação de docs (REQUIRED)      │
       │  │ 5. PAYMENT_INFO      - Conta bancária/empresa (OPTIONAL)   │
       │  │ 6. CLIENT_VALIDATION - Aprovação do cliente (OPTIONAL)     │
       │  └─────────────────────────────────────────────────────────────┘
       │
       ├──(alerta criado)──► PENDING_SUPERVISOR
       │                           │
       │                           ├──(alerta resolvido)──► IN_PROGRESS
       │                           │
       │                           └──(rejeitado via alerta)──► REJECTED
       │
       ├──(rejeitado em qualquer etapa)──► REJECTED
       │
       ├──(expirado)──► EXPIRED
       │
       ├──(cancelado)──► CANCELLED
       │
       └──(todas etapas aprovadas)──► APPROVED

### Mecânica de Controle de Fluxo

O progresso é controlado por duas colunas desnormalizadas na tabela principal, permitindo consultas eficientes sem joins:

1. **`configured_step_types`**: Lista ordenada de etapas definida na criação (snapshot).
   - Exemplo: `['CONVERSATION', 'PROFESSIONAL_DATA', 'DOCUMENT_UPLOAD', 'DOCUMENT_REVIEW']`
   - Permite flexibilidade caso o fluxo mude no futuro (processos antigos mantêm seu fluxo).

2. **`current_step_type`**: Ponteiro para a etapa ativa.
   - Avanço: Ao completar uma etapa, o sistema busca o próximo item na lista configurada.
   - Término: Se não houver próximo item, o processo é movido para `APPROVED`.

Isso resolve problemas de performance (N+1 queries) e complexidade (joins múltiplos) na listagem de triagens.

## Enums

### StepType
Tipos fixos de etapas no workflow de triagem (6 tipos).

| Valor | Obrigatório | Descrição |
|-------|-------------|-----------|
| CONVERSATION | ✅ | Conversa inicial/pré-triagem por telefone |
| PROFESSIONAL_DATA | ✅ | Dados completos: pessoais + qualificação + especialidades + formação |
| DOCUMENT_UPLOAD | ✅ | Upload de documentos obrigatórios pelo profissional |
| DOCUMENT_REVIEW | ✅ | Verificação de documentos pelo gestor |
| PAYMENT_INFO | ❌ | Conta bancária + empresa PJ (se aplicável) |
| CLIENT_VALIDATION | ❌ | Validação final pelo cliente contratante |

### AlertCategory
Categorias de alertas de triagem.

| Valor | Descrição |
|-------|-----------|
| DOCUMENT | Problema com documentos |
| DATA | Dados inconsistentes |
| BEHAVIOR | Comportamento inadequado |
| COMPLIANCE | Problemas de conformidade |
| QUALIFICATION | Qualificação insuficiente |
| OTHER | Outros |

### ScreeningStatus
Status macro do processo de triagem.

| Valor | Descrição |
|-------|-----------|
| IN_PROGRESS | Em andamento (qualquer etapa) |
| PENDING_SUPERVISOR | Aguardando ação do supervisor (alerta criado) |
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
| PENDING_UPLOAD | Aguardando upload (profissional ou gestor) |
| PENDING_REVIEW | Upload feito, aguardando revisão |
| APPROVED | Documento aprovado |
| CORRECTION_NEEDED | Documento precisa de correção, re-upload necessário |
| REUSED | **Legado (não usar como status no fluxo novo)**. Regra do produto: tratar como **origem** e manter `status = PENDING_REVIEW` (segue para revisão) |
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

### ScreeningErrorCodes (Error Codes)

Códigos de erro específicos do módulo de triagem. Todos os códigos são prefixados com `SCREENING_`.

#### Process Errors
| Código | Descrição |
|--------|-----------|
| `SCREENING_PROCESS_NOT_FOUND` | Processo de triagem não encontrado |
| `SCREENING_PROCESS_ACTIVE_EXISTS` | Já existe uma triagem ativa para este profissional |
| `SCREENING_PROCESS_INVALID_STATUS` | Status do processo não permite esta ação |
| `SCREENING_PROCESS_ALREADY_COMPLETED` | Processo já foi finalizado |
| `SCREENING_PROCESS_CANNOT_APPROVE` | Não é possível aprovar o processo |
| `SCREENING_PROCESS_CANNOT_REJECT` | Não é possível rejeitar o processo |
| `SCREENING_PROCESS_CANNOT_CANCEL` | Não é possível cancelar o processo |
| `SCREENING_PROCESS_HAS_REJECTED_DOCUMENTS` | Processo possui documentos rejeitados |
| `SCREENING_PROCESS_INCOMPLETE_STEPS` | Etapas obrigatórias incompletas |

#### Step Errors
| Código | Descrição |
|--------|-----------|
| `SCREENING_STEP_NOT_FOUND` | Step não encontrado |
| `SCREENING_STEP_ALREADY_COMPLETED` | Step já foi completado |
| `SCREENING_STEP_SKIPPED` | Step foi pulado |
| `SCREENING_STEP_NOT_IN_PROGRESS` | Step não está em andamento |
| `SCREENING_STEP_NOT_PENDING` | Step não está pendente |
| `SCREENING_STEP_INVALID_TYPE` | Tipo de step inválido |
| `SCREENING_STEP_CANNOT_GO_BACK` | Não é possível retroceder no fluxo |
| `SCREENING_STEP_NOT_ASSIGNED_TO_USER` | Step não atribuído a este usuário |
| `SCREENING_STEP_NOT_CONFIGURED` | **Step não foi configurado (is_configured = false). Upload/reutilização/complete bloqueados.** |
| `SCREENING_STEP_ALREADY_CONFIGURED` | **Step já foi configurado (is_configured = true). Reconfiguração não permitida.** |

#### Document Errors
| Código | Descrição |
|--------|-----------|
| `SCREENING_DOCUMENTS_NOT_UPLOADED` | Documentos não foram enviados |
| `SCREENING_DOCUMENTS_MISSING_REQUIRED` | Documentos obrigatórios faltando |
| `SCREENING_DOCUMENTS_PENDING_REVIEW` | Documentos aguardando revisão |
| `SCREENING_DOCUMENTS_NOT_REVIEWED` | Documentos não foram revisados |
| `SCREENING_DOCUMENT_NOT_FOUND` | Documento não encontrado |
| `SCREENING_DOCUMENT_INVALID_STATUS` | Status do documento não permite esta ação |
| `SCREENING_DOCUMENT_TYPE_MISMATCH` | Tipo de documento não corresponde |
| `SCREENING_DOCUMENT_REUSE_PENDING` | Documento para reutilização está pendente |

#### Alert Errors
| Código | Descrição |
|--------|-----------|
| `SCREENING_ALERT_NOT_FOUND` | Alerta não encontrado |
| `SCREENING_ALERT_ALREADY_EXISTS` | Já existe um alerta pendente |
| `SCREENING_ALERT_ALREADY_RESOLVED` | Alerta já foi resolvido |
| `SCREENING_PROCESS_BLOCKED_BY_ALERT` | Processo bloqueado por alerta pendente |

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
| status | ScreeningStatus | ❌ | Status atual (default: **IN_PROGRESS**) |
| current_step_type | StepType | ❌ | Etapa ativa (default: CONVERSATION) |
| configured_step_types | VARCHAR[] | ❌ | Lista ordenada de etapas deste processo |
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
| is_configured | BOOLEAN | ❌ | Se os documentos foram configurados para este step (default: `false`) |
| total_documents | INTEGER | ❌ | Total de documentos configurados |
| required_documents | INTEGER | ❌ | Número de documentos obrigatórios |
| uploaded_documents | INTEGER | ❌ | Número de documentos já enviados |

**Relationship:** `documents` → lista de `ScreeningDocument`

**Propriedades Computadas (não persistidas):**
- `optional_documents` → `total_documents - required_documents`
- `all_required_uploaded` → `uploaded_documents >= required_documents`

#### screening_document_review_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| upload_step_id | UUID | ❌ | FK para screening_document_upload_steps |
| total_documents | INTEGER | ❌ | Total a revisar |
| approved_count | INTEGER | ❌ | Quantidade aprovada |
| correction_needed_count | INTEGER | ❌ | Quantidade que precisa correção |
| pending_count | INTEGER | ❌ | Quantidade pendente |

#### screening_payment_info_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| is_pj | BOOLEAN | ❌ | Se é pessoa jurídica |
| company_id | UUID | ✅ | FK para companies |
| professional_company_id | UUID | ✅ | FK para professional_companies |
| bank_account_id | UUID | ✅ | FK para bank_accounts |
| payment_version_id | UUID | ✅ | FK para versão de pagamento |

#### screening_client_validation_steps

| Campo Adicional | Tipo | Nullable | Descrição |
|-----------------|------|----------|-----------|
| outcome | ClientValidationOutcome | ✅ | Resultado: APPROVED/REJECTED |
| validation_notes | TEXT | ✅ | Notas da validação |
| validated_by_name | VARCHAR(255) | ✅ | Nome de quem validou |
| validated_at | TIMESTAMP | ✅ | Quando foi validado |

### screening_alerts

Alertas que podem ser criados a qualquer momento durante a triagem para escalar ao supervisor.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| process_id | UUID | ❌ | FK para screening_processes |
| reason | VARCHAR(2000) | ❌ | Motivo do alerta |
| category | AlertCategory | ❌ | Categoria do alerta |
| notes | JSONB | ❌ | Histórico de notas (AlertNote[]) |
| is_resolved | BOOLEAN | ❌ | Se foi resolvido |
| resolved_at | TIMESTAMP | ✅ | Quando foi resolvido |
| resolved_by | UUID | ✅ | Quem resolveu |
| created_by, updated_by | UUID | ✅ | Tracking |
| created_at, updated_at | TIMESTAMP | | Timestamps |

**AlertNote (TypedDict):**
```json
{
  "timestamp": "2026-01-28T14:00:00Z",
  "user_id": "uuid-string",
  "user_name": "João Silva",
  "user_role": "Escalista",
  "content": "Documentos verificados"
}
```

### screening_documents

Documento unificado que combina requisito + upload + revisão.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| upload_step_id | UUID | ❌ | FK para screening_document_upload_steps |
| document_type_id | UUID | ❌ | FK para document_types (shared) |
| professional_document_id | UUID | ✅ | FK para professional_documents (após upload) |
| **Configuração** | | | |
| is_required | BOOLEAN | ❌ | Se é obrigatório |
| order | INTEGER | ❌ | Ordem de exibição |
| description | VARCHAR(500) | ✅ | Descrição/instruções customizadas |
| **Status** | | | |
| status | ScreeningDocumentStatus | ❌ | Status atual |
| **Revisão** | | | |
| review_notes | VARCHAR(2000) | ✅ | Notas do revisor |
| rejection_reason | VARCHAR(1000) | ✅ | Motivo da correção necessária |
| review_history | JSONB | ❌ | Histórico de ações de revisão |
| **Upload Tracking** | | | |
| uploaded_at | TIMESTAMP | ✅ | Quando foi enviado |
| uploaded_by | UUID | ✅ | Quem enviou |
| **Review Tracking** | | | |
| reviewed_at | TIMESTAMP | ✅ | Quando foi revisado |
| reviewed_by | UUID | ✅ | Quem revisou |
| **Mixins** | | | |
| created_by, updated_by | UUID | ✅ | Tracking |
| created_at, updated_at | TIMESTAMP | | Timestamps |

**Nota:** A categoria do documento (`PROFILE`, `QUALIFICATION`, `SPECIALTY`) é obtida via relacionamento com `document_types.category`.

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
3. **DOCUMENT_UPLOAD** (Obrigatório): Configuração e upload de documentos
   - **Fase 1 - Configuração** (`is_configured = false`):
     - Gestor define quais documentos são necessários via endpoint `/configure`
     - Upload, reutilização e complete são **bloqueados** nesta fase
     - Após configuração, `is_configured = true` e step avança para `IN_PROGRESS`
   - **Fase 2 - Upload** (`is_configured = true`):
     - Profissional/Gestor faz upload dos arquivos
     - Reconfiguração **não é permitida** (erro `SCREENING_STEP_ALREADY_CONFIGURED`)
     - Step pode ser completado quando todos os documentos obrigatórios forem enviados
4. **DOCUMENT_REVIEW** (Obrigatório): Revisão individual de cada documento
5. **PAYMENT_INFO** (Opcional): Dados bancários e empresa PJ
6. **CLIENT_VALIDATION** (Opcional): Aprovação final pelo cliente contratante

### Sistema de Alertas

A qualquer momento durante a triagem (desde que `status = IN_PROGRESS`), um alerta pode ser criado para escalar ao supervisor:

```
┌─────────────┐
│ IN_PROGRESS │
└──────┬──────┘
       │
       │ POST /screenings/{id}/alerts
       │ Payload: { reason, category }
       ▼
┌────────────────────┐
│ PENDING_SUPERVISOR │ ◄── Processo bloqueado
└─────────┬──────────┘
          │
          ├── POST /screenings/{id}/alerts/{alert_id}/resolve
          │   └── Processo volta para IN_PROGRESS
          │
          └── POST /screenings/{id}/alerts/{alert_id}/reject
              └── Processo vai para REJECTED
```

**Características:**
- Apenas um alerta pendente por vez
- O `current_actor_id` passa a ser o `supervisor_id`
- Histórico de notas mantido no campo `notes` (JSONB)
- Qualquer usuário pode criar alerta, mas só supervisor resolve/rejeita

### Fluxo Detalhado: DOCUMENT_UPLOAD e DOCUMENT_REVIEW

O processo de documentos é dividido em duas etapas com um fluxo de estados bem definido.

**O DOCUMENT_UPLOAD possui duas fases controladas pela flag `is_configured`:**
1. **Fase de Configuração** (`is_configured = false`): Gestor define quais documentos são necessários
2. **Fase de Upload** (`is_configured = true`): Profissional/Gestor envia os documentos

Esta separação garante que:
- Documentos não podem ser enviados antes de serem configurados
- A lista de documentos não pode ser alterada após a configuração inicial
- O fluxo é mais previsível e rastreável

#### Guia de Frontend (para agente de IA)

**Objetivo:** o frontend deve tratar o backend como **fonte de verdade** do workflow.

**Carregar estado (sempre):**
- Gestor (autenticado): `GET /api/v1/screenings/{screening_id}`
- Profissional (público): `GET /api/v1/public/screening/{token}`

**Verificar fase do Document Upload:**
- Use `DocumentUploadStepResponse.is_configured` para determinar a fase:
  - `is_configured = false` → Mostrar UI de configuração de documentos
  - `is_configured = true` → Mostrar UI de upload de documentos

**Como renderizar estado por documento (recomendação):**
- Use `ScreeningDocument.status` (e flags como `needs_upload`, `needs_review`, `needs_correction`) para decidir UI.
- Use contadores do step (`required_documents`, `uploaded_documents`, etc.) apenas como *informação auxiliar*.
- Use `all_required_uploaded` (propriedade computada) para habilitar/desabilitar botão "Completar Step"

**Ações por fase:**

*Fase de Configuração (`is_configured = false`):*
- Gestor configura documentos:
  - `POST /api/v1/screenings/{screening_id}/steps/document-upload/configure`
  - Body: `{ documents: [{ document_type_id, is_required, order, description }] }`
  - ⚠️ Esta ação só pode ser executada UMA VEZ

*Fase de Upload (`is_configured = true`):*
- Upload novo:
  - Gestor: `POST /api/v1/screenings/{screening_id}/documents/{document_id}/upload`
  - Público: `POST /api/v1/public/screening/{token}/documents/{document_id}/upload`
  - `multipart/form-data`: `file` + `expires_at?` + `notes?`
  - Retorno: `ScreeningDocumentResponse` atualizado (use isso para atualizar o card imediatamente).

- Reutilização (gestor):
  - `POST /api/v1/screenings/{screening_id}/documents/{document_id}/reuse?professional_document_id=...`
  - Retorno: `ScreeningDocumentResponse` atualizado.
  - Regra do produto: reutilização é equivalente ao upload no workflow; muda apenas a origem.

**Revisão (gestor):**
- `POST /api/v1/screenings/{screening_id}/documents/{document_id}/review`
- Body: `{ approved: boolean, notes?: string, rejection_reason?: string }`

**Refresh recomendado (robustez):**
- Após uma sequência de uploads/reuse/reviews, faça `GET` do processo novamente para sincronizar contadores e status de steps.

#### Diagrama do Fluxo de Documentos

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT_UPLOAD Step                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Fase 1: Configuração (is_configured = false)                                           │
│  ─────────────────────────────────────────────                                          │
│  Step criado mas ainda não configurado.                                                 │
│  Nenhum documento foi selecionado ainda.                                                │
│  status = PENDING, is_configured = false                                                │
│                                                                                         │
│  Ações BLOQUEADAS nesta fase:                                                           │
│  • Upload de documento      → Error: SCREENING_STEP_NOT_CONFIGURED                      │
│  • Reutilização de documento → Error: SCREENING_STEP_NOT_CONFIGURED                     │
│  • Completar step           → Error: SCREENING_STEP_NOT_CONFIGURED                      │
│                                                                                         │
│       │                                                                                 │
│       │ POST /api/v1/screenings/{screening_id}/steps/document-upload/configure          │
│       │ Payload: lista de document_type_ids com is_required, order, description         │
│       │ ⚠️ IMPORTANTE: Este endpoint só pode ser chamado UMA VEZ                        │
│       │ Se is_configured=true → Error: SCREENING_STEP_ALREADY_CONFIGURED               │
│       ▼                                                                                 │
│                                                                                         │
│  Fase 2: Upload (is_configured = true)                                                  │
│  ────────────────────────────────────                                                   │
│  Documentos configurados, aguardando uploads.                                           │
│  ScreeningDocument records criados com status PENDING_UPLOAD.                           │
│  status = IN_PROGRESS, is_configured = true                                             │
│                                                                                         │
│       │                                                                                 │
│       │ Para cada documento (duas opções equivalentes):                                 │
│       │                                                                                 │
│       │ 1) Upload (arquivo novo, fluxo atômico na API)                                  │
│       │    POST /api/v1/screenings/{screening_id}/documents/{document_id}/upload         │
│       │    POST /api/v1/public/screening/{token}/documents/{document_id}/upload          │
│       │    Form: file (binary), expires_at (opcional), notes (opcional)                 │
│       │                                                                                 │
│       │ 2) Reutilização (sem upload de arquivo, fluxo equivalente)                       │
│       │    POST /api/v1/screenings/{screening_id}/documents/{document_id}/reuse          │
│       │      ?professional_document_id={uuid}                                            │
│       │                                                                                 │
│       │ Em ambos os casos (regra do produto):                                            │
│       │ - Backend vincula ProfessionalDocument ao ScreeningDocument                       │
│       │ - Atualiza DocumentUploadStep.uploaded_documents (contador)                       │
│       │ - ScreeningDocument.status → PENDING_REVIEW                                       │
│       │ - DOCUMENT_REVIEW é obrigatório (sempre passa por revisão)                       │
│       ▼                                                                                 │
│                                                                                         │
│  Uploads Completos                                                                      │
│  ─────────────────                                                                      │
│  Todos os documentos obrigatórios (is_required=true) foram enviados.                    │
│                                                                                         │
│       │                                                                                 │
│       │ Regra do produto: o backend pode marcar automaticamente o step como COMPLETED   │
│       │ quando todos os required docs saírem de PENDING_UPLOAD.                          │
│                                                                                         │
│       │ Endpoint explícito (fallback/idempotente):                                       │
│       │ POST /api/v1/screenings/{screening_id}/steps/{step_id}/document-upload/complete │
│       │ Valida: todos required docs com status != PENDING_UPLOAD                         │
│       ▼                                                                                 │
│                                                                                         │
│  Status: COMPLETED                                                                      │
│  ─────────────────                                                                      │
│  Step finalizado, pronto para revisão.                                                  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                              │
                              ▼

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT_REVIEW Step                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Status: IN_PROGRESS                                                                    │
│  ────────────────────                                                                   │
│  Gestor revisa cada documento individualmente.                                          │
│                                                                                         │
│       │                                                                                 │
│       │ POST /api/v1/screenings/{screening_id}/documents/{document_id}/review            │
│       │ Payload: { approved: true|false, notes?, rejection_reason? }                     │
│       │                                                                                 │
│       │ Para cada documento:                                                            │
│       │   • APPROVED: documento válido                                                  │
│       │   • CORRECTION_NEEDED: documento inválido, precisa re-upload                    │
│       ▼                                                                                 │
│                                                                                         │
│  Todos Revisados                                                                        │
│  ───────────────                                                                        │
│  Nenhum documento com status PENDING_REVIEW.                                            │
│                                                                                         │
│       │                                                                                 │
│       │ Regra do produto: o backend pode completar automaticamente o step                │
│       │ quando não houver PENDING_REVIEW.                                                │
│                                                                                         │
│       │ Endpoint explícito (fallback/idempotente):                                       │
│       │ POST /api/v1/screenings/{screening_id}/steps/{step_id}/document-review/complete │
│       ▼                                                                                 │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                       DECISÃO BASEADA NOS RESULTADOS                            │    │
│  ├─────────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                                 │    │
│  │  ┌─────────────────────┐              ┌─────────────────────────┐               │    │
│  │  │   Todos APPROVED    │              │ Algum CORRECTION_NEEDED │               │    │
│  │  └──────────┬──────────┘              └────────────┬────────────┘               │    │
│  │             │                                      │                            │    │
│  │             ▼                                      ▼                            │    │
│  │       Step APPROVED                       Step CORRECTION_NEEDED                │    │
│  │       Prossegue para                      Retorna ao DOCUMENT_UPLOAD            │    │
│  │       próximo step                        para re-upload                        │    │
│  │                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Ciclo de Correção de Documentos

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                           CICLO DE CORREÇÃO                                           │
├───────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  DOCUMENT_REVIEW.complete() com documentos CORRECTION_NEEDED                          │
│                                                                                       │
│       │                                                                               │
│       │ 1. DocumentReviewStep.status → CORRECTION_NEEDED                              │
│       │ 2. DocumentUploadStep.status → CORRECTION_NEEDED                              │
│       │ 3. ScreeningDocument (com correção).status → permanece CORRECTION_NEEDED      │
│       ▼                                                                               │
│                                                                                       │
│  Profissional notificado para re-upload                                               │
│                                                                                       │
│       │                                                                               │
│       │ POST /api/v1/screenings/{screening_id}/documents/{document_id}/upload (re-upload)│
│       │ POST /api/v1/public/screening/{token}/documents/{document_id}/upload (re-upload) │
│       │ ScreeningDocument.status → PENDING_REVIEW                                     │
│       │ Histórico de revisão mantido em review_history[]                              │
│       ▼                                                                               │
│                                                                                       │
│  Todos re-uploads feitos                                                              │
│                                                                                       │
│       │                                                                               │
│       │ POST /api/v1/screenings/{screening_id}/steps/{step_id}/document-upload/complete│
│       │ DocumentUploadStep.status → COMPLETED                                         │
│       ▼                                                                               │
│                                                                                       │
│  Volta para DOCUMENT_REVIEW                                                           │
│                                                                                       │
│       │                                                                               │
│       │ DocumentReviewStep.status → IN_PROGRESS                                       │
│       │ Gestor revisa novamente                                                       │
│       ▼                                                                               │
│                                                                                       │
│  (Ciclo repete até todos APPROVED ou processo rejeitado)                              │
│                                                                                       │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

#### Estados do ScreeningDocument

```
                    ┌─────────────────┐
                    │ PENDING_UPLOAD  │◄─────────────────────────────┐
                    └────────┬────────┘                              │
                             │                                       │
                             │ upload()                              │
                             ▼                                       │
                    ┌─────────────────┐                              │
                    │ PENDING_REVIEW  │                              │
                    └────────┬────────┘                              │
                             │                                       │
                             │ review()                              │
                             ▼                                       │
            ┌────────────────┼────────────────┐                      │
            │                │                │                      │
            ▼                ▼                ▼                      │
    ┌───────────┐    ┌──────────────────┐    │                       │
    │ APPROVED  │    │CORRECTION_NEEDED │────┘                       │
    └───────────┘    └──────────────────┘   (ciclo de correção)


    Estados Especiais:
    ┌───────────┐
    │  SKIPPED  │
    └───────────┘
    (doc opcional não enviado)

    Origem (para auditoria/UX):
    - Upload novo: cria ProfessionalDocument (is_pending=True)
    - Reutilização: vincula ProfessionalDocument existente (is_pending=False)

    Importante: "REUSED" deve ser tratado como ORIGEM (não como status).
    Mesmo em reutilização, o status segue o fluxo normal: PENDING_REVIEW → review().
```

### Documentos Pendentes (Pending Documents)

Documentos enviados durante uma triagem são criados como **pendentes** (`is_pending=True`) no modelo `ProfessionalDocument`. 
Isso significa que o documento existe no sistema, mas **não substitui a versão oficial do profissional** até que a triagem seja finalizada.

#### Por que documentos pendentes?

1. **Segurança**: Se a triagem for cancelada ou rejeitada, os documentos não aprovados são automaticamente removidos
2. **Versionamento**: Mantém histórico claro entre documentos "oficiais" e documentos em processo de aprovação
3. **Reutilização**: Permite que documentos já aprovados de triagens anteriores sejam reutilizados sem novo upload

#### Campos no ProfessionalDocument

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `is_pending` | BOOLEAN | Se está pendente de aprovação (default: False) |
| `source_type` | DocumentSourceType | Origem do documento: DIRECT ou SCREENING |
| `screening_id` | UUID | FK para screening_processes (se criado durante triagem) |
| `promoted_at` | TIMESTAMP | Quando foi promovido (is_pending → False) |
| `promoted_by` | UUID | Quem promoveu o documento |

#### DocumentSourceType Enum

| Valor | Descrição |
|-------|-----------|
| `DIRECT` | Upload direto via API/admin (documento já aprovado) |
| `SCREENING` | Upload durante processo de triagem (pendente até aprovação) |

#### Fluxo de Documentos Pendentes

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         FLUXO DE DOCUMENTOS PENDENTES                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Upload de documento durante triagem (FLUXO CONSOLIDADO)                                │
│                                                                                         │
│       │                                                                                 │
│       │ 1. Frontend envia arquivo via multipart/form-data                               │
│       │    POST /api/v1/screenings/{screening_id}/documents/{document_id}/upload         │
│       │    POST /api/v1/public/screening/{token}/documents/{document_id}/upload          │
│       │    → Form: file (binary), expires_at, notes                                     │
│       │                                                                                 │
│       │ 2. Backend faz upload para Firebase Storage                                     │
│       │                                                                                 │
│       │ 3. Backend cria ProfessionalDocument automaticamente:                           │
│       │    → is_pending = True                                                          │
│       │    → source_type = SCREENING                                                    │
│       │    → screening_id = ID do processo                                              │
│       │    → qualification_id = inferido (ver tabela abaixo)                            │
│       │    → specialty_id = inferido (ver tabela abaixo)                                │
│       │                                                                                 │
│       │ 4. Backend vincula ProfessionalDocument ao ScreeningDocument                    │
│       ▼                                                                                 │
│                                                                                         │
│  Inferência Automática de qualification_id e specialty_id                               │
│  ─────────────────────────────────────────────────────────────────────────              │
│  ┌─────────────┬──────────────────────────────┬─────────────────────────┐               │
│  │  Categoria  │  qualification_id            │  specialty_id           │               │
│  ├─────────────┼──────────────────────────────┼─────────────────────────┤               │
│  │  PROFILE    │  null                        │  null                   │               │
│  │  QUALIFIC.  │  primary/first qualification │  null                   │               │
│  │  SPECIALTY  │  primary/first qualification │  expected_specialty_id  │               │
│  └─────────────┴──────────────────────────────┴─────────────────────────┘               │
│                                                                                         │
│  Notas:                                                                                 │
│  • Médicos podem não ter especialidade (generalista/clínico geral)                      │
│  • Se não houver qualificação cadastrada, o campo fica null                             │
│  • A qualificação é atualizada posteriormente se necessário                             │
│                                                                                         │
│  Documento criado como PENDENTE                                                         │
│  ─────────────────────────────                                                          │
│  O profissional pode visualizar o documento enviado,                                    │
│  mas ele ainda não é a versão "oficial".                                                │
│                                                                                         │
│       │                                                                                 │
│       │ Triagem continua normalmente...                                                 │
│       │ Revisão de documentos, etc.                                                     │
│       ▼                                                                                 │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                       DECISÃO FINAL DA TRIAGEM                                  │    │
│  ├─────────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                                 │    │
│  │  ┌─────────────────────┐              ┌─────────────────────────┐               │    │
│  │  │  Triagem APROVADA   │              │ Triagem CANCELADA/      │               │    │
│  │  │  POST /finalize     │              │ REJEITADA               │               │    │
│  │  └──────────┬──────────┘              └────────────┬────────────┘               │    │
│  │             │                                      │                            │    │
│  │             ▼                                      ▼                            │    │
│  │   Promove documentos:                    Soft-delete documentos:                │    │
│  │   • is_pending = False                   • deleted_at = now()                   │    │
│  │   • promoted_at = now()                  (apenas is_pending=True)               │    │
│  │   • promoted_by = user_id                                                       │    │
│  │                                                                                 │    │
│  │   Documentos tornam-se                   Documentos órfãos são                  │    │
│  │   versão oficial                         removidos automaticamente              │    │
│  │                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Reutilização de Documentos

Profissionais podem reutilizar documentos já aprovados de triagens anteriores, evitando re-upload do mesmo arquivo.

#### Fluxo de Reutilização

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         REUTILIZAÇÃO DE DOCUMENTOS                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Profissional tem documento aprovado de triagem anterior                                │
│  (is_pending = False, source_type = SCREENING ou DIRECT)                                │
│                                                                                         │
│       │                                                                                 │
│       │ POST /api/v1/screenings/{screening_id}/documents/{document_id}/reuse             │
│       │   ?professional_document_id={uuid-do-doc-existente}                              │
│       ▼                                                                                 │
│                                                                                         │
│  Validações:                                                                            │
│  ─────────────                                                                          │
│  • ScreeningDocument está em PENDING_UPLOAD ou CORRECTION_NEEDED                        │
│  • ProfessionalDocument existe e is_pending = False                                     │
│  • document_type_id do ProfessionalDocument == do ScreeningDocument                     │
│                                                                                         │
│       │                                                                                 │
│       │ Vinculação:                                                                     │
│       │ • ScreeningDocument.professional_document_id = uuid-doc-existente               │
│       │ • ScreeningDocument.status = PENDING_REVIEW                                     │
│       │ • Registra em review_history (origem = REUSED / ação = REUSE)                   │
│       │ • Atualiza DocumentUploadStep.uploaded_documents (contador)                     │
│       ▼                                                                                 │
│                                                                                         │
│  Regra do produto: documento reutilizado PASSA por DOCUMENT_REVIEW                      │
│  (mesmas regras do upload: revisão obrigatória e avanço automático/contadores iguais). │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Importante:** Documentos reutilizados (origem `REUSED` / ação `REUSE` no `review_history`) **não criam novo ProfessionalDocument** - apenas vinculam o existente ao `ScreeningDocument`.

### Endpoint de Finalização

```
POST /api/v1/screenings/{screening_id}/finalize
```

Finaliza a triagem e promove todos os documentos pendentes.

#### Validações

1. Triagem deve estar em status `IN_PROGRESS`
2. Todas as etapas obrigatórias devem estar `COMPLETED` ou `APPROVED`

#### Ações Realizadas

1. Promove documentos pendentes: `is_pending = False`
2. Registra promoção: `promoted_at`, `promoted_by`
3. Atualiza status da triagem: `APPROVED`
4. Registra conclusão: `completed_at`

#### Response

```json
{
  "id": "uuid",
  "status": "APPROVED",
  "completed_at": "2024-01-15T10:30:00Z",
  // ... demais campos
}
```

#### Error Codes

| Status | Code | Descrição |
|--------|------|-----------|
| 404 | `SCREENING_PROCESS_NOT_FOUND` | Triagem não encontrada |
| 422 | `VALIDATION_ERROR` | Etapas incompletas |

### Error Codes do Document Upload Step

O step de upload de documentos possui validações específicas baseadas na flag `is_configured`:

| Status | Code | Contexto | Descrição |
|--------|------|----------|-----------|
| 409 | `SCREENING_STEP_ALREADY_CONFIGURED` | Configure | Tentativa de reconfigurar documentos após `is_configured = true` |
| 422 | `SCREENING_STEP_NOT_CONFIGURED` | Upload | Tentativa de upload antes de configurar documentos (`is_configured = false`) |
| 422 | `SCREENING_STEP_NOT_CONFIGURED` | Reuse | Tentativa de reutilização antes de configurar documentos |
| 422 | `SCREENING_STEP_NOT_CONFIGURED` | Complete | Tentativa de completar step antes de configurar documentos |

**Fluxo de Estados do Step:**

```
                ┌──────────────────────────────────┐
                │  is_configured = false           │
                │  status = PENDING                │
                │                                  │
                │  ❌ Upload bloqueado             │
                │  ❌ Reutilização bloqueada       │
                │  ❌ Complete bloqueado           │
                └───────────────┬──────────────────┘
                                │
                                │ POST /configure
                                │ ✅ Sucesso: is_configured = true
                                │
                                ▼
                ┌──────────────────────────────────┐
                │  is_configured = true            │
                │  status = IN_PROGRESS            │
                │                                  │
                │  ✅ Upload permitido             │
                │  ✅ Reutilização permitida       │
                │  ✅ Complete permitido           │
                │  ❌ Reconfiguração bloqueada     │
                └──────────────────────────────────┘
```

#### Endpoints de Documentos

| Método | Endpoint | Descrição | Pré-condição | Quem usa |
|--------|----------|-----------|--------------|----------|
| POST | `/screening/{id}/steps/document-upload/configure` | Configura lista de documentos | `is_configured = false` | Gestor |
| GET | `/screening/{id}/documents` | Lista documentos da triagem | - | Ambos |
| POST | `/screening/{id}/documents/{doc_id}/upload` | Upload de arquivo | `is_configured = true` | Profissional/Gestor |
| POST | `/screening/{id}/documents/{doc_id}/reuse` | Reutiliza documento aprovado | `is_configured = true` | Profissional/Gestor |
| DELETE | `/screening/{id}/documents/{doc_id}` | Exclui documento da triagem | - | Profissional/Gestor |
| POST | `/screening/{id}/steps/document-upload/complete` | Finaliza etapa de upload | `is_configured = true` | Profissional/Gestor |
| POST | `/screening/{id}/documents/{doc_id}/review` | Revisa documento individual | - | Gestor |
| POST | `/screening/{id}/steps/document-review/complete` | Finaliza etapa de revisão | - | Gestor |
| POST | `/screening/{id}/finalize` | Finaliza triagem e promove documentos | - | Gestor |

#### Payload: Upload de Documento (Consolidado)

O endpoint de upload agora recebe o arquivo diretamente via `multipart/form-data`. O backend faz upload para o Firebase Storage e cria o `ProfessionalDocument` automaticamente:

```http
POST /screening/{id}/documents/{doc_id}/upload
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="diploma.pdf"
Content-Type: application/pdf

<binary file content>
--boundary
Content-Disposition: form-data; name="expires_at"

2027-12-31T23:59:59Z
--boundary
Content-Disposition: form-data; name="notes"

Documento original
--boundary--
```

**Campos (multipart/form-data):**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| file | binary | Sim | Arquivo do documento (PDF, JPEG, PNG, WebP, HEIC) |
| expires_at | datetime | Não | Data de validade (UTC) |
| notes | string | Não | Notas sobre o documento |

**Tipos de arquivo permitidos:**
- `application/pdf`
- `image/jpeg`
- `image/png`
- `image/webp`
- `image/heic`, `image/heif`

**Tamanho máximo:** 10 MB

**Comportamento:**
1. Backend faz upload do arquivo para Firebase Storage
2. Backend cria `ProfessionalDocument` automaticamente com `is_pending=True`
3. Backend infere `qualification_id` e `specialty_id` baseado na categoria do documento
4. Backend vincula ao `ScreeningDocument` e atualiza status para `PENDING_REVIEW`

#### Payload: Configurar Documentos

```json
POST /screening/{id}/steps/document-upload/configure

{
  "documents": [
    {
      "document_type_id": "uuid-rg",
      "is_required": true,
      "order": 1,
      "description": "Documento com foto legível"
    },
    {
      "document_type_id": "uuid-diploma",
      "is_required": true,
      "order": 2,
      "description": null
    },
    {
      "document_type_id": "uuid-comprovante-residencia",
      "is_required": false,
      "order": 3,
      "description": "Últimos 3 meses"
    }
  ]
}
```

**Observações:**
- O step deve estar com `is_configured = false` (ainda não configurado)
- Após configuração, `is_configured = true` e o step move para `IN_PROGRESS`
- **Reconfiguração NÃO é permitida**: chamar o endpoint novamente retorna erro `SCREENING_STEP_ALREADY_CONFIGURED`
- Para alterar a lista de documentos, é necessário criar uma nova triagem

**Validações:**
- Se `is_configured = true` → HTTP 409 Conflict com código `SCREENING_STEP_ALREADY_CONFIGURED`
- Se step não está em status `PENDING` ou `IN_PROGRESS` → HTTP 422

#### Response: DocumentUploadStepResponse

O schema de resposta do step de upload de documentos inclui:

```json
{
  "id": "uuid",
  "process_id": "uuid",
  "step_type": "DOCUMENT_UPLOAD",
  "order": 3,
  "status": "IN_PROGRESS",
  
  // Flag de configuração
  "is_configured": true,
  
  // Contadores
  "total_documents": 5,
  "required_documents": 3,
  "uploaded_documents": 2,
  
  // Propriedade computada (não persistida)
  // Indica se todos os documentos obrigatórios foram enviados
  // all_required_uploaded = uploaded_documents >= required_documents
  
  // Campos herdados do step base
  "assigned_to": "uuid-or-null",
  "review_notes": null,
  "rejection_reason": null,
  "started_at": "2026-02-01T10:00:00Z",
  "completed_at": null,
  "completed_by": null,
  "reviewed_at": null,
  "reviewed_by": null,
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-01T10:30:00Z"
}
```

**Campos importantes para o frontend:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `is_configured` | boolean | `false` = fase de configuração, `true` = fase de upload |
| `total_documents` | integer | Total de documentos configurados |
| `required_documents` | integer | Quantos são obrigatórios |
| `uploaded_documents` | integer | Quantos já foram enviados |

#### Obtendo Tipos de Documento Disponíveis

Os `document_type_id` utilizados na configuração **devem vir do endpoint de listagem de tipos de documento ativos**:

```
GET /document-types/all?is_active=true
```

**Fluxo no Frontend:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  1. Buscar tipos de documento disponíveis                                    │
│                                                                              │
│     GET /document-types/all?is_active=true                                   │
│                                                                              │
│     Response:                                                                │
│     [                                                                        │
│       { "id": "uuid-1", "name": "RG", "category": "PROFILE", ... },          │
│       { "id": "uuid-2", "name": "Diploma", "category": "QUALIFICATION", ...},│
│       { "id": "uuid-3", "name": "Certidão CRM", "category": "QUALIFICATION"},│
│       ...                                                                    │
│     ]                                                                        │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  2. Usuário seleciona quais documentos são necessários para esta triagem     │
│                                                                              │
│     Interface permite:                                                       │
│     • Selecionar tipos de documento da lista                                 │
│     • Marcar como obrigatório ou opcional                                    │
│     • Definir ordem de exibição                                              │
│     • Adicionar descrição/instruções customizadas                            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  3. Enviar configuração para a API                                           │
│                                                                              │
│     POST /screening/{id}/steps/document-upload/configure                     │
│     {                                                                        │
│       "documents": [                                                         │
│         { "document_type_id": "uuid-1", "is_required": true, "order": 1 },   │
│         { "document_type_id": "uuid-3", "is_required": true, "order": 2 },   │
│         ...                                                                  │
│       ]                                                                      │
│     }                                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Importante:**
- O endpoint `/document-types/all` retorna tipos de documento **visíveis na família da organização** (parent + children)
- Filtrar por `is_active=true` garante que apenas tipos ativos e válidos sejam exibidos
- O campo `category` (`PROFILE`, `QUALIFICATION`, `SPECIALTY`) pode ser usado para agrupar documentos na interface
- O campo `help_text` contém instruções para o profissional sobre como obter o documento
- O campo `validation_instructions` contém orientações para o revisor sobre como validar

#### Payload: Revisar Documento

```json
POST /screening/{id}/documents/{doc_id}/review

// Aprovação
{
  "status": "APPROVED",
  "notes": "Documento válido e legível"
}

// Rejeição
{
  "status": "REJECTED",
  "rejection_reason": "Documento ilegível, enviar foto com melhor qualidade"
}

// Alerta (escala para supervisor)
{
  "status": "ALERT",
  "alert_reason": "Documento com data de validade próxima do vencimento"
}
```

#### Rastreabilidade

Cada ação é registrada para auditoria:

- **ScreeningDocument.created_by**: Quem configurou o documento
- **ScreeningDocument.uploaded_by**: Quem fez o upload
- **ScreeningDocument.reviewed_by**: Quem revisou
- **ScreeningDocument.review_history**: Array JSONB com histórico completo

```json
// Exemplo de review_history
[
  {
    "user_id": "uuid",
    "action": "REJECTED",
    "notes": "Documento ilegível",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  {
    "user_id": "uuid",
    "action": "APPROVED",
    "notes": "Novo upload aceito",
    "timestamp": "2024-01-16T14:00:00Z"
  }
]
```

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
│   │   ├── enums.py                              # StepType, ScreeningStatus, AlertCategory, etc.
│   │   ├── document_type_config.py               # Configuração de tipos de documento
│   │   ├── organization_screening_settings.py   # Configurações por organização
│   │   ├── screening_process.py                  # Processo de triagem
│   │   ├── screening_document.py                 # Documento unificado
│   │   ├── screening_alert.py                    # Alertas de triagem
│   │   └── steps/
│   │       ├── __init__.py
│   │       ├── base_step.py                      # ScreeningStepMixin
│   │       ├── conversation_step.py
│   │       ├── professional_data_step.py
│   │       ├── document_upload_step.py
│   │       ├── document_review_step.py
│   │       ├── payment_info_step.py
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
