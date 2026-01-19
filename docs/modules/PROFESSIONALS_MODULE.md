# Módulo de Profissionais

## Visão Geral

O módulo de profissionais gerencia dados de profissionais de saúde (médicos, enfermeiros, técnicos, etc.), suas qualificações, especialidades, educação, documentos, empresas (PJ) e contas bancárias. Um profissional pode existir **antes** de ter uma conta na plataforma (pré-cadastro por gestores de escala).

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PROFISSIONAIS                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────┐      ┌─────────────────────┐      ┌───────────────────────────┐           │
│  │   User   │──0:1─│ ProfessionalProfile │──1:N─│ ProfessionalQualification │           │
│  └──────────┘      └─────────────────────┘      └───────────────────────────┘           │
│                              │                              │                           │
│                    ┌─────────┼─────────┬────────────────────┤                           │
│                   1:N       N:N       1:N                  1:N                          │
│                    │         │         │                    │                           │
│            ┌───────────┐  ┌──────────────────┐    ┌─────────┴─────────┐                 │
│            │  Bank     │  │ Professional     │    │                   │                 │
│            │  Account  │  │ Company          │    │   ┌────────────────┐  ┌───────────┐ │
│            └───────────┘  └──────────────────┘    │   │ Professional   │  │Professional│ │
│                  │                 │              │   │ Specialty      │  │ Education  │ │
│                  │                N:1             │   └────────────────┘  └───────────┘ │
│                  │                 │              │          │                          │
│                  │           ┌───────────┐        │         N:1                         │
│                  │           │  Company  │        │          │                          │
│                  │           └───────────┘        │    ┌───────────┐                    │
│                  │                 │              │    │ Specialty │                    │
│                  │                1:N             │    └───────────┘                    │
│                  │                 │              │                                     │
│                  └────────► ┌───────────┐ ◄───────┘                                     │
│                             │  Bank     │                                               │
│                             │  Account  │                                               │
│                             └───────────┘                                               │
│                                    │                                                    │
│                                   N:1                                                   │
│                                    │                                                    │
│                              ┌───────────┐                                              │
│                              │   Bank    │ (shared module)                              │
│                              └───────────┘                                              │
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

### DocumentType
Tipos de documentos que podem ser enviados.

| Valor | Categoria | Descrição |
|-------|-----------|-----------|
| ID_DOCUMENT | PROFILE | Documento oficial com foto (RG ou CNH) |
| CRIMINAL_RECORD | PROFILE | Antecedentes criminais |
| ADDRESS_PROOF | PROFILE | Comprovante de endereço |
| CV | PROFILE | Currículo |
| DIPLOMA | QUALIFICATION | Diploma de Medicina/Enfermagem/etc |
| CRM_REGISTRATION_CERTIFICATE | QUALIFICATION | Certidão de Regularidade de Inscrição |
| CRM_FINANCIAL_CERTIFICATE | QUALIFICATION | Certidão de Regularidade Financeira |
| CRM_ETHICS_CERTIFICATE | QUALIFICATION | Certidão Ética |
| RESIDENCY_CERTIFICATE | SPECIALTY | Certificado de Conclusão de Residência |
| SPECIALIST_TITLE | SPECIALTY | Título de Especialista da Sociedade |
| SBA_DIPLOMA | SPECIALTY | Diploma da SBA (anestesiologia) |
| OTHER | - | Outros documentos |

## Tabelas

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

### professional_profiles

Perfil do profissional de saúde.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ✅ | FK para users (null = pré-cadastro) |
| full_name | VARCHAR(255) | ❌ | Nome completo |
| email | VARCHAR(255) | ✅ | Email |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| cpf | VARCHAR(11) | ✅ | CPF (11 dígitos, unique) |
| birth_date | VARCHAR | ✅ | Data de nascimento (YYYY-MM-DD) |
| nationality | VARCHAR(100) | ✅ | Nacionalidade |
| gender | Gender | ✅ | Gênero |
| marital_status | MaritalStatus | ✅ | Estado civil |
| avatar_url | HttpUrl | ✅ | URL do avatar |
| **Endereço (AddressMixin)** | | | |
| address | VARCHAR(255) | ✅ | Logradouro |
| number | VARCHAR(20) | ✅ | Número |
| complement | VARCHAR(100) | ✅ | Complemento |
| neighborhood | VARCHAR(100) | ✅ | Bairro |
| city | VARCHAR(100) | ✅ | Cidade |
| state_code | VARCHAR(2) | ✅ | UF (2 chars) |
| state_name | VARCHAR(100) | ✅ | Nome do estado |
| postal_code | VARCHAR(10) | ✅ | CEP |
| latitude | FLOAT | ✅ | Latitude |
| longitude | FLOAT | ✅ | Longitude |
| **Status** | | | |
| profile_completed_at | TIMESTAMP | ✅ | Quando perfil foi completado |
| claimed_at | TIMESTAMP | ✅ | Quando perfil foi reivindicado |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users (quem verificou) |
| **Tracking (TrackingMixin)** | | | |
| created_by | UUID | ✅ | FK para users (quem criou) |
| updated_by | UUID | ✅ | FK para users (quem atualizou) |
| **Timestamps** | | | |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

