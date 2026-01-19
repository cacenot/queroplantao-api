# Módulo de Autenticação e Autorização

## Visão Geral

O módulo de autenticação gerencia usuários, roles e permissões da plataforma. A autenticação é feita via **Firebase Auth**, enquanto a autorização (roles e permissions) é gerenciada internamente.

## Diagrama ER

```
┌──────────┐      ┌──────────────────┐      ┌──────────┐      ┌───────────────────┐
│   User   │──N:N─│   user_roles     │──N:1─│   Role   │──1:N─│ role_permissions  │
└──────────┘      └──────────────────┘      └──────────┘      └───────────────────┘
     │                                                                │
     │            ┌──────────────────────┐                            │
     └─────N:N────│  user_permissions    │──N:1───────────────────────┘
                  └──────────────────────┘                     ┌────────────┐
                                                               │ Permission │
                                                               └────────────┘
```

## Tabelas

### users

Usuários da plataforma. Complementa dados do Firebase Auth.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| firebase_uid | VARCHAR(128) | ❌ | UID do Firebase Auth (unique) |
| email | VARCHAR(255) | ❌ | Email do usuário (unique) |
| full_name | VARCHAR(255) | ✅ | Nome completo |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| avatar_url | VARCHAR(500) | ✅ | URL do avatar |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| email_verified_at | TIMESTAMP | ✅ | Quando email foi verificado |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

### permissions

Permissões disponíveis no sistema.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| code | VARCHAR(100) | ❌ | Código único (ex: 'shift:create') |
| name | VARCHAR(255) | ❌ | Nome legível |
| description | TEXT | ✅ | Descrição da permissão |
| module | VARCHAR(50) | ❌ | Módulo (ex: 'shifts', 'schedules') |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

### roles

Roles do sistema.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| code | VARCHAR(50) | ❌ | Código único (ex: 'doctor', 'admin') |
| name | VARCHAR(100) | ❌ | Nome legível |
| description | TEXT | ✅ | Descrição da role |
| is_system | BOOLEAN | ❌ | Se é role do sistema (não pode deletar) |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

### role_permissions

Permissões de cada role (junction table).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| role_id | UUID | ❌ | FK para roles |
| permission_id | UUID | ❌ | FK para permissions |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(role_id, permission_id)

### user_roles

Roles atribuídas aos usuários (junction table).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ❌ | FK para users |
| role_id | UUID | ❌ | FK para roles |
| granted_by | UUID | ✅ | FK para users (quem concedeu) |
| granted_at | TIMESTAMP | ❌ | Quando foi concedida |
| expires_at | TIMESTAMP | ✅ | Expiração (role temporária) |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(user_id, role_id)

**Nota:** `granted_by` é nullable para suportar:
1. Auto-cadastro: usuário cria conta e recebe role padrão automaticamente
2. Migrações: roles importadas de sistemas legados
3. Sistema: roles atribuídas por processos automatizados

### user_permissions

Permissões standalone atribuídas diretamente aos usuários.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ❌ | FK para users |
| permission_id | UUID | ❌ | FK para permissions |
| granted_by | UUID | ✅ | FK para users (quem concedeu) |
| granted_at | TIMESTAMP | ❌ | Quando foi concedida |
| expires_at | TIMESTAMP | ✅ | Expiração |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |

**Constraints:**
- UNIQUE(user_id, permission_id)

## Regras de Negócio

1. **Firebase Auth** é usado apenas para autenticação (login/logout)
2. **Roles e Permissions** são gerenciadas internamente na API
3. Um usuário pode ter múltiplas roles (ex: médico + gestor)
4. Permissions podem vir de:
   - Roles atribuídas ao usuário
   - Permissions standalone atribuídas diretamente
5. A lista final de permissions é a **união** de todas as fontes
6. Roles e permissions podem ter data de expiração (temporárias)

## Arquivos de Implementação

```
src/modules/auth/domain/models/
├── __init__.py
├── user.py
├── permission.py
├── role.py
├── role_permission.py
├── user_role.py
└── user_permission.py
```
