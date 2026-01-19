# Módulo de Organizações

## Visão Geral

O módulo de organizações gerencia a estrutura hierárquica de hospitais, clínicas e empresas terceirizadoras. Suporta uma hierarquia de **um nível** entre organizações (pai → filhas), além da estrutura interna Organization → Unit → Sector.

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              HIERARQUIA ORGANIZACIONAL                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────┐                                                                   │
│  │   Organization   │◄──────────────┐ (self-reference: parent_id)                       │
│  │ (Terceirizadora) │               │                                                   │
│  └──────────────────┘               │                                                   │
│          │                          │ (máx 1 nível)                                     │
│         1:N                         │                                                   │
│          ▼                          │                                                   │
│  ┌──────────────────┐               │                                                   │
│  │   Organization   │───────────────┘                                                   │
│  │    (Hospital)    │                                                                   │
│  └──────────────────┘                                                                   │
│          │                                                                              │
│         1:N                                                                             │
│          ▼                                                                              │
│  ┌──────────────────┐      ┌──────────────────┐                                         │
│  │       Unit       │──1:N─│      Sector      │                                         │
│  │    (Ala Sul)     │      │      (UTI)       │                                         │
│  └──────────────────┘      └──────────────────┘                                         │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           MEMBROS (Polimórfico)                                  │   │
│  │                                                                                  │   │
│  │  User ──N:N── OrganizationMember ──N:1── Organization / Unit / Sector            │   │
│  │                      │                                                           │   │
│  │                      └── role (OWNER, ADMIN, MANAGER, SCHEDULER, VIEWER)         │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           ENTIDADE LEGAL (Opcional)                              │   │
│  │                                                                                  │   │
│  │  Organization ──N:1── Company (shared)                                           │   │
│  │        │                  │                                                      │   │
│  │        └── cnpj           └── cnpj, legal_name, bank_accounts                    │   │
│  │      (se Company                                                                 │   │
│  │        não vinculada)                                                            │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Enums

### OrganizationType
Tipos de organizações de saúde.

| Valor | Descrição |
|-------|-----------|
| HOSPITAL | Hospital |
| CLINIC | Clínica |
| LABORATORY | Laboratório |
| EMERGENCY_UNIT | UPA / Pronto Socorro |
| HEALTH_CENTER | Posto de Saúde / UBS |
| HOME_CARE | Home Care |
| OUTSOURCING_COMPANY | Empresa Terceirizadora / Licitadora |
| OTHER | Outros |

### MemberRole
Papéis para membros da organização.

| Valor | Descrição | Permissões |
|-------|-----------|------------|
| OWNER | Proprietário | Acesso total, pode deletar org |
| ADMIN | Administrador | Gerencia membros e configurações |
| MANAGER | Gestor | Gerencia escalas e plantões |
| SCHEDULER | Escalista | Cria/edita escalas |
| VIEWER | Visualizador | Apenas leitura |

### SharingScope
Define o que uma organização pai compartilha com as filhas.

| Valor | Descrição |
|-------|-----------|
| NONE | Nenhum compartilhamento |
| PROFESSIONALS | Compartilha apenas profissionais cadastrados |
| SCHEDULES | Compartilha profissionais + escalas |
| FULL | Compartilhamento total |

### EntityType
Tipos de entidade para membership polimórfico.

| Valor | Descrição |
|-------|-----------|
| ORGANIZATION | Membro da organização |
| UNIT | Membro de uma unidade |
| SECTOR | Membro de um setor |

## Tabelas

### organizations

Organizações de saúde (hospitais, clínicas, terceirizadoras).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| parent_id | UUID | ✅ | FK para organizations (org pai) |
| company_id | UUID | ✅ | FK para companies (entidade legal) |
| name | VARCHAR(255) | ❌ | Nome da organização |
| trading_name | VARCHAR(255) | ✅ | Nome fantasia |
| organization_type | OrganizationType | ❌ | Tipo da organização |
| cnpj | VARCHAR(14) | ✅ | CNPJ (se não tiver Company vinculada) |
| email | VARCHAR(255) | ✅ | Email |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| website | VARCHAR(500) | ✅ | Website |
| sharing_scope | SharingScope | ❌ | O que compartilhar com filhas |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Endereço (AddressMixin)** | | | |
| address, number, complement, neighborhood, city, state_code, state_name, postal_code, latitude, longitude | | ✅ | |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| **Timestamps & Soft Delete** | | | |
| created_at, updated_at, deleted_at | TIMESTAMP | ✅* | |

**Constraints:**
- UNIQUE PARTIAL INDEX: `cnpj WHERE cnpj IS NOT NULL AND deleted_at IS NULL`

**Regra de Hierarquia:**
- Se `parent_id IS NULL` → organização raiz (pode ter filhas)
- Se `parent_id IS NOT NULL` → organização filha (NÃO pode ter filhas)
- Validação no application layer: `parent.parent_id` deve ser NULL

### units

