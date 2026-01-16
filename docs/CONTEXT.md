# Quero Plantão - Documento de Contexto

## 1. Visão Geral do Sistema

**Quero Plantão** é uma plataforma SaaS para busca e publicação de vagas de plantões médicos. O sistema conecta médicos em busca de oportunidades de trabalho com gestores de escala de hospitais, clínicas e consultórios.

### 1.1 Analogias

- **Indeed/Glassdoor**: Busca e publicação de vagas
- **Uber**: Sistema de matching entre disponibilidade do médico e necessidade do gestor

---

## 2. Personas

### 2.1 Profissional de Saúde (Professional)
- Busca vagas de plantões
- Publica seus horários disponíveis (escala reversa)
- Bate ponto via geolocalização
- Visualiza recebimentos
- Pode atuar também como gestor
- Tipos: Médico, Enfermeiro, Técnico de Enfermagem, etc.

### 2.2 Gestor de Escala (Scale Manager)
- Gerencia escalas de plantões
- Cria plantões com horários, valores e especialidades
- Publica anúncios de vagas
- Controla entrada/saída dos médicos
- Visualiza pagamentos devidos

---

## 3. Conceitos do Domínio

### 3.1 Hierarquia Organizacional

```
Organização (Organization)
    └── Unidade (Unit) - Ex: Hospital X, Clínica Y, Ala Sul
            └── Setor (Sector) - Ex: UTI, Sala de Emergência, Cardiologia
                    └── Escala (Schedule)
                            └── Plantão (Shift)
                                    └── Anúncio de Vaga (Job Posting)
```

### 3.2 Definições

| Termo | Descrição |
|-------|-----------|
| **Organization** | Entidade principal (hospital, rede de clínicas, etc.) |
| **Unit** | Local físico dentro da organização (filial, ala, prédio) |
| **Sector** | Subdivisão da unidade (sala, especialidade, departamento) |
| **Schedule** | Agenda de plantões de um setor específico |
| **Shift** | Plantão individual com horário, valor e especialidade |
| **Job Posting** | Anúncio público de vaga derivado de um plantão |
| **Availability** | Horários disponíveis informados pelo médico (escala reversa) |
| **Time Record** | Registro de ponto (entrada/saída) com geolocalização |

---

## 4. Modelagem de Dados

### 4.1 Diagrama ER (Conceitual)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AUTENTICAÇÃO & PERMISSÕES                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────┐      ┌──────────────────┐      ┌──────────┐      ┌───────────────────┐   │
│  │   User   │──N:N─│   user_roles     │──N:1─│   Role   │──1:N─│ role_permissions  │   │
│  └──────────┘      └──────────────────┘      └──────────┘      └───────────────────┘   │
│       │                                                                │               │
│       │            ┌──────────────────────┐                            │               │
│       └─────N:N────│  user_permissions    │──N:1───────────────────────┘               │
│                    └──────────────────────┘                     ┌────────────┐         │
│                                                                 │ Permission │         │
│                                                                 └────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ESTRUTURA ORGANIZACIONAL                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────┐      ┌──────────┐      ┌──────────┐      ┌────────────┐               │
│  │ Organization │──1:N─│   Unit   │──1:N─│  Sector  │──1:N─│  Schedule  │               │
│  └──────────────┘      └──────────┘      └──────────┘      └────────────┘               │
│         │                   │                 │                   │                     │
│         │                   │                 │                   │                     │
│         └───────────────────┴────────N:N──────┴───────────────────┘                     │
│                                       │                                                 │
│                              ┌─────────────────┐                                        │
│                              │ OrganizationUser│ (membership com role context)          │
│                              └─────────────────┘                                        │
│                                       │                                                 │
│                                      N:1                                                │
│                                       │                                                 │
│                                  ┌──────────┐                                           │
│                                  │   User   │                                           │
│                                  └──────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PLANTÕES & VAGAS                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌────────────┐      ┌─────────┐      ┌─────────────┐                                   │
│  │  Schedule  │──1:N─│  Shift  │──0:1─│ Job Posting │                                   │
│  └────────────┘      └─────────┘      └─────────────┘                                   │
│                           │                  │                                          │
│                          1:N                N:N                                         │
│                           │                  │                                          │
│                    ┌─────────────┐    ┌──────────────────┐                              │
│                    │ Time Record │    │ Job Application  │                              │
│                    └─────────────┘    └──────────────────┘                              │
│                           │                  │                                          │
│                          N:1                N:1                                         │
│                           │                  │                                          │
│                           └────────┬─────────┘                                          │
│                                    │                                                    │
│                             ┌──────────────┐                                            │
│                             │ Professional │ (pode existir sem User)                    │
│                             └──────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MATCHING & DISPONIBILIDADE                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐                            │
│  │ Professional │──1:N─│ Availability │──N:N─│ Job Posting │──> Match Score             │
│  └──────────────┘      └──────────────┘      └─────────────┘                            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Esquema de Tabelas

