# Módulo de Contratos

## Visão Geral

O módulo de contratos gerencia dois tipos de relacionamentos contratuais:

1. **ClientContract (Contrato de Cliente)**: Contratos simples entre a organização e entidades externas (hospitais, municípios, etc.). Funciona como um "contrato pai" para rastrear onde os profissionais estão alocados.

2. **ProfessionalContract (Contrato Profissional)**: Contratos detalhados entre a organização e profissionais, com informações de valor hora, local de trabalho, dados bancários, workflow de assinatura, aditivos e rescisões.

O módulo é flexível: contratos profissionais podem ou não estar vinculados a um contrato de cliente.

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ESTRUTURA DE CONTRATOS                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────┐                                                                   │
│  │   Organization   │                                                                   │
│  └──────────────────┘                                                                   │
│          │                                                                              │
│         1:N                                                                             │
│          ▼                                                                              │
│  ┌──────────────────┐           ┌────────────────────────┐                              │
│  │  ClientContract  │◄─────────N│  ProfessionalContract  │                              │
│  │ (Contrato Pai)   │   (opt)   │  (Contrato Detalhado)  │                              │
│  └──────────────────┘           └────────────────────────┘                              │
│                                          │                                              │
│                                         1:N                                             │
│                          ┌───────────────┼───────────────┐                              │
│                          ▼               ▼               ▼                              │
│                  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐                      │
│                  │ContractAmend.│ │ContractDoc. │ │  (outros)    │                      │
│                  │  (Aditivo)   │ │  (Anexos)   │ │              │                      │
│                  └──────────────┘ └─────────────┘ └──────────────┘                      │
│                         │                                                               │
│                        1:N                                                              │
│                         ▼                                                               │
│                  ┌──────────────┐                                                       │
│                  │ContractDoc.  │ (anexo do aditivo)                                    │
│                  └──────────────┘                                                       │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           RELACIONAMENTOS                                        │   │
│  │                                                                                  │   │
│  │  ProfessionalContract ──N:1── OrganizationProfessional (profissional)            │   │
│  │  ProfessionalContract ──N:1── Unit (local de trabalho)                           │   │
│  │  ProfessionalContract ──N:1── Company (PJ do profissional) [opcional]            │   │
│  │  ProfessionalContract ──N:1── BankAccount (conta para pagamento) [opcional]      │   │
│  │  ProfessionalContract ──N:1── ClientContract (contrato pai) [opcional]           │   │
│  │                                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           WORKFLOW DE ASSINATURA                                 │   │
│  │                                                                                  │   │
│  │  submitted_at → professional_signed_at → organization_signed_at                  │   │
│  │                                                                                  │   │
│  │  Status: DRAFT → PENDING_SIGNATURES → ACTIVE → (SUSPENDED/TERMINATED/EXPIRED)    │   │
│  │                                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Enums

### ContractStatus
Status do contrato ao longo do ciclo de vida.

| Valor | Descrição |
|-------|-----------|
| DRAFT | Rascunho - contrato em elaboração |
| PENDING_SIGNATURES | Aguardando assinaturas |
| ACTIVE | Contrato ativo e em vigor |
| SUSPENDED | Contrato suspenso temporariamente |
| TERMINATED | Contrato rescindido/encerrado |
| EXPIRED | Contrato expirado (fim da vigência) |

## Tabelas

### client_contracts