Unidades físicas dentro de uma organização.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations |
| name | VARCHAR(255) | ❌ | Nome da unidade |
| code | VARCHAR(50) | ✅ | Código interno |
| description | TEXT | ✅ | Descrição |
| email | VARCHAR(255) | ✅ | Email |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| geofence_radius_meters | INTEGER | ✅ | Raio do geofence (0-10000) |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Endereço (AddressMixin)** | | | |
| address, ..., latitude, longitude | | ✅ | Usado para geofence |
| **Verificação (VerificationMixin)** | | | |
| verified_at, verified_by | | ✅ | |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | | ✅ | |
| **Timestamps** | | | |
| created_at, updated_at | | | |

**Constraints:**
- UNIQUE(organization_id, code)

### sectors

Setores dentro de uma unidade.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| unit_id | UUID | ❌ | FK para units |
| name | VARCHAR(255) | ❌ | Nome do setor |
| code | VARCHAR(50) | ✅ | Código interno |
| description | TEXT | ✅ | Descrição |
| latitude | FLOAT | ✅ | Override de latitude |
| longitude | FLOAT | ✅ | Override de longitude |
| geofence_radius_meters | INTEGER | ✅ | Override de raio |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | | ✅ | |
| **Timestamps** | | | |
| created_at, updated_at | | | |

**Constraints:**
- UNIQUE(unit_id, code)

**Herança de Geofence:**
- Se `latitude/longitude/geofence_radius_meters` forem NULL, herda da Unit pai

### organization_members

Membros (usuários) vinculados a organizações, unidades ou setores.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ❌ | FK para users |
| organization_id | UUID | ✅ | FK para organizations (XOR) |
| unit_id | UUID | ✅ | FK para units (XOR) |
| sector_id | UUID | ✅ | FK para sectors (XOR) |
| role | MemberRole | ❌ | Papel do membro |
| invited_at | TIMESTAMP | ✅ | Quando foi convidado |
| accepted_at | TIMESTAMP | ✅ | Quando aceitou |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | | ✅ | |
| **Timestamps** | | | |
| created_at, updated_at | | | |

**Constraints:**
- CHECK: Exatamente um de (organization_id, unit_id, sector_id) deve ser NOT NULL
- UNIQUE PARTIAL INDEX: `(user_id, organization_id) WHERE organization_id IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(user_id, unit_id) WHERE unit_id IS NOT NULL`
- UNIQUE PARTIAL INDEX: `(user_id, sector_id) WHERE sector_id IS NOT NULL`

## Regras de Negócio

### Hierarquia de Organizações

1. Uma organização pode ser **raiz** (sem parent_id) ou **filha** (com parent_id)
2. **Máximo 1 nível de profundidade**: organizações filhas não podem ter filhas
3. O `sharing_scope` da organização pai define o que as filhas podem acessar
4. Organizações filhas herdam profissionais e/ou escalas conforme configurado

### Hierarquia Organization → Unit → Sector

1. Uma organização pode ter múltiplas unidades
2. Uma unidade pode ter múltiplos setores
3. Setores herdam geofence da unit se não definirem o próprio
4. Escalas (Schedules) serão vinculadas a Sectors

### Membros e Permissões

1. Um usuário pode ser membro de múltiplas entidades (org, unit, sector)
2. **Herança de acesso**:
   - Membro de Organization → acesso a todas Units e Sectors
   - Membro de Unit → acesso a todos Sectors da Unit
   - Membro de Sector → acesso apenas ao Sector
3. O `role` define o que o membro pode fazer (OWNER > ADMIN > MANAGER > SCHEDULER > VIEWER)
4. `invited_at` + `accepted_at` = NULL → acesso imediato (adicionado diretamente)
5. `invited_at` NOT NULL + `accepted_at` = NULL → convite pendente

### Company vs Organization

1. Uma Organization pode ter um `company_id` vinculando a uma Company (entidade legal)
2. Se `company_id` for NULL, a Organization pode ter seu próprio `cnpj`
3. A Company é usada para questões legais/financeiras (contratos, pagamentos)

## Arquivos de Implementação

```
src/modules/organizations/domain/models/
├── __init__.py
├── enums.py                  # OrganizationType, MemberRole, SharingScope, EntityType
├── organization.py           # Organization model
├── unit.py                   # Unit model
├── sector.py                 # Sector model
└── organization_member.py    # OrganizationMember model
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | Organization |
| TrackingMixin | created_by, updated_by | Todas as tabelas |
| AddressMixin | address, ..., latitude, longitude | Organization, Unit |
| VerificationMixin | verified_at, verified_by | Organization, Unit |

## Fluxos Principais

### Fluxo de Criação de Organização

```
1. Criar Organization (tipo: HOSPITAL, CLINIC, etc.)
2. [Opcional] Vincular a uma Company existente ou criar CNPJ próprio
3. Adicionar primeiro membro como OWNER
4. Criar Units com endereço e geofence
5. Criar Sectors dentro das Units
6. Adicionar membros (ADMIN, MANAGER, SCHEDULER, VIEWER)
```

### Fluxo de Terceirização

```
1. Empresa terceirizadora cria Organization (tipo: OUTSOURCING_COMPANY)
2. Define sharing_scope (PROFESSIONALS, SCHEDULES, ou FULL)
3. Hospital cria Organization filha (parent_id = terceirizadora)
4. Hospital herda profissionais/escalas conforme sharing_scope
5. Cada organização gerencia seus próprios membros
```