#### 4.2.1 Módulo de Autenticação e Autorização

```sql
-- Usuários (dados complementares ao Firebase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP -- soft delete
);

-- Permissões disponíveis no sistema
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL, -- Ex: 'shift:create', 'schedule:view'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL, -- Ex: 'shifts', 'schedules', 'users'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles do sistema
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL, -- Ex: 'doctor', 'manager', 'admin'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE, -- roles do sistema não podem ser deletadas
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissões de cada Role (1:N)
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- Roles do usuário (N:N)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id), -- NULL quando auto-atribuição (ex: cadastro inicial)
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- opcional: role temporária
    UNIQUE(user_id, role_id)
);
-- NOTA: granted_by é nullable para suportar:
--   1. Auto-cadastro: usuário cria conta e recebe role padrão automaticamente
--   2. Migrações: roles importadas de sistemas legados
--   3. Sistema: roles atribuídas por processos automatizados

-- Permissões standalone do usuário (N:N)
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(user_id, permission_id)
);
```

#### 4.2.2 Módulo de Profissionais

```sql
-- Tipos de conselhos profissionais
CREATE TYPE council_type AS ENUM (
    'CRM',   -- Conselho Regional de Medicina
    'COREN', -- Conselho Regional de Enfermagem
    'CRF',   -- Conselho Regional de Farmácia
    'CRO',   -- Conselho Regional de Odontologia
    'CREFITO', -- Conselho Regional de Fisioterapia e Terapia Ocupacional
    'CRP',   -- Conselho Regional de Psicologia
    'CRN',   -- Conselho Regional de Nutricionistas
    'CRBM',  -- Conselho Regional de Biomedicina
    'OTHER'  -- Outros conselhos
);

-- Tipos de profissionais
CREATE TYPE professional_type AS ENUM (
    'DOCTOR',           -- Médico
    'NURSE',            -- Enfermeiro
    'NURSING_TECH',     -- Técnico de Enfermagem
    'PHARMACIST',       -- Farmacêutico
    'DENTIST',          -- Dentista
    'PHYSIOTHERAPIST',  -- Fisioterapeuta
    'PSYCHOLOGIST',     -- Psicólogo
    'NUTRITIONIST',     -- Nutricionista
    'BIOMEDIC',         -- Biomédico
    'OTHER'             -- Outros
);

-- Status de residência médica
CREATE TYPE residency_status AS ENUM (
    'NOT_APPLICABLE', -- Não se aplica (não é médico ou já concluiu)
    'NOT_STARTED',    -- Ainda não iniciou
    'R1',             -- Primeiro ano
    'R2',             -- Segundo ano
    'R3',             -- Terceiro ano
    'R4',             -- Quarto ano
    'R5',             -- Quinto ano
    'R6',             -- Sexto ano (algumas especialidades)
    'COMPLETED'       -- Concluída
);

-- Especialidades (médicas e de outras áreas da saúde)
CREATE TABLE specialties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL, -- Código do conselho (ex: código CFM para médicos)
    name VARCHAR(100) NOT NULL,
    description TEXT,
    professional_type professional_type NOT NULL, -- Tipo de profissional que pode ter essa especialidade
    is_generalist BOOLEAN DEFAULT FALSE, -- TRUE para "Clínico Geral", "Enfermeiro Generalista", etc.
    requires_residency BOOLEAN DEFAULT FALSE, -- Se requer residência/especialização
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Perfil do profissional
-- NOTA: user_id é nullable para permitir pré-cadastro por escalistas
-- O profissional pode existir antes de ter uma conta na plataforma
CREATE TABLE professional_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE SET NULL, -- NULL = pré-cadastro
    
    -- Tipo de profissional
    professional_type professional_type NOT NULL,
    
    -- Dados pessoais (necessários mesmo sem user)
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    cpf VARCHAR(14) UNIQUE, -- CPF formatado ou não
    birth_date DATE,
    gender VARCHAR(20), -- 'male', 'female', 'other', 'prefer_not_to_say'
    marital_status VARCHAR(20), -- 'single', 'married', 'divorced', 'widowed', 'other'
    avatar_url TEXT,
    
    -- Endereço do profissional
    street VARCHAR(255),
    number VARCHAR(20),
    complement VARCHAR(100),
    neighborhood VARCHAR(100),
    city VARCHAR(100),
    state CHAR(2),
    postal_code VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Dados profissionais
    graduation_year INTEGER,
    bio TEXT,
    hourly_rate_min DECIMAL(10,2), -- Pretensão mínima por hora
    hourly_rate_max DECIMAL(10,2), -- Pretensão máxima por hora
    is_available BOOLEAN DEFAULT TRUE, -- Está aceitando propostas
    
    -- Status do perfil
    profile_completed_at TIMESTAMP,
    verified_at TIMESTAMP, -- Verificação de documentos
    
    -- Quem cadastrou (para pré-cadastros)
    created_by UUID REFERENCES users(id),
    claimed_at TIMESTAMP, -- Quando o profissional "reivindicou" o perfil
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Registros em conselhos profissionais (CRM, COREN, etc.)
-- Um profissional pode ter múltiplos registros (ex: CRM em 2 estados, ou CRM + COREN)
CREATE TABLE professional_councils (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    council_type council_type NOT NULL, -- CRM, COREN, etc.
    council_number VARCHAR(20) NOT NULL, -- Número do registro
    council_state CHAR(2) NOT NULL, -- UF do conselho
    
    -- Validação
    is_primary BOOLEAN DEFAULT FALSE, -- Registro principal
    verified_at TIMESTAMP, -- Verificação do registro
    verification_url TEXT, -- Link para comprovante
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    suspended_at TIMESTAMP,
    suspension_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(council_type, council_number, council_state)
);

-- Especialidades do profissional (N:N)
CREATE TABLE professional_specialties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    specialty_id UUID NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    
    is_primary BOOLEAN DEFAULT FALSE, -- Especialidade principal
    
    -- RQE (Registro de Qualificação de Especialista) - específico para médicos
    rqe_number VARCHAR(20),
    rqe_state CHAR(2),
    rqe_verified_at TIMESTAMP,
    
    -- Status de residência (para quem ainda está em formação)
    residency_status residency_status DEFAULT 'NOT_APPLICABLE',
    residency_institution VARCHAR(255), -- Onde está fazendo residência
    residency_expected_completion DATE, -- Previsão de término
    
    -- Comprovantes
    certificate_url TEXT,
    verified_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(professional_id, specialty_id)
);

-- Índices para busca de profissionais
CREATE INDEX idx_professional_profiles_type ON professional_profiles(professional_type);
CREATE INDEX idx_professional_profiles_city_state ON professional_profiles(city, state);
CREATE INDEX idx_professional_profiles_cpf ON professional_profiles(cpf) WHERE cpf IS NOT NULL;
CREATE INDEX idx_professional_profiles_email ON professional_profiles(email) WHERE email IS NOT NULL;
CREATE INDEX idx_professional_councils_number ON professional_councils(council_type, council_number, council_state);
CREATE INDEX idx_professional_specialties_specialty ON professional_specialties(specialty_id);
```