Contratos com clientes externos (hospitais, municípios, etc.).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (multi-tenant) |
| client_name | VARCHAR(255) | ❌ | Nome do cliente |
| contract_number | VARCHAR(100) | ✅ | Número do contrato/licitação |
| description | VARCHAR(2000) | ✅ | Descrição e detalhes |
| status | ContractStatus | ❌ | Status do contrato |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| **Timestamps & Soft Delete** | | | |
| created_at, updated_at, deleted_at | TIMESTAMP | ✅* | |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(organization_id, contract_number) WHERE contract_number IS NOT NULL AND deleted_at IS NULL`

**Índices:**
- `ix_client_contracts_organization_id` - listagem por organização
- `ix_client_contracts_status` - filtro por status

### professional_contracts

Contratos entre a organização e profissionais.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_professional_id | UUID | ❌ | FK para organization_professionals |
| client_contract_id | UUID | ✅ | FK para client_contracts (contrato pai) |
| company_id | UUID | ✅ | FK para companies (PJ do profissional) |
| bank_account_id | UUID | ✅ | FK para bank_accounts (pagamento) |
| unit_id | UUID | ✅ | FK para units (local de trabalho) |
| contract_number | VARCHAR(100) | ✅ | Número do contrato |
| status | ContractStatus | ❌ | Status do contrato |
| **Termos Financeiros** | | | |
| hourly_rate | DECIMAL(10,2) | ✅ | Valor hora |
| currency | VARCHAR(3) | ❌ | Moeda (default: BRL) |
| **Período de Vigência** | | | |
| start_date | DATE | ✅ | Data de início |
| end_date | DATE | ✅ | Data de fim (NULL = indeterminado) |
| **Notas** | | | |
| notes | VARCHAR(2000) | ✅ | Observações adicionais |
| **Workflow de Assinatura** | | | |
| submitted_at | TIMESTAMP | ✅ | Quando enviado para assinatura |
| professional_signed_at | TIMESTAMP | ✅ | Quando profissional assinou |
| organization_signed_at | TIMESTAMP | ✅ | Quando organização assinou |
| **Rescisão** | | | |
| terminated_at | TIMESTAMP | ✅ | Quando foi rescindido |
| terminated_by | UUID | ✅ | Quem rescindiu |
| termination_reason | VARCHAR(2000) | ✅ | Motivo da rescisão |
| termination_notice_date | DATE | ✅ | Data do aviso de rescisão |
| **Tracking & Version** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| version | INTEGER | ❌ | Controle de concorrência |
| **Timestamps & Soft Delete** | | | |
| created_at, updated_at, deleted_at | TIMESTAMP | ✅* | |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(organization_professional_id, contract_number) WHERE contract_number IS NOT NULL AND deleted_at IS NULL`

**Índices:**
- `ix_professional_contracts_org_professional_id` - contratos por profissional
- `ix_professional_contracts_status` - filtro por status
- `ix_professional_contracts_client_contract_id` - contratos por cliente
- `ix_professional_contracts_unit_id` - contratos por unidade

### contract_amendments

Aditivos contratuais (modificações em contratos existentes).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| contract_id | UUID | ❌ | FK para professional_contracts |
| amendment_number | INTEGER | ❌ | Número sequencial do aditivo |
| description | VARCHAR(2000) | ❌ | Descrição do que foi alterado |
| previous_values | JSONB | ✅ | Snapshot dos valores anteriores |
| new_values | JSONB | ✅ | Snapshot dos novos valores |
| effective_from | DATE | ❌ | Data de vigência do aditivo |
| notes | VARCHAR(2000) | ✅ | Observações adicionais |
| **Workflow de Assinatura** | | | |
| professional_signed_at | TIMESTAMP | ✅ | Quando profissional assinou |
| organization_signed_at | TIMESTAMP | ✅ | Quando organização assinou |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| **Timestamps** | | | |
| created_at, updated_at | TIMESTAMP | | |

**Constraints:**
- UNIQUE: `(contract_id, amendment_number)`

**Índices:**
- `ix_contract_amendments_contract_id` - aditivos por contrato
- `ix_contract_amendments_effective_from` - filtro por data de vigência

### contract_documents

Documentos/anexos de contratos e aditivos.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| contract_id | UUID | ❌ | FK para professional_contracts |
| amendment_id | UUID | ✅ | FK para contract_amendments |
| file_url | VARCHAR(2048) | ❌ | URL do arquivo |
| file_name | VARCHAR(255) | ❌ | Nome original do arquivo |
| file_size | INTEGER | ✅ | Tamanho em bytes |
| mime_type | VARCHAR(100) | ✅ | Tipo MIME |
| notes | VARCHAR(1000) | ✅ | Observações |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users |
| **Timestamps** | | | |
| created_at, updated_at | TIMESTAMP | | |

**Índices:**
- `ix_contract_documents_contract_id` - documentos por contrato
- `ix_contract_documents_amendment_id` - documentos por aditivo

## Regras de Negócio

### Contratos de Cliente (ClientContract)

1. São contratos simples para rastrear relacionamentos com clientes externos
2. Não possuem datas de início/fim (por enquanto)
3. Múltiplos contratos profissionais podem referenciar o mesmo contrato de cliente
4. Útil para empresas terceirizadoras que prestam serviços a hospitais/municípios

