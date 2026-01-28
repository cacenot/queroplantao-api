# Módulo de Profissionais

## Visão Geral

O módulo de profissionais gerencia dados de profissionais de saúde (médicos, enfermeiros, técnicos, etc.) **com escopo de organização (multi-tenant)**. Cada organização mantém seus próprios registros de profissionais, isolados de outras organizações. A mesma pessoa (por CPF) pode existir em múltiplas organizações com dados diferentes.

### Principais Funcionalidades

- **Multi-tenancy com escopo de família**: Profissionais compartilhados entre organizações pai/filhas
- **Versionamento de dados**: Histórico completo de alterações via Event Sourcing simplificado
- **Qualificações múltiplas**: Um profissional pode ter CRM + COREN, por exemplo
- **Especialidades com residência**: Tracking de status de residência (R1-R6, COMPLETED)
- **Documentos categorizados**: PROFILE, QUALIFICATION, SPECIALTY

## Versionamento de Dados (Event Sourcing)

O módulo implementa um sistema de versionamento simplificado para rastrear todas as alterações feitas nos dados do profissional.

### Conceito

1. **Toda alteração cria uma versão**: Ao modificar dados do profissional, uma nova `ProfessionalVersion` é criada
2. **Snapshot completo**: Cada versão contém todos os dados, não apenas os alterados
3. **Diffs calculados automaticamente**: O use case calcula as diferenças e popula `ProfessionalChangeDiff`
4. **Aplicação controlada**: A versão pode ser aplicada imediatamente ou aguardar aprovação
5. **Rastreabilidade**: `source_type` + `source_id` indicam a origem da alteração

### Fluxo de Versionamento

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           VERSIONAMENTO DE PROFISSIONAL                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────┐                                                           │
│  │ OrganizationProfessional │                                                           │
│  └──────────────────────────┘                                                           │
│              │                                                                          │
│             1:N                                                                         │
│              │                                                                          │
│              ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐        │
│  │                        professional_versions                                │        │
│  │                                                                             │        │
│  │  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐              │        │
│  │  │ Version 1 │ → │ Version 2 │ → │ Version 3 │ → │ Version 4 │ (is_current) │        │
│  │  │ SCREENING │   │  DIRECT   │   │ SCREENING │   │    API    │              │        │
│  │  └───────────┘   └───────────┘   └───────────┘   └───────────┘              │        │
│  │       │               │               │               │                     │        │
│  │      1:N             1:N             1:N             1:N                    │        │
│  │       │               │               │               │                     │        │
│  │       ▼               ▼               ▼               ▼                     │        │
│  │  ┌─────────────────────────────────────────────────────────────────┐        │        │
│  │  │                 professional_change_diffs                        │        │        │
│  │  │  (field_path, old_value, new_value, change_type)                │        │        │
│  │  └─────────────────────────────────────────────────────────────────┘        │        │
│  └─────────────────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PROFISSIONAIS                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────┐      ┌──────────────────────────┐                                 │
│  │   Organization   │──1:N─│ OrganizationProfessional │                                 │
│  └──────────────────┘      └──────────────────────────┘                                 │
│                                        │                                                │
│                    ┌───────────────────┼───────────────────┐                            │
│                   1:N                 1:N                 1:N                           │
│                    │                   │                   │                            │
│            ┌───────────────┐   ┌───────────────────────┐   │                            │
│            │    Bank       │   │ ProfessionalCompany   │   │                            │
│            │   Account     │   └───────────────────────┘   │                            │
│            └───────────────┘           │                   │                            │
│                    │                  N:1                  │                            │
│                   N:1                  │                   │                            │
│                    │             ┌───────────┐             │                            │
│              ┌───────────┐       │  Company  │             │                            │
│              │   Bank    │       └───────────┘             │                            │
│              └───────────┘             │                   │                            │
│                                       1:N                  │                            │
│                                        │                   │                            │
│                                  ┌───────────┐             │                            │
│                                  │   Bank    │             │                            │
│                                  │  Account  │             │                            │
│                                  └───────────┘             │                            │
│                                                            │                            │
│                            ┌───────────────────────────────┘                            │
│                            │                                                            │
│                    ┌───────────────────────────┐                                        │
│                    │ ProfessionalQualification │                                        │
│                    └───────────────────────────┘                                        │
│                               │         │                                               │
│                    ┌──────────┘         └──────────┐                                    │
│                   1:N                             1:N                                   │
│                    │                               │                                    │
│        ┌────────────────────┐          ┌───────────────────┐                            │
│        │ ProfessionalSpecialty│        │ProfessionalEducation│                          │
│        └────────────────────┘          └───────────────────┘                            │
│                  │                                                                      │
│                 N:1                                                                     │
│                  │                                                                      │
│           ┌───────────┐                                                                 │
│           │ Specialty │                                                                 │
│           └───────────┘                                                                 │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           DOCUMENTOS                                              │   │
│  │                                                                                   │   │
│  │  OrganizationProfessional ──1:N── ProfessionalDocument                            │   │
│  │                                         │                                         │   │
│  │                                ┌────────┴────────┐                                │   │
│  │                           (opcional)        (opcional)                            │   │
│  │                                │                 │                                │   │
│  │                   ProfessionalQualification  ProfessionalSpecialty                │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Enums