#### 4.2.3 Módulo Organizacional

```sql
-- Organizações (hospitais, redes de clínicas, etc.)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255), -- Nome fantasia
    document_type VARCHAR(10) NOT NULL DEFAULT 'CNPJ', -- CNPJ, CPF
    document_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    website VARCHAR(255),
    logo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Endereços das organizações
CREATE TABLE organization_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    label VARCHAR(100), -- Ex: "Sede", "Filial Centro"
    street VARCHAR(255) NOT NULL,
    number VARCHAR(20),
    complement VARCHAR(100),
    neighborhood VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    country VARCHAR(50) DEFAULT 'Brasil',
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unidades (locais físicos: Ala Sul, Hospital X, Filial Y)
CREATE TABLE units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50), -- Código interno
    description TEXT,
    
    -- Endereço da unidade
    street VARCHAR(255),
    number VARCHAR(20),
    complement VARCHAR(100),
    neighborhood VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    postal_code VARCHAR(10),
    
    -- Geolocalização para ponto
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geofence_radius_meters INTEGER DEFAULT 200, -- Raio para bater ponto
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Setores (subdivisões das unidades: UTI, Sala de Emergência, etc.)
CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    
    -- Geolocalização específica do setor (opcional, herda da unit se não definido)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geofence_radius_meters INTEGER,
    
    -- Especialidade padrão do setor (opcional)
    default_specialty_id UUID REFERENCES specialties(id),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Membros da organização (usuários vinculados)
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'owner', 'admin', 'manager', 'viewer'
    
    -- Permissões específicas por contexto
    can_manage_units BOOLEAN DEFAULT FALSE,
    can_manage_sectors BOOLEAN DEFAULT FALSE,
    can_manage_schedules BOOLEAN DEFAULT FALSE,
    can_manage_shifts BOOLEAN DEFAULT FALSE,
    can_manage_members BOOLEAN DEFAULT FALSE,
    can_view_financials BOOLEAN DEFAULT FALSE,
    can_publish_jobs BOOLEAN DEFAULT FALSE,
    
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);

-- Acesso de membros a unidades específicas
CREATE TABLE member_unit_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES organization_members(id) ON DELETE CASCADE,
    unit_id UUID NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'full', -- 'full', 'view_only'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(member_id, unit_id)
);

-- Acesso de membros a setores específicos
CREATE TABLE member_sector_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES organization_members(id) ON DELETE CASCADE,
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'full',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(member_id, sector_id)
);
```

