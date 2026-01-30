# Screening (Triagem) - Frontend Implementation Guide

## Overview

O módulo de Triagem implementa um workflow de etapas para onboarding de profissionais de saúde:

1. **Conversa/Criação** - Identificação do profissional, atribuição, seleção de empresa contratante
2. **Coleta de Dados** - Dados pessoais, formação, especialidades, educação, empresa, conta bancária
3. **Coleta de Documentos** - Profissional envia os documentos (com versionamento)
4. **Verificação de Documentos** - Equipe analisa e aprova/rejeita documentos
5. **Revisão Superior** (opcional) - Para casos com alertas
6. **Validação do Cliente** (opcional) - Aprovação pela empresa contratante

## API Endpoints

### Base URLs

- **Authenticated**: `/api/v1/screenings`
- **Public (token-based)**: `/api/v1/public/screening/{token}`

### Screening Process (Triagem)

#### Create Screening (Etapa 1)
```http
POST /screenings
Content-Type: application/json
X-Organization-ID: {organization_id}

{
  "professional_cpf": "12345678901",
  "professional_name": "Dr. João Silva",
  "professional_phone": "+5511999999999",
  "expected_professional_type": "MEDICO",
  "expected_specialty_id": "uuid-of-specialty",
  "client_company_id": "uuid-of-client-company",
  "selected_document_type_ids": ["uuid-doc-type-1", "uuid-doc-type-2"]
}
```

#### List Screenings
```http
GET /screenings?page=1&size=20&status=IN_PROGRESS&assignee_id={uuid}
```

#### List My Screenings (assigned to me)
```http
GET /screenings/me?page=1&size=20
```

#### Get Single Screening
```http
GET /screenings/{screening_id}
```

#### Approve Screening
```http
POST /screenings/{screening_id}/approve
{
  "notes": "Aprovado após verificação completa"
}
```

#### Reject Screening
```http
POST /screenings/{screening_id}/reject
{
  "reason": "Documentação irregular"
}
```

#### Cancel Screening
```http
POST /screenings/{screening_id}/cancel?reason=Desistência%20do%20profissional
```

### Document Management (Etapas 2-4)

#### Select Required Documents (Etapa 2)
```http
POST /screenings/{screening_id}/documents
[
  {
    "document_type_config_id": "uuid-doc-type",
    "is_required": true,
    "notes": "Enviar frente e verso"
  },
  {
    "document_type_config_id": "uuid-doc-type-2",
    "professional_document_id": "uuid-existing-doc",  // Reutilizar documento existente
    "is_required": true
  }
]
```

#### Upload Document (Etapa 3)
```http
POST /screenings/{screening_id}/documents/{document_id}/upload
{
  "file_url": "https://storage.firebase.com/...",
  "file_name": "rg_frente.pdf",
  "expiration_date": "2025-12-31",
  "issuer": "SSP-SP"
}
```

#### Keep Existing Document
```http
POST /screenings/{screening_id}/documents/{document_id}/keep
?professional_document_id={uuid}
```

#### Review Document (Etapa 4)
```http
POST /screenings/{screening_id}/documents/{document_id}/review
{
  "status": "APPROVED",  // APPROVED, NEEDS_CHANGES, REJECTED, ALERT
  "notes": "Documento validado com sucesso"
}
```

#### Quick Actions
```http
POST /screenings/{screening_id}/documents/{document_id}/approve
POST /screenings/{screening_id}/documents/{document_id}/request-changes?notes=...
POST /screenings/{screening_id}/documents/{document_id}/reject?notes=...
```

### Step Navigation

#### Advance Step
```http
POST /screenings/{screening_id}/steps/{step_id}/complete
```

#### Go Back to Step
```http
POST /screenings/{screening_id}/steps/{step_id}/go-back
```

### Client Validation

#### Complete Validation
```http
POST /screenings/{screening_id}/client-validation/complete
{
  "outcome": "APPROVED",  // APPROVED, REJECTED, NEEDS_CHANGES
  "notes": "Aprovado pelo RH",
  "validated_by_name": "Maria Santos"
}
```

#### Skip Validation
```http
POST /screenings/{screening_id}/client-validation/skip?reason=Não%20aplicável
```

### Public Access (Token-based)

#### Get Screening by Token
```http
GET /public/screening/{token}
```

#### Upload Document via Token
```http
POST /public/screening/{token}/documents/{document_id}/upload
{
  "file_url": "https://storage.firebase.com/...",
  "file_name": "documento.pdf"
}
```

## Data Models

### ScreeningProcessResponse
```typescript
interface ScreeningProcessResponse {
  id: string;
  organization_id: string;
  professional_id: string;
  professional_cpf: string;
  professional_name: string;
  status: ScreeningStatus;
  current_step_type: StepType;
  configured_step_types: StepType[];
  
  // Assignment
  owner_id?: string;           // Responsável geral
  supervisor_id?: string;      // Supervisor responsável
  current_actor_id?: string;   // Responsável pela ação atual
  
  // Etapa 1 fields
  expected_professional_type?: string;
  expected_specialty_id?: string;
  client_company_id?: string;
  
  // Token access
  access_token: string;
  token_expires_at: string;
  
  // Relationships
  steps: ScreeningProcessStepResponse[];
  required_documents: ScreeningRequiredDocumentResponse[];
  
  // Timestamps
  created_at: string;
  updated_at: string;
  completed_at?: string;
}
```