### CouncilType
Tipos de conselhos profissionais no Brasil.

| Valor | Descrição |
|-------|-----------|
| CRM | Conselho Regional de Medicina |
| COREN | Conselho Regional de Enfermagem |
| CRF | Conselho Regional de Farmácia |
| CRO | Conselho Regional de Odontologia |
| CREFITO | Conselho Regional de Fisioterapia e Terapia Ocupacional |
| CRP | Conselho Regional de Psicologia |
| CRN | Conselho Regional de Nutricionistas |
| CRBM | Conselho Regional de Biomedicina |
| OTHER | Outros conselhos |

### ProfessionalType
Tipos de profissionais de saúde.

| Valor | Descrição |
|-------|-----------|
| DOCTOR | Médico |
| NURSE | Enfermeiro |
| NURSING_TECH | Técnico de Enfermagem |
| PHARMACIST | Farmacêutico |
| DENTIST | Dentista |
| PHYSIOTHERAPIST | Fisioterapeuta |
| PSYCHOLOGIST | Psicólogo |
| NUTRITIONIST | Nutricionista |
| BIOMEDIC | Biomédico |
| OTHER | Outros |

### ResidencyStatus
Status de residência médica/multiprofissional.

| Valor | Descrição |
|-------|-----------|
| R1 | Primeiro ano |
| R2 | Segundo ano |
| R3 | Terceiro ano |
| R4 | Quarto ano |
| R5 | Quinto ano |
| R6 | Sexto ano (algumas especialidades) |
| COMPLETED | Concluída |

### Gender
Gênero do profissional.

| Valor | Descrição |
|-------|-----------|
| MALE | Masculino |
| FEMALE | Feminino |

### MaritalStatus
Estado civil.

| Valor | Descrição |
|-------|-----------|
| SINGLE | Solteiro(a) |
| MARRIED | Casado(a) |
| DIVORCED | Divorciado(a) |
| WIDOWED | Viúvo(a) |
| SEPARATED | Separado(a) |
| CIVIL_UNION | União estável |

### EducationLevel
Níveis de formação educacional.

| Valor | Descrição |
|-------|-----------|
| TECHNICAL | Curso técnico |
| UNDERGRADUATE | Graduação |
| SPECIALIZATION | Especialização / Pós-graduação lato sensu |
| MASTERS | Mestrado |
| DOCTORATE | Doutorado |
| POSTDOC | Pós-doutorado |
| COURSE | Curso livre / Capacitação |
| FELLOWSHIP | Fellowship |

### DocumentCategory
Categoria do documento baseada na entidade relacionada.

| Valor | Descrição |
|-------|-----------|
| PROFILE | Documentos pessoais do profissional |
| QUALIFICATION | Documentos da qualificação/conselho |
| SPECIALTY | Documentos da especialidade |

### DocumentType (Tabela)

> **Nota**: `DocumentType` é uma tabela configurável localizada em `src/shared/domain/models/document_type.py`. 
> Não é mais um enum - agora os tipos de documento são configuráveis por organização.

Os tipos padrão (seed) incluem:

| Código | Categoria | Nome | Requer Validade |
|--------|-----------|------|-----------------|
| ID_DOCUMENT | PROFILE | Documento de Identidade (RG ou CNH) | Não |
| PHOTO | PROFILE | Foto 3x4 | Não |
| CRIMINAL_RECORD | PROFILE | Certidão de Antecedentes Criminais | Sim (90 dias) |
| ADDRESS_PROOF | PROFILE | Comprovante de Endereço | Sim (90 dias) |
| CV | PROFILE | Currículo | Não |
| DIPLOMA | QUALIFICATION | Diploma de Graduação | Não |
| CRM_REGISTRATION_CERTIFICATE | QUALIFICATION | Certidão de Regularidade de Inscrição | Sim (30 dias) |
| CRM_FINANCIAL_CERTIFICATE | QUALIFICATION | Certidão de Regularidade Financeira | Sim (30 dias) |
| CRM_ETHICS_CERTIFICATE | QUALIFICATION | Certidão Ética | Sim (30 dias) |
| RESIDENCY_CERTIFICATE | SPECIALTY | Certificado de Conclusão de Residência | Não |
| SPECIALIST_TITLE | SPECIALTY | Título de Especialista | Não |
| SBA_DIPLOMA | SPECIALTY | Diploma da SBA (Anestesiologia) | Não |
| OTHER | PROFILE | Outro Documento | Não |

## Tabelas

### document_types

Tipos de documentos configuráveis. Compartilhado entre módulos (shared).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| code | VARCHAR(50) | ❌ | Código único do tipo (ex: CRM_REGISTRATION_CERTIFICATE) |
| name | VARCHAR(255) | ❌ | Nome em português (ex: Certidão de Regularidade) |
| category | DocumentCategory | ❌ | Categoria: PROFILE, QUALIFICATION, SPECIALTY |
| description | VARCHAR(500) | ✅ | Descrição breve |
| help_text | TEXT | ✅ | Instruções de como obter o documento |
| validation_instructions | TEXT | ✅ | Instruções para revisor validar |
| validation_url | VARCHAR(500) | ✅ | URL para validação online |
| requires_expiration | BOOLEAN | ❌ | Se requer data de validade |
| default_validity_days | INTEGER | ✅ | Validade padrão em dias |
| required_for_professional_types | JSONB | ✅ | Lista de ProfessionalType (null = todos) |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| display_order | INTEGER | ❌ | Ordem de exibição |
| organization_id | UUID | ✅ | FK para organizations (null = global) |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE: `(code, organization_id)` - Código único por organização

### specialties

Catálogo de especialidades médicas e de outras áreas da saúde.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| code | VARCHAR(20) | ❌ | Código do conselho (unique) |
| name | VARCHAR(100) | ❌ | Nome da especialidade |
| description | TEXT | ✅ | Descrição |
| professional_type | ProfessionalType | ❌ | Tipo de profissional |
| is_generalist | BOOLEAN | ❌ | Se é generalista |
| requires_residency | BOOLEAN | ❌ | Se requer residência |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

### organization_professionals