#### 4.2.4 Módulo de Escalas e Plantões

```sql
-- Escalas (agendas de plantões)
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configurações padrão
    default_specialty_id UUID REFERENCES specialties(id),
    default_hourly_rate DECIMAL(10,2),
    
    -- Período de vigência
    start_date DATE,
    end_date DATE,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Plantões (shifts individuais)
CREATE TABLE shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES schedules(id) ON DELETE SET NULL, -- Pode ser NULL (plantão avulso)
    
    -- Referência direta ao setor (para plantões avulsos)
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    
    -- Dados do plantão
    title VARCHAR(255),
    description TEXT,
    specialty_id UUID NOT NULL REFERENCES specialties(id),
    
    -- Horários
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Recorrência (opcional)
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule TEXT, -- RRULE format (RFC 5545)
    recurrence_end_date DATE,
    parent_shift_id UUID REFERENCES shifts(id), -- Para instâncias de recorrência
    
    -- Valores
    hourly_rate DECIMAL(10,2) NOT NULL,
    fixed_rate DECIMAL(10,2), -- Valor fixo alternativo
    payment_type VARCHAR(20) DEFAULT 'hourly', -- 'hourly', 'fixed'
    
    -- Status
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'assigned', 'in_progress', 'completed', 'cancelled'
    
    -- Profissional atribuído
    assigned_professional_id UUID REFERENCES professional_profiles(id),
    assigned_at TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    
    -- Metadados
    notes TEXT,
    requirements TEXT, -- Requisitos específicos
    
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Índices para busca de plantões
CREATE INDEX idx_shifts_date ON shifts(shift_date);
CREATE INDEX idx_shifts_specialty ON shifts(specialty_id);
CREATE INDEX idx_shifts_status ON shifts(status);
CREATE INDEX idx_shifts_sector ON shifts(sector_id);
```

