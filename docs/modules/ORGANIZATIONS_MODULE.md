# Módulo de Organizações

## Visão Geral

O módulo de organizações gerencia a estrutura hierárquica de hospitais, clínicas e empresas terceirizadoras. Suporta uma hierarquia de **um nível** entre organizações (pai → filhas). Cada organização mantém seus próprios profissionais isolados (multi-tenant).

> **Nota:** As tabelas `units` e `sectors` foram movidas para o módulo de Unidades. Ver [UNITS_MODULE.md](UNITS_MODULE.md).

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
│          ├──────────────────1:N──────────────────┐                                      │
│          │                                       │                                      │
│          ▼                                       ▼                                      │
│  ┌──────────────────┐                  ┌──────────────────────────┐                     │
│  │ OrganizationMember│                 │ OrganizationProfessional │                     │
│  │   (User + Role)   │                 │     (multi-tenant)       │                     │
│  └──────────────────┘                  └──────────────────────────┘                     │
│          │                                                                              │
│         N:1                                                                             │
│          ▼                                                                              │
│  ┌──────────────────┐                                                                   │
│  │       User       │                                                                   │
│  └──────────────────┘                                                                   │
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

### DataScopePolicy (Runtime)
Define o escopo de busca de dados entre organizações da mesma família. Este enum é usado no nível de aplicação (não armazenado em banco).

| Valor | Descrição |
|-------|-----------|
| ORGANIZATION_ONLY | Dados apenas da organização atual |
| FAMILY | Dados de todas as organizações da família (pai + filhas/irmãs) |

> **Nota:** O escopo padrão para profissionais é `FAMILY` - profissionais são compartilhados entre todas as organizações da família. A validação de unicidade (CPF, email, registro de conselho) também é feita no escopo da família.

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
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Endereço (AddressMixin)** | | | |
| address, number, complement, neighborhood, city, state_code, postal_code, latitude, longitude | | ✅ | |
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

### organization_members

Membros (usuários) vinculados a organizações.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ❌ | FK para users |
| organization_id | UUID | ❌ | FK para organizations |
| role | MemberRole | ❌ | Papel do membro |
| invited_at | TIMESTAMP | ✅ | Quando foi convidado |
| accepted_at | TIMESTAMP | ✅ | Quando aceitou |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | | ✅ | |
| **Timestamps** | | | |
| created_at, updated_at | | | |

**Constraints:**
- UNIQUE(user_id, organization_id)

**Índices de Performance:**
- `ix_organization_members_user_id` - busca por membros de um usuário
- `ix_organization_members_organization_id` - busca por membros de uma organização

## Tabelas Relacionadas (Outros Módulos)

> As tabelas de unidades e setores foram implementadas no módulo de Unidades.
> Ver [UNITS_MODULE.md](UNITS_MODULE.md) para detalhes.

## Regras de Negócio

### Hierarquia de Organizações

1. Uma organização pode ser **raiz** (sem parent_id) ou **filha** (com parent_id)
2. **Máximo 1 nível de profundidade**: organizações filhas não podem ter filhas
3. Profissionais são **compartilhados automaticamente** entre todas as organizações da família
4. A validação de unicidade (CPF, email, registro de conselho) é feita no **escopo da família**
5. Todas as organizações da família podem visualizar e editar os mesmos profissionais
6. Os `family_org_ids` são cacheados em Redis para performance

### Multi-Tenancy de Profissionais

1. Profissionais são **compartilhados dentro da família** de organizações (pai + filhas)
2. A mesma pessoa (CPF) **não pode** existir em múltiplas organizações da mesma família
3. Organizações de **famílias diferentes** não podem acessar profissionais umas das outras
4. O campo `organization_id` indica qual organização criou o profissional
5. Consultas usam `family_org_ids` do contexto para filtrar profissionais da família

### Membros e Permissões

1. Um usuário pode ser membro de múltiplas organizações
2. O `role` define o que o membro pode fazer (OWNER > ADMIN > MANAGER > SCHEDULER > VIEWER)
3. `invited_at` + `accepted_at` = NULL → acesso imediato (adicionado diretamente)
4. `invited_at` NOT NULL + `accepted_at` = NULL → convite pendente

### Company vs Organization

1. Uma Organization pode ter um `company_id` vinculando a uma Company (entidade legal)
2. Se `company_id` for NULL, a Organization pode ter seu próprio `cnpj`
3. A Company é usada para questões legais/financeiras (contratos, pagamentos)

## Arquivos de Implementação

```
src/modules/organizations/domain/models/
├── __init__.py
├── enums.py                  # OrganizationType, MemberRole, SharingScope
├── organization.py           # Organization model
└── organization_member.py    # OrganizationMember model
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Todas as tabelas |
| TimestampMixin | created_at, updated_at | Todas as tabelas |
| SoftDeleteMixin | deleted_at | Organization |
| TrackingMixin | created_by, updated_by | Organization, OrganizationMember |
| AddressMixin | address, ..., latitude, longitude | Organization |
| VerificationMixin | verified_at, verified_by | Organization |

## Fluxos Principais

### Fluxo de Criação de Organização

```
1. Criar Organization (tipo: HOSPITAL, CLINIC, etc.)
2. [Opcional] Vincular a uma Company existente ou criar CNPJ próprio
3. Adicionar primeiro membro como OWNER
4. Cadastrar profissionais (organization_professionals)
5. Adicionar membros (ADMIN, MANAGER, SCHEDULER, VIEWER)
```

### Fluxo de Terceirização

```
1. Empresa terceirizadora cria Organization (tipo: OUTSOURCING_COMPANY)
2. Hospital cria Organization filha (parent_id = terceirizadora)
3. Profissionais cadastrados em qualquer organização da família são visíveis em todas
4. Todas as organizações podem editar os profissionais da família
5. Cada organização gerencia seus próprios membros
6. Unicidade de CPF/email/conselho é validada no escopo da família
```