Profissionais vinculados a uma organização específica (multi-tenant).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (tenant isolation) |
| full_name | VARCHAR(255) | ❌ | Nome completo |
| email | VARCHAR(255) | ✅ | Email |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| cpf | VARCHAR(11) | ✅ | CPF (11 dígitos) |
| birth_date | VARCHAR | ✅ | Data de nascimento (YYYY-MM-DD) |
| nationality | VARCHAR(100) | ✅ | Nacionalidade |
| gender | Gender | ✅ | Gênero |
| marital_status | MaritalStatus | ✅ | Estado civil |
| avatar_url | VARCHAR(2048) | ✅ | URL do avatar |
| **Endereço (AddressMixin)** | | | |
| address | VARCHAR(255) | ✅ | Logradouro |
| number | VARCHAR(20) | ✅ | Número |
| complement | VARCHAR(100) | ✅ | Complemento |
| neighborhood | VARCHAR(100) | ✅ | Bairro |
| city | VARCHAR(100) | ✅ | Cidade |
| state_code | VARCHAR(2) | ✅ | UF (2 chars) |
| postal_code | VARCHAR(10) | ✅ | CEP |
| latitude | FLOAT | ✅ | Latitude |
| longitude | FLOAT | ✅ | Longitude |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| **Timestamps & Soft Delete** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(organization_id, cpf) WHERE cpf IS NOT NULL AND deleted_at IS NULL`
- UNIQUE PARTIAL INDEX: `(organization_id, email) WHERE email IS NOT NULL AND deleted_at IS NULL`

**Índices de Performance:**
- `ix_organization_professionals_organization_id` - busca por organização

### professional_qualifications

Qualificações/formações do profissional. Inclui registro no conselho.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_professional_id | UUID | ❌ | FK para organization_professionals |
| professional_type | ProfessionalType | ❌ | Tipo (DOCTOR, NURSE, etc.) |
| is_primary | BOOLEAN | ❌ | Se é a qualificação principal |
| graduation_year | INTEGER | ✅ | Ano de formatura |
| **Registro no Conselho** | | | |
| council_type | CouncilType | ❌ | Tipo de conselho (CRM, COREN, etc.) |
| council_number | VARCHAR(20) | ❌ | Número do registro |
| council_state | VARCHAR(2) | ❌ | UF do conselho |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(organization_professional_id, professional_type)

**Índices de Performance:**
- `ix_professional_qualifications_org_professional_id`

**Nota:** Uma qualificação agrupa conselho, especialidades e educação de uma formação específica. Ex: Um profissional com formação em Medicina e Enfermagem terá 2 qualificações.

### professional_specialties

Especialidades vinculadas a uma qualificação.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| qualification_id | UUID | ❌ | FK para professional_qualifications |
| specialty_id | UUID | ❌ | FK para specialties |
| is_primary | BOOLEAN | ❌ | Se é a especialidade principal |
| **RQE (para médicos)** | | | |
| rqe_number | VARCHAR(20) | ✅ | Número do RQE |
| rqe_state | VARCHAR(2) | ✅ | UF do RQE |
| **Residência** | | | |
| residency_status | ResidencyStatus | ❌ | Status da residência (default: COMPLETED) |
| residency_institution | VARCHAR(255) | ✅ | Instituição da residência |
| residency_expected_completion | VARCHAR | ✅ | Previsão de término (YYYY-MM-DD) |
| **Verificação (VerificationMixin)** | | | |
| certificate_url | VARCHAR(500) | ✅ | URL do certificado |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(qualification_id, specialty_id)

### professional_educations

Histórico educacional vinculado a uma qualificação.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| qualification_id | UUID | ❌ | FK para professional_qualifications |
| level | EducationLevel | ❌ | Nível (graduação, mestrado, etc.) |
| course_name | VARCHAR(255) | ❌ | Nome do curso |
| institution | VARCHAR(255) | ❌ | Instituição |
| start_year | INTEGER | ✅ | Ano de início |
| end_year | INTEGER | ✅ | Ano de conclusão |
| is_completed | BOOLEAN | ❌ | Se está concluído |
| workload_hours | INTEGER | ✅ | Carga horária (para cursos) |
| certificate_url | VARCHAR(500) | ✅ | URL do certificado/diploma |
| notes | TEXT | ✅ | Observações |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

### professional_documents

Documentos enviados pelo/para o profissional.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| document_type_id | UUID | ❌ | FK para document_types |
| organization_professional_id | UUID | ❌ | FK para organization_professionals |
| qualification_id | UUID | ✅ | FK para professional_qualifications |
| specialty_id | UUID | ✅ | FK para professional_specialties |
| **Arquivo** | | | |
| file_url | VARCHAR(2048) | ❌ | URL do arquivo |
| file_name | VARCHAR(255) | ❌ | Nome original do arquivo |
| file_size | INTEGER | ✅ | Tamanho em bytes |
| mime_type | VARCHAR(100) | ✅ | MIME type |
| **Validade** | | | |
| expires_at | TIMESTAMP | ✅ | Data de expiração (para docs com validade) |
| notes | TEXT | ✅ | Observações |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Nota:** Múltiplas versões do mesmo tipo de documento podem existir. O documento válido atual é determinado por: `verified_at IS NOT NULL` + `(expires_at IS NULL OR expires_at > NOW())` + ordenado por `created_at DESC`.

**Nota:** A categoria do documento (`PROFILE`, `QUALIFICATION`, `SPECIALTY`) é obtida via relacionamento com `document_types.category`.

### companies

Empresas (PJ) utilizadas pelos profissionais para contratação.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| cnpj | VARCHAR(14) | ❌ | CNPJ (14 dígitos, unique) |
| legal_name | VARCHAR(255) | ❌ | Razão Social |
| trade_name | VARCHAR(255) | ✅ | Nome Fantasia |
| state_registration | VARCHAR(30) | ✅ | Inscrição Estadual |
| municipal_registration | VARCHAR(30) | ✅ | Inscrição Municipal |
| email | VARCHAR(255) | ✅ | Email da empresa |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| **Endereço (AddressMixin)** | | | |
| address | VARCHAR(255) | ✅ | Logradouro |
| number | VARCHAR(20) | ✅ | Número |
| complement | VARCHAR(100) | ✅ | Complemento |
| neighborhood | VARCHAR(100) | ✅ | Bairro |
| city | VARCHAR(100) | ✅ | Cidade |
| state_code | VARCHAR(2) | ✅ | UF (2 chars) |
| postal_code | VARCHAR(10) | ✅ | CEP |
| latitude | FLOAT | ✅ | Latitude |
| longitude | FLOAT | ✅ | Longitude |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(cnpj)

### professional_companies

Associação N:N entre profissionais e empresas.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_professional_id | UUID | ❌ | FK para organization_professionals |
| company_id | UUID | ❌ | FK para companies |
| joined_at | TIMESTAMP | ❌ | Quando o profissional entrou na empresa |
| left_at | TIMESTAMP | ✅ | Quando o profissional saiu (null = ativo) |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(organization_professional_id, company_id)

### banks (shared module)

Catálogo de bancos brasileiros.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| code | VARCHAR(10) | ❌ | Código COMPE (ex: '001') |
| ispb_code | VARCHAR(8) | ✅ | Código ISPB (8 dígitos) |
| name | VARCHAR(255) | ❌ | Nome completo do banco |
| short_name | VARCHAR(50) | ✅ | Nome comercial curto |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(code)
- UNIQUE(ispb_code)

**Nota:** Esta tabela será populada via migration com todos os bancos ativos do BACEN.

### bank_accounts (shared module)

Contas bancárias para pagamentos.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| bank_id | UUID | ❌ | FK para banks |
| organization_professional_id | UUID | ✅ | FK para organization_professionals (XOR company_id) |
| company_id | UUID | ✅ | FK para companies (XOR organization_professional_id) |
| **Dados bancários** | | | |
| agency | VARCHAR(10) | ❌ | Número da agência |
| agency_digit | VARCHAR(2) | ✅ | Dígito da agência |
| account_number | VARCHAR(20) | ❌ | Número da conta |
| account_digit | VARCHAR(2) | ✅ | Dígito da conta |
| account_type | AccountType | ❌ | Tipo (CHECKING, SAVINGS) |
| holder_name | VARCHAR(255) | ❌ | Nome do titular |
| holder_document | VARCHAR(14) | ❌ | CPF ou CNPJ do titular |
| **PIX** | | | |
| pix_key_type | PixKeyType | ✅ | Tipo da chave PIX |
| pix_key | VARCHAR(255) | ✅ | Chave PIX |
| **Status** | | | |
| is_primary | BOOLEAN | ❌ | Se é a conta principal do owner |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- CHECK: `(organization_professional_id IS NOT NULL AND company_id IS NULL) OR (organization_professional_id IS NULL AND company_id IS NOT NULL)`
- UNIQUE PARTIAL INDEX: `(organization_professional_id) WHERE is_primary = true AND organization_professional_id IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(company_id) WHERE is_primary = true AND company_id IS NOT NULL`
- UNIQUE(bank_id, agency, account_number, organization_professional_id)
- UNIQUE(bank_id, agency, account_number, company_id)

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
      "is_primary": true,
      "specialties": [
        {
          "id": "uuid",
          "specialty_id": "uuid",
          "specialty_name": "Cardiologia",
          "is_primary": true,
          "rqe_number": "12345",
          "residency_status": "COMPLETED"
        }
      ],
      "educations": [
        {
          "id": "uuid",
          "level": "SPECIALIZATION",
          "course_name": "Residência em Cardiologia",
          "institution": "USP",
          "is_completed": true
        }
      ]
    }
  ],
  "companies": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "cnpj": "12345678000199",
      "razao_social": "Empresa Médica LTDA"
    }
  ],
  "bank_accounts": [
    {
      "id": "uuid",
      "bank_code": "001",
      "agency_number": "1234",
      "account_number": "123456",
      "account_holder_name": "João Silva",
      "account_holder_document": "12345678901",
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
- `qualifications[id=uuid].specialties[id=uuid]`
- `bank_accounts[0].pix_key`

**Índices:**
- `ix_professional_change_diffs_version_id`
- `ix_professional_change_diffs_field_path`
- `ix_professional_change_diffs_version_field (version_id, field_path)`

### Enums de Versionamento

#### SourceType
Origem de uma alteração nos dados do profissional.

| Valor | Descrição |
|-------|-----------|
| DIRECT | Alteração direta via API/admin |
| SCREENING | Alteração via processo de triagem |
| IMPORT | Importação em lote |
| API | Integração externa |

#### ChangeType
Tipo de mudança em um campo específico.

| Valor | Descrição |
|-------|-----------|
| ADDED | Campo/entidade adicionado |
| MODIFIED | Campo/entidade modificado |
| REMOVED | Campo/entidade removido |

### Enums Financeiros (shared module)

#### AccountType
| Valor | Descrição |
|-------|-----------|
| CHECKING | Conta Corrente |
| SAVINGS | Conta Poupança |

#### PixKeyType
| Valor | Descrição |
|-------|-----------|
| CPF | CPF do titular |
| CNPJ | CNPJ da empresa |
| EMAIL | E-mail |
| PHONE | Telefone celular |
| RANDOM | Chave aleatória (EVP) |

## Regras de Negócio

### Multi-Tenancy (Escopo de Família)

1. Profissionais são **compartilhados dentro da família** de organizações (pai + filhas/irmãs)
2. A mesma pessoa (CPF) **não pode** existir em múltiplas organizações da mesma família
3. `organization_id` indica qual organização criou o profissional
4. Unique constraints são validados no **escopo da família**: CPF, email e registro de conselho
5. Organizações de **famílias diferentes** não podem acessar profissionais umas das outras
6. Consultas usam `family_org_ids` do contexto de requisição para filtrar profissionais
7. Os `family_org_ids` são cacheados em Redis junto com os dados de organização

### Qualificações e Conselhos

1. Uma qualificação representa uma formação profissional completa (Medicina, Enfermagem, etc.)
2. Cada qualificação possui **um único** registro de conselho
3. Um profissional pode ter múltiplas qualificações (raro, mas possível: médico + enfermeiro)
4. Especialidades e educação são vinculadas à qualificação, não diretamente ao perfil

### Documentos

1. Documentos **não têm soft delete** - múltiplas versões podem coexistir
2. Documentos de PROFILE: vinculados apenas ao organization_professional_id
3. Documentos de QUALIFICATION: vinculados ao organization_professional_id + qualification_id
4. Documentos de SPECIALTY: vinculados ao organization_professional_id + specialty_id
5. Alguns documentos têm validade (ex: certidões do CRM) - usar `expires_at`
6. Documento válido = verificado + não expirado + mais recente

### Empresas e Contas Bancárias

1. Uma empresa (Company) pode ser compartilhada por múltiplos profissionais (sócios)
2. A relação ProfessionalCompany rastreia entrada/saída via `joined_at` e `left_at`
3. Contas bancárias podem pertencer diretamente ao profissional OU a uma empresa (nunca ambos)
4. Apenas **uma conta principal** (`is_primary=true`) por owner (constraint via partial unique index)
5. O campo `is_active` em bank_accounts permite desativar contas sem removê-las
6. A tabela `banks` é compartilhada e será populada via migration com os bancos do BACEN

### Verificação

1. Todas as entidades que podem ser verificadas usam o `VerificationMixin`
2. `verified_at` indica quando foi verificado
3. `verified_by` indica quem verificou (FK para users)
4. No futuro, um módulo de triagem gerenciará o fluxo de verificação

## Arquivos de Implementação

```
src/modules/professionals/domain/models/
├── __init__.py
├── enums.py                        # Enums do módulo
├── organization_professional.py    # Profissional por organização (multi-tenant)
├── professional_qualification.py   # Qualificações (com conselho)
├── professional_specialty.py       # Especialidades do profissional
├── professional_education.py       # Histórico educacional
├── professional_document.py        # Documentos do profissional
├── professional_company.py         # Junção profissional-empresa
├── professional_version.py         # Versionamento de dados (Event Sourcing)
├── professional_change_diff.py     # Diffs granulares de alterações
└── version_snapshot.py             # TypedDict para estrutura do data_snapshot

src/shared/domain/models/
├── enums.py                        # AccountType, PixKeyType
├── specialty.py                    # Catálogo de especialidades
├── company.py                      # Empresas (PJ)
├── bank.py                         # Catálogo de bancos
└── bank_account.py                 # Contas bancárias
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | OrganizationProfessional |
| TrackingMixin | created_by, updated_by | OrganizationProfessional, Company, ProfessionalCompany, BankAccount |
| AddressMixin | address, number, complement, neighborhood, city, state_code, postal_code, latitude, longitude | OrganizationProfessional, Company |
| VerificationMixin | verified_at, verified_by | OrganizationProfessional, ProfessionalQualification, ProfessionalSpecialty, ProfessionalEducation, ProfessionalDocument, Company, BankAccount |