#### 4.2.5 Módulo de Vagas (Job Postings)

```sql
-- Anúncios de vagas
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Pode estar vinculado a um plantão ou ser avulso
    shift_id UUID REFERENCES shifts(id) ON DELETE SET NULL,
    
    -- Dados da organização (denormalizados para busca)
    organization_id UUID NOT NULL REFERENCES organizations(id),
    unit_id UUID NOT NULL REFERENCES units(id),
    sector_id UUID REFERENCES sectors(id),
    
    -- Dados da vaga
    title VARCHAR(255) NOT NULL,
    description TEXT,
    specialty_id UUID NOT NULL REFERENCES specialties(id),
    
    -- Localização (denormalizado para busca)
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    neighborhood VARCHAR(100),
    
    -- Horários
    shift_date DATE,
    start_time TIME,
    end_time TIME,
    
    -- Recorrência para vagas recorrentes
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern JSONB, -- Dias da semana, frequência, etc.
    
    -- Valores
    hourly_rate DECIMAL(10,2),
    fixed_rate DECIMAL(10,2),
    payment_type VARCHAR(20) DEFAULT 'hourly',
    show_rate BOOLEAN DEFAULT TRUE, -- Exibir valor no anúncio
    
    -- Requisitos
    min_experience_years INTEGER,
    requirements TEXT,
    benefits TEXT,
    
    -- Status e visibilidade
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'paused', 'filled', 'expired', 'cancelled'
    is_featured BOOLEAN DEFAULT FALSE, -- Destaque (monetização)
    is_urgent BOOLEAN DEFAULT FALSE,
    
    -- Período de publicação
    published_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Contadores
    views_count INTEGER DEFAULT 0,
    applications_count INTEGER DEFAULT 0,
    
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Índices para busca de vagas
CREATE INDEX idx_job_postings_specialty ON job_postings(specialty_id);
CREATE INDEX idx_job_postings_city_state ON job_postings(city, state);
CREATE INDEX idx_job_postings_status ON job_postings(status);
CREATE INDEX idx_job_postings_date ON job_postings(shift_date);
CREATE INDEX idx_job_postings_published ON job_postings(published_at) WHERE status = 'published';

-- Candidaturas
CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Status da candidatura
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'viewed', 'shortlisted', 'accepted', 'rejected', 'withdrawn'
    
    -- Proposta do profissional (se diferente do anunciado)
    proposed_hourly_rate DECIMAL(10,2),
    cover_letter TEXT,
    
    -- Histórico de status
    viewed_at TIMESTAMP,
    shortlisted_at TIMESTAMP,
    accepted_at TIMESTAMP,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_posting_id, professional_id)
);
```

#### 4.2.6 Módulo de Disponibilidade (Escala Reversa)