### Contratos Profissionais (ProfessionalContract)

1. Sempre vinculado a um `organization_professional_id` (obrigatório)
2. Vínculo com `client_contract_id` é **opcional**
3. Pode ter empresa PJ do profissional (`company_id`) para contratos de prestação de serviço
4. Local de trabalho (`unit_id`) define onde o profissional atuará
5. Conta bancária (`bank_account_id`) para destino dos pagamentos

### Workflow de Assinatura

1. **DRAFT**: Contrato em elaboração (default)
2. Ao enviar para assinatura: `submitted_at` é preenchido, status → PENDING_SIGNATURES
3. Profissional assina: `professional_signed_at` preenchido
4. Organização assina: `organization_signed_at` preenchido
5. Ambos assinaram: status → ACTIVE
6. Properties `is_pending_signatures` e `is_fully_signed` auxiliam na verificação

### Rescisão de Contrato

1. Rescisão preenche: `terminated_at`, `terminated_by`, `termination_reason`
2. `termination_notice_date` registra quando o aviso foi dado
3. Status muda para TERMINATED
4. Não usa soft delete (`deleted_at`) para rescisões - são registros históricos

### Aditivos Contratuais (ContractAmendment)

1. Modificações em contratos existentes
2. Numeração sequencial por contrato (`amendment_number`)
3. `previous_values`/`new_values` armazenam snapshots em JSON para auditoria
4. `effective_from` define quando as alterações entram em vigor
5. Também possui workflow de assinatura próprio
6. Pode ter documentos anexos específicos do aditivo

### Versionamento

1. `VersionMixin` no ProfessionalContract para lock otimista
2. Evita conflitos de atualização concorrente
3. `version` é incrementado a cada update

## Arquivos de Implementação

```
src/modules/contracts/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── enums.py                  # ContractStatus
│       ├── client_contract.py        # ClientContract model
│       ├── professional_contract.py  # ProfessionalContract model
│       ├── contract_amendment.py     # ContractAmendment model
│       └── contract_document.py      # ContractDocument model
├── infrastructure/
│   ├── __init__.py
│   └── repositories/
│       └── __init__.py
├── presentation/
│   └── __init__.py
└── use_cases/
    └── __init__.py
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | ClientContract, ProfessionalContract |
| TrackingMixin | created_by, updated_by | ClientContract, ProfessionalContract, ContractAmendment |
| VersionMixin | version | ProfessionalContract |
| VerificationMixin | verified_at, verified_by | ContractAmendment, ContractDocument |

## Fluxos Principais

### Fluxo de Contrato Profissional

```
1. Criar contrato (status: DRAFT)
   - Vincular a OrganizationProfessional (obrigatório)
   - [Opcional] Vincular a ClientContract, Company, BankAccount, Unit
   - Definir termos (valor hora, datas)

2. Enviar para assinatura
   - submitted_at = now()
   - status = PENDING_SIGNATURES

3. Coleta de assinaturas
   - Profissional assina: professional_signed_at = now()
   - Organização assina: organization_signed_at = now()
   - Quando ambos assinarem: status = ACTIVE

4. Vida do contrato
   - Pode ser SUSPENDED temporariamente
   - Aditivos podem ser criados para modificações
   - Documentos podem ser anexados

5. Encerramento
   - TERMINATED: rescisão (preencher campos de termination)
   - EXPIRED: fim natural da vigência (end_date atingido)
```

### Fluxo de Aditivo Contratual

```
1. Criar aditivo vinculado ao contrato
   - amendment_number = próximo sequencial
   - Descrever alterações
   - Armazenar snapshots em previous_values/new_values
   - Definir effective_from

2. Coleta de assinaturas do aditivo
   - professional_signed_at
   - organization_signed_at

3. Verificação
   - verified_at, verified_by

4. Anexar documentos do aditivo
   - ContractDocument com amendment_id preenchido
```

### Fluxo de Terceirização

```
1. Terceirizadora ganha licitação
   - Criar ClientContract (cliente: Hospital/Município)

2. Contratar profissionais para o projeto
   - Criar ProfessionalContract
   - Vincular ao ClientContract
   - Definir Unit onde atuará

3. Gestão
   - Aditivos conforme necessário
   - Rescisões quando profissional sai do projeto
   - Novos contratos para novos profissionais
```