### ScreeningStatus
```typescript
enum ScreeningStatus {
  IN_PROGRESS = "IN_PROGRESS", // Em andamento (qualquer etapa)
  APPROVED = "APPROVED",      // Aprovado e finalizado
  REJECTED = "REJECTED",      // Rejeitado
  EXPIRED = "EXPIRED",        // Expirado
  CANCELLED = "CANCELLED"     // Cancelado
}

// Estado detalhado é determinado pela combinação:
// status + current_step_type + step.status
```

### StepType
```typescript
enum StepType {
  CONVERSATION = "conversation",
  PROFESSIONAL_DATA = "professional_data",
  QUALIFICATION = "qualification",
  SPECIALTY = "specialty",
  EDUCATION = "education",
  COMPANY = "company",
  BANK_ACCOUNT = "bank_account",
  DOCUMENTS = "documents",
  DOCUMENT_REVIEW = "document_review",
  CLIENT_VALIDATION = "client_validation"
}
```

### DocumentReviewStatus
```typescript
enum DocumentReviewStatus {
  PENDING = "pending",
  APPROVED = "approved",
  NEEDS_CHANGES = "needs_changes",
  REJECTED = "rejected",
  ALERT = "alert"
}
```

## Frontend Implementation Notes

### 1. Step Navigation

O frontend deve:
- Mostrar breadcrumb/stepper com todas as etapas
- Destacar etapa atual (status: IN_PROGRESS)
- Permitir navegação para etapas anteriores concluídas
- Bloquear navegação para etapas futuras não liberadas

### 2. Document Upload Flow

```
1. Listar documentos requeridos (required_documents[])
2. Para cada documento:
   - Se professional_document_id existe e is_existing=true -> Mostrar "Manter documento existente"
   - Se is_uploaded=true -> Mostrar preview e opção de substituir
   - Se is_uploaded=false -> Mostrar botão de upload
3. Após upload, validar se todos os required=true estão uploaded
4. Liberar botão "Avançar" quando todos estiverem ok
```

### 3. Document Versioning

Quando um documento já existe do profissional:
```
┌─────────────────────────────────────────────┐
│ RG - Documento de Identidade                │
├─────────────────────────────────────────────┤
│ Documento existente encontrado              │
│ Enviado em: 15/01/2024 (versão 2)          │
│                                             │
│ [Manter atual]  [Enviar novo (v3)]         │
└─────────────────────────────────────────────┘
```

### 4. Document Review UI

Para a Etapa 4 (Verificação):
```
┌─────────────────────────────────────────────┐
│ RG - João Silva                    PENDENTE │
├─────────────────────────────────────────────┤
│ [Preview do documento]                      │
│                                             │
│ Link de validação: portal.gov.br/...        │
│                                             │
│ [✓ Aprovar] [↻ Solicitar alteração] [✗ Rejeitar]
│                                             │
│ Observações: [________________]             │
└─────────────────────────────────────────────┘
```

### 5. Token Link for Professionals

Gerar link para profissional completar upload:
```
https://app.queroplantao.com.br/triagem/{access_token}
```

O link:
- Expira em X horas (configurável por organização)
- Permite apenas upload de documentos
- Não requer login

### 7. Status Badge Colors

| Status | Color | Label |
|--------|-------|-------|
| PENDING | gray | Pendente |
| IN_PROGRESS | blue | Em andamento |
| AWAITING_APPROVAL | yellow | Aguardando aprovação |
| APPROVED | green | Aprovado |
| REJECTED | red | Rejeitado |
| CANCELLED | gray | Cancelado |

### 8. Organization Settings

Configurações afetam o workflow:
- `requires_client_company`: Obriga seleção de empresa contratante na Etapa 1
- `requires_client_validation_step`: Inclui etapa de validação do cliente no workflow
- `auto_approve_existing_documents`: Aprova automaticamente docs de triagens anteriores

## Error Handling

Todos os endpoints retornam erros no formato:
```json
{
  "code": "SCREENING_NOT_FOUND",
  "message": "Triagem não encontrada"
}
```

### Error Codes

| Code | HTTP | Descrição |
|------|------|-----------|
| `SCREENING_NOT_FOUND` | 404 | Triagem não encontrada |
| `SCREENING_STEP_NOT_FOUND` | 404 | Etapa não encontrada |
| `SCREENING_ALREADY_EXISTS` | 409 | Profissional já possui triagem ativa |
| `SCREENING_INVALID_STATUS` | 422 | Status não permite esta ação |
| `SCREENING_TOKEN_EXPIRED` | 401 | Token de acesso expirado |
| `DOCUMENT_NOT_UPLOADED` | 422 | Documento ainda não foi enviado |
| `DOCUMENT_ALREADY_REVIEWED` | 409 | Documento já foi revisado |