```sql
-- Disponibilidade do profissional (escala reversa)
CREATE TABLE professional_availabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Tipo de disponibilidade
    availability_type VARCHAR(20) DEFAULT 'available', -- 'available', 'preferred', 'unavailable'
    
    -- Data/hora
    date DATE, -- NULL para recorrente
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Recorrência
    is_recurring BOOLEAN DEFAULT FALSE,
    day_of_week INTEGER, -- 0-6 (domingo-sábado) para recorrentes
    recurrence_start_date DATE,
    recurrence_end_date DATE,
    
    -- Preferências
    preferred_specialties UUID[], -- Array de specialty_ids
    preferred_cities TEXT[], -- Array de cidades
    preferred_states CHAR(2)[], -- Array de UFs
    min_hourly_rate DECIMAL(10,2),
    max_distance_km INTEGER, -- Distância máxima do endereço
    
    notes TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para matching
CREATE INDEX idx_availabilities_professional ON professional_availabilities(professional_id);
CREATE INDEX idx_availabilities_date ON professional_availabilities(date);
CREATE INDEX idx_availabilities_day_of_week ON professional_availabilities(day_of_week) WHERE is_recurring = TRUE;
```

#### 4.2.7 Módulo de Ponto e Pagamentos

```sql
-- Registro de ponto (time records)
CREATE TABLE time_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_id UUID NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Check-in
    check_in_at TIMESTAMP,
    check_in_latitude DECIMAL(10, 8),
    check_in_longitude DECIMAL(11, 8),
    check_in_accuracy_meters DECIMAL(10,2),
    check_in_method VARCHAR(20), -- 'gps', 'manual', 'qrcode'
    check_in_validated BOOLEAN DEFAULT FALSE,
    check_in_notes TEXT,
    
    -- Check-out
    check_out_at TIMESTAMP,
    check_out_latitude DECIMAL(10, 8),
    check_out_longitude DECIMAL(11, 8),
    check_out_accuracy_meters DECIMAL(10,2),
    check_out_method VARCHAR(20),
    check_out_validated BOOLEAN DEFAULT FALSE,
    check_out_notes TEXT,
    
    -- Cálculos
    worked_minutes INTEGER, -- Calculado: check_out - check_in
    expected_minutes INTEGER, -- Do plantão
    hourly_rate DECIMAL(10,2) NOT NULL, -- Snapshot do valor
    
    -- Valores calculados
    calculated_amount DECIMAL(10,2), -- (worked_minutes / 60) * hourly_rate
    adjustments DECIMAL(10,2) DEFAULT 0, -- Ajustes manuais
    final_amount DECIMAL(10,2), -- calculated_amount + adjustments
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'disputed', 'paid'
    
    -- Aprovação
    approved_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    
    -- Disputas
    dispute_reason TEXT,
    dispute_resolved_at TIMESTAMP,
    dispute_resolved_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Histórico de ajustes no ponto
CREATE TABLE time_record_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    time_record_id UUID NOT NULL REFERENCES time_records(id) ON DELETE CASCADE,
    
    adjustment_type VARCHAR(20) NOT NULL, -- 'check_in', 'check_out', 'amount', 'status'
    old_value TEXT,
    new_value TEXT,
    reason TEXT NOT NULL,
    
    adjusted_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumo de pagamentos (para relatórios)
CREATE TABLE payment_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Período
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Contexto
    organization_id UUID NOT NULL REFERENCES organizations(id),
    professional_id UUID REFERENCES professional_profiles(id), -- NULL para resumo geral
    unit_id UUID REFERENCES units(id),
    sector_id UUID REFERENCES sectors(id),
    
    -- Totais
    total_shifts INTEGER DEFAULT 0,
    total_hours DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'paid'
    
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.8 Módulo de Matching (Monetização)

```sql
-- Matches entre disponibilidade e vagas
CREATE TABLE availability_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_availability_id UUID NOT NULL REFERENCES professional_availabilities(id) ON DELETE CASCADE,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    
    -- Score de matching (0-100)
    match_score INTEGER NOT NULL,
    
    -- Fatores do score
    time_match_score INTEGER, -- Compatibilidade de horário
    specialty_match_score INTEGER, -- Especialidade
    location_match_score INTEGER, -- Proximidade
    rate_match_score INTEGER, -- Valor compatível
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'notified', 'viewed', 'applied', 'dismissed'
    
    notified_at TIMESTAMP,
    viewed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(professional_availability_id, job_posting_id)
);

