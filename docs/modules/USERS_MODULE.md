# Módulo de Usuários (Users)

## Visão Geral

O módulo de usuários gerencia:
1. **Dados de usuários**: informações complementares ao Firebase Auth
2. **Roles e Permissions**: autorização gerenciada internamente
3. **Membros de organizações**: usuários associados a organizações com roles específicas
4. **Convites**: fluxo de convite para novos membros de organizações

A **autenticação** é feita via **Firebase Auth**, enquanto a **autorização** (roles e permissions) é gerenciada internamente na API.

## Diagrama ER

```
┌──────────┐      ┌──────────────────┐      ┌──────────┐      ┌───────────────────┐
│   User   │──N:N─│   user_roles     │──N:1─│   Role   │──1:N─│ role_permissions  │
└──────────┘      └──────────────────┘      └──────────┘      └───────────────────┘
     │                    │                      │                     │
     │                    │                      │                     │
     │  ┌─────────────────────────────────┐      │             ┌────────────┐
     └──│  organization_memberships       │──N:1─┘             │ Permission │
        │  (users in organizations)       │                    └────────────┘
        └─────────────────────────────────┘
                       │
                       │
               ┌───────────────┐
               │  Organization │
               └───────────────┘
```

## Fluxo de Convite

1. **Admin convida usuário**: POST /users/invite com email e role_id
2. **Sistema cria membership pendente**: `is_pending=true`, `invited_at=now()`
3. **Email enviado via Resend**: contém link com JWT token
4. **Usuário clica no link**: redireciona para frontend
5. **Frontend chama**: POST /invitations/accept com token
6. **Sistema valida token** e marca `accepted_at=now()`, `is_pending=false`

### Token JWT de Convite

O token contém:
- `email`: email do convidado
- `organization_id`: organização destino
- `role_id`: role a ser atribuída
- `invited_by`: quem enviou o convite
- `membership_id`: ID do membership pendente
- `exp`: expiração (padrão: 7 dias)

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
| cpf | VARCHAR(11) | ✅ | CPF (apenas números) |
| avatar_url | VARCHAR(500) | ✅ | URL do avatar |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| email_verified_at | TIMESTAMP | ✅ | Quando email foi verificado |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |

### organization_memberships

Associações entre usuários e organizações (multi-tenant).

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| user_id | UUID | ❌ | FK para users |
| organization_id | UUID | ❌ | FK para organizations |
| role_id | UUID | ❌ | FK para roles |
| is_active | BOOLEAN | ❌ | Se o membership está ativo |
| granted_by | UUID | ✅ | Quem concedeu a role |
| granted_at | TIMESTAMP | ❌ | Quando a role foi concedida |
| expires_at | TIMESTAMP | ✅ | Expiração da role |
| invited_at | TIMESTAMP | ✅ | Quando o convite foi enviado |
| accepted_at | TIMESTAMP | ✅ | Quando o convite foi aceito |
| created_at | TIMESTAMP | ❌ | Timestamp de criação |
| updated_at | TIMESTAMP | ✅ | Timestamp de atualização |
| deleted_at | TIMESTAMP | ✅ | Soft delete |
| created_by | UUID | ✅ | Quem criou o registro |
| updated_by | UUID | ✅ | Quem atualizou o registro |

**Constraints:**
- UNIQUE(user_id, organization_id) WHERE deleted_at IS NULL

**Propriedade calculada:**
- `is_pending`: `invited_at IS NOT NULL AND accepted_at IS NULL`

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

Roles globais atribuídas aos usuários (junction table).

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

## Endpoints

### Usuário Atual (auth)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/v1/auth/me | Dados do usuário autenticado |
| PATCH | /api/v1/auth/me | Atualizar dados do usuário |

### Membros da Organização (org-scoped)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/v1/users | Listar membros da organização |
| GET | /api/v1/users/summary | Listar membros (resumido) |
| POST | /api/v1/users/invite | Convidar usuário |
| GET | /api/v1/users/{id} | Detalhes de um membro |
| PATCH | /api/v1/users/{id} | Atualizar role/status |
| DELETE | /api/v1/users/{id} | Remover membro |

### Convites (público)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/v1/invitations/accept | Aceitar convite |

## Regras de Negócio

1. **Firebase Auth** é usado apenas para autenticação (login/logout)
2. **Roles e Permissions** são gerenciadas internamente na API
3. Um usuário pode ter múltiplas roles globais (ex: superadmin)
4. Dentro de cada organização, usuário tem uma role específica
5. Permissions podem vir de:
   - Roles globais (user_roles)
   - Role na organização (organization_memberships)
   - Permissions standalone (user_permissions)
6. A lista final de permissions é a **união** de todas as fontes
7. Roles e permissions podem ter data de expiração (temporárias)

### Regras de Convite

1. Não é possível convidar usuário que já é membro
2. Não é possível enviar convite se já existe um pendente para o email
3. Convites expiram após 7 dias (configurável via `INVITATION_TOKEN_EXPIRE_DAYS`)
4. Token expirado não pode ser usado para aceitar convite
5. Usuário que aceita convite pode ser novo ou existente na plataforma

### Regras de Remoção

1. Não é possível remover o próprio usuário (use "sair da organização")
2. Não é possível remover o owner da organização
3. Remoção é soft-delete (preserva histórico)

## Configurações de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `RESEND_API_KEY` | API key do Resend para emails | - |
| `RESEND_FROM_EMAIL` | Email remetente | noreply@queroplantao.com |
| `RESEND_FROM_NAME` | Nome remetente | Quero Plantão |
| `INVITATION_TOKEN_EXPIRE_DAYS` | Dias para expirar convite | 7 |
| `FRONTEND_URL` | URL do frontend (para links) | - |

## Arquivos de Implementação

```
src/modules/users/
├── domain/
│   ├── models/
│   │   ├── user.py
│   │   ├── permission.py
│   │   ├── role.py
│   │   ├── role_permission.py
│   │   ├── user_role.py
│   │   └── user_permission.py
│   └── schemas/
│       ├── user.py
│       └── organization_user.py
├── infrastructure/
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── organization_membership_repository.py
│   ├── filters/
│   │   └── organization_user_filters.py
│   └── services/
│       └── invitation_token_service.py
├── presentation/
│   ├── dependencies/
│   └── routes/
│       ├── me_routes.py
│       ├── organization_user_routes.py
│       └── invitation_routes.py
└── use_cases/
    ├── me/
    └── organization_user/
        ├── list_organization_users_use_case.py
        ├── get_organization_user_use_case.py
        ├── invite_organization_user_use_case.py
        ├── update_organization_user_use_case.py
        ├── remove_organization_user_use_case.py
        └── accept_invitation_use_case.py
```

## Códigos de Erro

| Code | Status | Descrição |
|------|--------|-----------|
| `USER_NOT_FOUND` | 404 | Usuário não encontrado |
| `USER_ALREADY_MEMBER` | 409 | Usuário já é membro da organização |
| `MEMBERSHIP_NOT_FOUND` | 404 | Associação não encontrada |
| `ROLE_NOT_FOUND` | 404 | Função não encontrada |
| `INVITATION_ALREADY_SENT` | 409 | Já existe convite pendente para este email |
| `INVITATION_EXPIRED` | 410 | Convite expirado |
| `INVITATION_INVALID_TOKEN` | 400 | Token de convite inválido |
| `INVITATION_ALREADY_ACCEPTED` | 409 | Convite já foi aceito |
| `CANNOT_REMOVE_SELF` | 403 | Não é possível remover a si mesmo |
| `CANNOT_REMOVE_OWNER` | 403 | Não é possível remover o dono da organização |