**Constraints:**
- UNIQUE(user_id)
- UNIQUE(cpf)

### professional_qualifications

Qualificações/formações do profissional. Inclui registro no conselho.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| professional_id | UUID | ❌ | FK para professional_profiles |
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
- UNIQUE(professional_id, professional_type)

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
| professional_id | UUID | ❌ | FK para professional_profiles |
| qualification_id | UUID | ✅ | FK para professional_qualifications |
| specialty_id | UUID | ✅ | FK para professional_specialties |
| document_type | DocumentType | ❌ | Tipo do documento |
| document_category | DocumentCategory | ❌ | Categoria do documento |
| **Arquivo** | | | |
| file_url | HttpUrl | ❌ | URL do arquivo |
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

**Nota:** Múltiplas versões do mesmo tipo de documento podem existir. O documento válido atual é determinado por: `verified_at IS NOT NULL` + `(expires_at IS NULL OR expires_at > NOW())` + ordenado por `created_at DESC`.

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
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Endereço (AddressMixin)** | | | |
| address | VARCHAR(255) | ✅ | Logradouro |
| number | VARCHAR(20) | ✅ | Número |
| complement | VARCHAR(100) | ✅ | Complemento |
| neighborhood | VARCHAR(100) | ✅ | Bairro |
| city | VARCHAR(100) | ✅ | Cidade |
| state_code | VARCHAR(2) | ✅ | UF (2 chars) |
| state_name | VARCHAR(100) | ✅ | Nome do estado |
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
| professional_id | UUID | ❌ | FK para professional_profiles |
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
- UNIQUE(professional_id, company_id)

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
| professional_id | UUID | ✅ | FK para professional_profiles (XOR company_id) |
| company_id | UUID | ✅ | FK para companies (XOR professional_id) |
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
- CHECK: `(professional_id IS NOT NULL AND company_id IS NULL) OR (professional_id IS NULL AND company_id IS NOT NULL)`
- UNIQUE PARTIAL INDEX: `(professional_id) WHERE is_primary = true AND professional_id IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(company_id) WHERE is_primary = true AND company_id IS NOT NULL`
- UNIQUE(bank_id, agency, account_number, professional_id)
- UNIQUE(bank_id, agency, account_number, company_id)

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

### Pré-cadastro

1. Um profissional pode existir **sem** ter um usuário na plataforma (pré-cadastro por gestor)
2. O `user_id` é nullable para suportar pré-cadastros
3. O `created_by` indica quem criou o perfil (para pré-cadastros)
4. Quando o profissional criar conta, o sistema tenta vincular via `email` ou `cpf`
5. O campo `claimed_at` marca quando o profissional "reivindicou" seu perfil

### Qualificações e Conselhos

1. Uma qualificação representa uma formação profissional completa (Medicina, Enfermagem, etc.)
2. Cada qualificação possui **um único** registro de conselho
3. Um profissional pode ter múltiplas qualificações (raro, mas possível: médico + enfermeiro)
4. Especialidades e educação são vinculadas à qualificação, não diretamente ao perfil

### Documentos

1. Documentos **não têm soft delete** - múltiplas versões podem coexistir
2. Documentos de PROFILE: vinculados apenas ao professional_id
3. Documentos de QUALIFICATION: vinculados ao professional_id + qualification_id
4. Documentos de SPECIALTY: vinculados ao professional_id + specialty_id
5. Alguns documentos têm validade (ex: certidões do CRM) - usar `expires_at`
6. Documento válido = verificado + não expirado + mais recente

### Empresas e Contas Bancárias

1. Uma empresa (Company) pode ser compartilhada por múltiplos profissionais (sócios)
2. A relação ProfessionalCompany rastreia entrada/saída via `joined_at` e `left_at`
3. Contas bancárias podem pertencer diretamente ao profissional OU a uma empresa (nunca ambos)
4. Apenas **uma conta principal** (`is_primary=true`) por owner (constraint via partial unique index)
5. Os campos `is_active` permitem desativar empresas/contas sem removê-las
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
├── enums.py                      # Enums do módulo
├── specialty.py                  # Catálogo de especialidades
├── professional_profile.py       # Perfil do profissional
├── professional_qualification.py # Qualificações (com conselho)
├── professional_specialty.py     # Especialidades do profissional
├── professional_education.py     # Histórico educacional
├── professional_document.py      # Documentos do profissional
├── company.py                    # Empresas (PJ)
└── professional_company.py       # Junção profissional-empresa

src/shared/domain/models/
├── enums.py                      # AccountType, PixKeyType
├── bank.py                       # Catálogo de bancos
└── bank_account.py               # Contas bancárias
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | ProfessionalProfile |
| TrackingMixin | created_by, updated_by | ProfessionalProfile, Company, ProfessionalCompany, BankAccount |
| AddressMixin | address, number, complement, neighborhood, city, state_code, state_name, postal_code, latitude, longitude | ProfessionalProfile, Company |
| VerificationMixin | verified_at, verified_by | ProfessionalProfile, ProfessionalQualification, ProfessionalSpecialty, ProfessionalEducation, ProfessionalDocument, Company, BankAccount |