-- Planos de assinatura
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Preços
    monthly_price DECIMAL(10,2),
    yearly_price DECIMAL(10,2),
    
    -- Limites
    max_job_postings INTEGER, -- Por mês
    max_matches_per_month INTEGER, -- Matches visíveis
    featured_postings_included INTEGER,
    
    -- Features
    features JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assinaturas de organizações
CREATE TABLE organization_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'cancelled', 'expired', 'suspended'
    
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Billing
    billing_cycle VARCHAR(20), -- 'monthly', 'yearly'
    next_billing_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créditos para matches (monetização por uso)
CREATE TABLE match_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    credits_purchased INTEGER NOT NULL,
    credits_used INTEGER DEFAULT 0,
    credits_remaining INTEGER NOT NULL,
    
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Referência de pagamento
    payment_reference VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.9 Módulo de Notificações

```sql
-- Templates de notificação
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Conteúdo
    title_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    
    -- Canais
    channels TEXT[] DEFAULT ARRAY['push', 'email'], -- 'push', 'email', 'sms', 'in_app'
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notificações dos usuários
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id UUID REFERENCES notification_templates(id),
    
    -- Conteúdo
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB, -- Dados extras (deep links, etc.)
    
    -- Tipo
    type VARCHAR(50) NOT NULL, -- 'match', 'application', 'shift_reminder', 'payment', etc.
    priority VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    
    -- Status
    read_at TIMESTAMP,
    clicked_at TIMESTAMP,
    
    -- Referências
    reference_type VARCHAR(50), -- 'job_posting', 'shift', 'application', etc.
    reference_id UUID,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Device tokens para push notifications
CREATE TABLE user_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    device_token TEXT NOT NULL,
    device_type VARCHAR(20) NOT NULL, -- 'ios', 'android', 'web'
    device_name VARCHAR(100),
    
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, device_token)
);
```

---

## 5. Regras de Negócio

### 5.1 Autenticação e Autorização

1. **Firebase Auth** é usado apenas para autenticação (login/logout)
2. **Roles e Permissions** são gerenciadas internamente na API
3. Um usuário pode ter múltiplas roles (médico + gestor)
4. Permissions podem vir de:
   - Roles atribuídas ao usuário
   - Permissions standalone atribuídas diretamente
5. A lista final de permissions é a união de todas as fontes

### 5.2 Geolocalização e Ponto

1. O **geofence** é configurado por Unit ou Sector
2. Se o Sector não tem coordenadas, herda da Unit
3. O check-in/out só é válido se estiver dentro do raio configurado
4. O cálculo de pagamento é: `(worked_minutes / 60) * hourly_rate`
5. O tempo trabalhado pode ser menor ou maior que o definido no plantão

### 5.3 Plantões e Vagas

1. Plantões podem pertencer a uma Schedule ou serem avulsos
2. Vagas (Job Postings) podem ser criadas a partir de um Shift ou avulsas
3. Um Shift pode ter no máximo uma Job Posting ativa
4. Múltiplos Shifts podem ter o mesmo horário na mesma Schedule

### 5.4 Matching

1. O matching ocorre entre Professional Availabilities e Job Postings
2. O score considera: horário, especialidade, localização, valor e tipo de profissional
3. Matches são a principal fonte de monetização

### 5.5 Profissionais

1. Um profissional pode existir **sem** ter um usuário na plataforma (pré-cadastro por escalista)
2. Quando o profissional criar conta, o sistema tentará vincular via `email` ou `cpf`
3. O campo `claimed_at` marca quando o profissional "reivindicou" seu perfil pré-cadastrado
4. Um profissional pode ter múltiplos registros em conselhos (CRM em 2 estados, ou CRM + COREN)
5. Especialidades podem ter status de residência para profissionais em formação
6. O campo `is_generalist` na especialidade identifica profissionais sem especialização

---

## 6. Fluxos Principais

### 6.1 Fluxo do Gestor

```
1. Criar Organization
2. Adicionar Units (com geolocalização)
3. Adicionar Sectors nas Units
4. Criar Schedules nos Sectors
5. Criar Shifts nas Schedules (ou avulsos)
6. Publicar Job Postings a partir dos Shifts
7. Receber candidaturas
8. Aceitar/Rejeitar candidatos
9. Acompanhar check-in/out
10. Aprovar pagamentos
```

### 6.2 Fluxo do Profissional

```
1. Criar conta ou reivindicar perfil pré-cadastrado
2. Completar perfil (dados pessoais, registros em conselhos, especialidades)
3. Definir disponibilidade (escala reversa)
4. Buscar vagas / Receber matches
5. Candidatar-se às vagas
6. Ser aceito/rejeitado
7. Fazer check-in no plantão (geolocalização)
8. Fazer check-out
9. Visualizar pagamentos
```

### 6.3 Fluxo de Pré-cadastro (Escalista)

```
1. Escalista cadastra profissional com dados básicos
2. Profissional recebe convite por email/SMS
3. Profissional cria conta na plataforma
4. Sistema vincula conta ao perfil via email ou CPF
5. Profissional confirma e completa o perfil
```

---

## 7. Considerações Técnicas

### 7.1 Stack Tecnológica

- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL
- **Auth**: Firebase Authentication
- **Cache**: Redis
- **Queue**: RabbitMQ / Redis
- **Mobile**: React Native / Flutter

### 7.2 Índices Recomendados

Além dos índices já definidos nas tabelas:

```sql
-- Busca de vagas por localização
CREATE INDEX idx_job_postings_location ON job_postings(state, city);

-- Busca de profissionais por especialidade
CREATE INDEX idx_professional_specialties_lookup ON professional_specialties(specialty_id, professional_id);

-- Plantões por data e status
CREATE INDEX idx_shifts_date_status ON shifts(shift_date, status);

-- Time records por período
CREATE INDEX idx_time_records_period ON time_records(check_in_at, check_out_at);

-- Profissionais por tipo e disponibilidade
CREATE INDEX idx_professional_type_available ON professional_profiles(professional_type, is_available) 
    WHERE deleted_at IS NULL;
```

### 7.3 Extensões PostgreSQL Sugeridas

```sql
-- Para busca geográfica
CREATE EXTENSION IF NOT EXISTS postgis;

-- Para busca full-text
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 8. Próximos Passos

1. [ ] Definir migrations com Alembic
2. [ ] Implementar models SQLAlchemy
3. [ ] Criar schemas Pydantic
4. [ ] Implementar repositórios
5. [ ] Desenvolver casos de uso
6. [ ] Criar endpoints da API
7. [ ] Implementar sistema de matching
8. [ ] Desenvolver app mobile

---

## 9. Glossário

| Termo EN | Termo PT | Descrição |
|----------|----------|-----------|
| Organization | Organização | Entidade principal (hospital, clínica) |
| Unit | Unidade | Local físico (ala, filial, prédio) |
| Sector | Setor | Subdivisão (sala, departamento) |
| Schedule | Escala | Agenda de plantões |
| Shift | Plantão | Turno de trabalho individual |
| Job Posting | Vaga/Anúncio | Publicação de oportunidade |
| Professional | Profissional | Médico, enfermeiro, técnico, etc. |
| Council | Conselho | Órgão regulador (CRM, COREN, etc.) |
| Specialty | Especialidade | Área de atuação do profissional |
| RQE | RQE | Registro de Qualificação de Especialista |
| Residency | Residência | Formação especializada (R1, R2, R3...) |
| Availability | Disponibilidade | Horários livres do profissional |
| Time Record | Registro de Ponto | Check-in/out do plantão |
| Match | Correspondência | Compatibilidade entre profissional e vaga |
| Geofence | Cerca Virtual | Área permitida para ponto |
| Claim Profile | Reivindicar Perfil | Quando profissional assume perfil pré-cadastrado |
