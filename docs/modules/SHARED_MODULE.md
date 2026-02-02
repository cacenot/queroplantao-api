# Módulo Shared

## Visão Geral

O módulo **shared** contém toda a infraestrutura base, componentes reutilizáveis e entidades compartilhadas entre todos os módulos da aplicação. É a fundação sobre a qual os módulos de domínio são construídos.

### Principais Responsabilidades

- **Base Classes**: Modelos base, mixins e repositórios genéricos
- **Value Objects**: Tipos validados para CPF, CNPJ, Telefone, CEP, UF
- **Entidades Compartilhadas**: Specialty, DocumentType, Bank, BankAccount, Company
- **Infraestrutura**: Conexão com banco, cache Redis, Firebase, email, messaging
- **Schemas Comuns**: Responses de erro, paginação, health check

## Estrutura de Diretórios

```
src/shared/
├── domain/
│   ├── events/                    # Event Sourcing (future)
│   ├── models/                    # Modelos SQLModel compartilhados
│   │   ├── base.py               # BaseModel + naming conventions
│   │   ├── mixins.py             # Mixins reutilizáveis
│   │   ├── fields.py             # Custom field helpers
│   │   ├── enums.py              # Enums compartilhados
│   │   ├── specialty.py          # Especialidades médicas (global)
│   │   ├── document_type.py      # Tipos de documento (org-scoped)
│   │   ├── bank.py               # Bancos (referência)
│   │   ├── bank_account.py       # Contas bancárias
│   │   └── company.py            # Empresas (PJ)
│   ├── schemas/                   # Pydantic DTOs compartilhados
│   │   ├── common.py             # ErrorResponse, HealthResponse
│   │   ├── enum.py               # Schemas para enums
│   │   ├── specialty.py          # DTOs de especialidade
│   │   ├── document_type.py      # DTOs de tipo de documento
│   │   └── bank_account.py       # DTOs de conta bancária
│   └── value_objects/            # Value Objects validados
│       ├── documents.py          # CPF, CNPJ, CPFOrCNPJ
│       ├── contact.py            # Phone
│       ├── address.py            # PostalCode
│       └── state.py              # StateUF
├── infrastructure/
│   ├── cache/                     # Redis cache service
│   ├── database/                  # Conexão async SQLAlchemy
│   ├── email/                     # Resend email service
│   ├── external/                  # Integrações externas
│   ├── filters/                   # FilterSet/SortingSet
│   ├── firebase/                  # Firebase Admin SDK
│   ├── messaging/                 # LavinMQ/RabbitMQ broker
│   └── repositories/              # Base repository + mixins
├── presentation/
│   ├── dependencies/              # FastAPI dependencies compartilhadas
│   └── routes/                    # Rotas globais (specialties, enums)
└── use_cases/
    ├── document_type/             # CRUD de tipos de documento
    └── specialty/                 # Leitura de especialidades
```

## Mixins de Modelo

Mixins são classes reutilizáveis que adicionam campos e comportamentos aos modelos SQLModel.

### PrimaryKeyMixin

Adiciona UUID v7 como chave primária.

```python
from src.shared.domain.models import PrimaryKeyMixin

class MyModel(PrimaryKeyMixin, table=True):
    __tablename__ = "my_table"
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Chave primária ordenada por tempo |

**Vantagens do UUID v7:**
- Identificadores ordenados por tempo
- Melhor performance de índices
- Evita fragmentação de índice

### TimestampMixin

Rastreamento automático de timestamps via `server_default`.

```python
from src.shared.domain.models import TimestampMixin

class MyModel(TimestampMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| created_at | TIMESTAMP WITH TZ | Quando o registro foi criado (UTC) |
| updated_at | TIMESTAMP WITH TZ | Última atualização (UTC), `onupdate=now()` |

### TrackingMixin

Rastreia quem criou e atualizou o registro (audit trail).

```python
from src.shared.domain.models import TrackingMixin

class MyModel(TrackingMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| created_by | UUID | Usuário que criou o registro |
| updated_by | UUID | Usuário que atualizou por último |

### VersionMixin

Optimistic locking para prevenir conflitos de atualização concorrente.

```python
from src.shared.domain.models import VersionMixin

class MyModel(VersionMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| version | INTEGER | Número de versão (incrementado a cada update) |

### SoftDeleteMixin (Model)

Permite soft delete ao invés de exclusão física.

```python
from src.shared.domain.models import SoftDeleteMixin

class MyModel(SoftDeleteMixin, table=True):
    pass

# Uso
entity.is_deleted  # property: True se deleted_at não for None
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| deleted_at | TIMESTAMP WITH TZ | Quando o registro foi "deletado" |

**Importante:** Criar índices parciais únicos com `postgresql_where=text("deleted_at IS NULL")`.

### AddressMixin

Campos completos de endereço brasileiro.

```python
from src.shared.domain.models import AddressMixin

class MyModel(AddressMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| address | VARCHAR(255) | Logradouro |
| number | VARCHAR(20) | Número |
| complement | VARCHAR(100) | Complemento |
| neighborhood | VARCHAR(100) | Bairro |
| city | VARCHAR(100) | Cidade |
| state_code | VARCHAR(2) | UF (2 caracteres) |
| postal_code | VARCHAR(10) | CEP |
| latitude | FLOAT | Coordenada latitude |
| longitude | FLOAT | Coordenada longitude |

### VerificationMixin

Rastreia quando e por quem um registro foi verificado.

```python
from src.shared.domain.models import VerificationMixin

class MyModel(VerificationMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| verified_at | TIMESTAMP WITH TZ | Quando foi verificado |
| verified_by | UUID | FK para users.id |

### MetadataMixin

Armazenamento flexível de dados JSON para extensibilidade.

```python
from src.shared.domain.models import MetadataMixin

class MyModel(MetadataMixin, table=True):
    pass
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| extra_metadata | JSONB | Dados JSON arbitrários |

**Nota:** Campo nomeado `extra_metadata` para evitar conflito com atributo reservado `metadata` do SQLModel.

## Custom Fields

Helpers para criar campos SQLModel com configurações pré-definidas.

### AwareDatetimeField

Campo datetime com timezone (TIMESTAMP WITH TIME ZONE).

```python
from pydantic import AwareDatetime
from src.shared.domain.models import AwareDatetimeField

class MyModel(table=True):
    scheduled_at: AwareDatetime = AwareDatetimeField(
        default=None,
        description="Data agendada (UTC)",
    )
```

### PhoneField

Campo de telefone com validação E.164.

```python
from src.shared.domain.models import PhoneField

class MyModel(table=True):
    phone: str | None = PhoneField(
        nullable=True,
        description="Telefone (E.164)",
    )
```

### CPFField / CNPJField / CPFOrCNPJField

Campos para documentos brasileiros (apenas dígitos).

```python
from src.shared.domain.models import CPFField, CNPJField, CPFOrCNPJField

class MyModel(table=True):
    cpf: str = CPFField(description="CPF")
    cnpj: str = CNPJField(description="CNPJ")
    document: str = CPFOrCNPJField(description="CPF ou CNPJ")
```

## Value Objects

Tipos validados que garantem dados consistentes em schemas Pydantic.

### CPF

Valida e normaliza CPF brasileiro (11 dígitos).

```python
from src.shared.domain.value_objects import CPF

cpf = CPF("123.456.789-09")  # → "12345678909"
```

| Entrada | Saída | Descrição |
|---------|-------|-----------|
| "123.456.789-09" | "12345678909" | Remove formatação |
| "12345678909" | "12345678909" | Apenas dígitos |
| "111.111.111-11" | ValueError | CPF inválido |

### CNPJ

Valida e normaliza CNPJ brasileiro (14 dígitos).

```python
from src.shared.domain.value_objects import CNPJ

cnpj = CNPJ("12.345.678/0001-90")  # → "12345678000190"
```

### CPFOrCNPJ

Detecta automaticamente e valida CPF ou CNPJ.

```python
from src.shared.domain.value_objects import CPFOrCNPJ

doc = CPFOrCNPJ("123.456.789-09")    # CPF → "12345678909"
doc = CPFOrCNPJ("12.345.678/0001-90") # CNPJ → "12345678000190"
```

### Phone

Valida e normaliza telefone para formato E.164 internacional.

```python
from src.shared.domain.value_objects import Phone

phone = Phone("+55 11 99999-9999")  # → "+5511999999999"
phone = Phone("+1 (555) 123-4567")  # → "+15551234567"

# Propriedades
phone.ddi           # "55"
phone.ddd           # "11" (para Brasil)
phone.formatted_national  # "(11) 99999-9999"
```

### StateUF

Valida código de estado brasileiro (2 letras).

```python
from src.shared.domain.value_objects import StateUF, BRAZILIAN_STATES

uf = StateUF("sp")   # → "SP" (normalizado)
uf = StateUF("XX")   # → ValueError

# Propriedades
uf.full_name  # "São Paulo"
uf.region     # "Sudeste"

# Métodos de classe
StateUF.get_states_by_region("Sudeste")  # [SP, RJ, MG, ES]

# Dicionário de estados
BRAZILIAN_STATES  # {"AC": "Acre", "AL": "Alagoas", ...}
```

### PostalCode

Valida CEP brasileiro (8 dígitos).

```python
from src.shared.domain.value_objects import PostalCode

cep = PostalCode("12345-678")  # → "12345678"

# Propriedades
cep.formatted  # "12345-678"
cep.region     # Região baseada no primeiro dígito
```

## Enums Compartilhados

### AccountType

Tipos de conta bancária.

| Valor | Descrição |
|-------|-----------|
| CHECKING | Conta Corrente |
| SAVINGS | Conta Poupança |

### PixKeyType

Tipos de chave PIX.

| Valor | Descrição |
|-------|-----------|
| CPF | CPF do titular |
| CNPJ | CNPJ da empresa |
| EMAIL | E-mail |
| PHONE | Telefone celular |
| RANDOM | Chave aleatória (EVP) |

### DocumentCategory

Categoria de documento baseada na entidade relacionada.

| Valor | Descrição |
|-------|-----------|
| PROFILE | Documentos pessoais do profissional |
| QUALIFICATION | Documentos da qualificação/conselho |
| SPECIALTY | Documentos da especialidade |

## Modelos Compartilhados

### Specialty

Especialidades médicas reconhecidas pelo CFM. **Dados globais, somente leitura.**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Primary key |
| code | VARCHAR(50) | Código (ex: 'CARDIOLOGIA') |
| name | VARCHAR(150) | Nome em português |
| description | TEXT | Descrição opcional |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Última atualização |
| deleted_at | TIMESTAMP | Soft delete |

**Índices:**
- `uq_specialties_code` - Código único (partial, onde `deleted_at IS NULL`)
- `idx_specialties_search_trgm` - GIN trigram para busca
- `idx_specialties_name` - B-tree para ordenação

### DocumentType

Tipos de documento configuráveis por organização.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Primary key |
| organization_id | UUID | FK para organizations (tenant) |
| name | VARCHAR(255) | Nome de exibição |
| category | DocumentCategory | Categoria (PROFILE/QUALIFICATION/SPECIALTY) |
| description | VARCHAR(500) | Descrição breve |
| help_text | TEXT | Instruções detalhadas de obtenção |
| validation_instructions | TEXT | Instruções para revisores |
| validation_url | VARCHAR(500) | URL de validação (ex: portal CFM) |
| requires_expiration | BOOLEAN | Se tem data de validade |
| default_validity_days | INTEGER | Dias de validade padrão |
| required_for_professional_types | JSONB | Tipos de profissional que requerem |
| is_active | BOOLEAN | Se está em uso |
| display_order | INTEGER | Ordem de exibição |
| created_by | UUID | Quem criou |
| updated_by | UUID | Quem atualizou |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Atualização |
| deleted_at | TIMESTAMP | Soft delete |

**Escopo:** Organization-scoped, visível dentro da família (parent + children).

### Bank

Tabela de referência de bancos brasileiros (BACEN).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Primary key |
| code | VARCHAR(10) | Código COMPE (ex: '001') |
| ispb_code | VARCHAR(8) | Código ISPB (8 dígitos) |
| name | VARCHAR(255) | Nome completo |
| short_name | VARCHAR(50) | Nome comercial |
| is_active | BOOLEAN | Se está ativo |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Atualização |

### BankAccount

Conta bancária para pagamentos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Primary key |
| bank_id | UUID | FK para banks |
| organization_professional_id | UUID | FK para profissional (XOR com company_id) |
| company_id | UUID | FK para company (XOR com professional_id) |
| agency | VARCHAR(10) | Número da agência |
| agency_digit | VARCHAR(2) | Dígito da agência |
| account_number | VARCHAR(20) | Número da conta |
| account_digit | VARCHAR(2) | Dígito da conta |
| account_type | AccountType | CHECKING ou SAVINGS |
| holder_name | VARCHAR(255) | Nome do titular |
| holder_document | VARCHAR(14) | CPF ou CNPJ do titular |
| pix_key_type | PixKeyType | Tipo de chave PIX |
| pix_key | VARCHAR(255) | Valor da chave PIX |
| is_primary | BOOLEAN | Se é conta principal |
| is_active | BOOLEAN | Se está ativa |
| verified_at | TIMESTAMP | Quando foi verificada |
| verified_by | UUID | Quem verificou |
| created_by | UUID | Quem criou |
| updated_by | UUID | Quem atualizou |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Atualização |

**Constraints:**
- Check: XOR entre `organization_professional_id` e `company_id`
- Unique: Uma conta primária por owner (partial index)
- Unique: Combinação bank + agency + account por owner

### Company

Pessoa jurídica (empresa) para contratos e pagamentos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (v7) | Primary key |
| cnpj | VARCHAR(14) | CNPJ (14 dígitos) |
| legal_name | VARCHAR(255) | Razão Social |
| trade_name | VARCHAR(255) | Nome Fantasia |
| state_registration | VARCHAR(30) | Inscrição Estadual |
| municipal_registration | VARCHAR(30) | Inscrição Municipal |
| email | VARCHAR(255) | Email da empresa |
| phone | VARCHAR(20) | Telefone (E.164) |
| (AddressMixin) | - | Campos de endereço |
| is_active | BOOLEAN | Se está ativa |
| verified_at | TIMESTAMP | Verificação |
| verified_by | UUID | Quem verificou |
| created_by | UUID | Quem criou |
| updated_by | UUID | Quem atualizou |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Atualização |

## Sistema de Repositórios

### BaseRepository

Classe base para operações CRUD com paginação.

```python
from src.shared.infrastructure.repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    model = User
```

**Métodos:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_query()` | `Select` | Query base (override em mixins) |
| `get_by_id(id)` | `T \| None` | Busca por ID |
| `get_by_id_or_raise(id)` | `T` | Busca ou levanta NotFoundError |
| `list(filters, sorting, limit, offset, base_query)` | `PaginatedResponse[T]` | Listagem paginada |
| `list_all(filters, sorting, base_query)` | `list[T]` | Lista tudo (sem paginação) |
| `create(entity)` | `T` | Criar entidade |
| `update(entity)` | `T` | Atualizar entidade |
| `delete(id)` | `None` | Deletar entidade (hard delete) |

### SoftDeleteMixin (Repository)

Adiciona soft delete ao repositório.

```python
from src.shared.infrastructure.repositories import BaseRepository, SoftDeleteMixin

class ProfessionalRepository(SoftDeleteMixin[Professional], BaseRepository[Professional]):
    model = Professional
```

**Comportamentos:**
- `get_query()` → Filtra `WHERE deleted_at IS NULL`
- `delete(id)` → Define `deleted_at = now()` ao invés de excluir

**Métodos Adicionais:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_by_id_including_deleted(id)` | `T \| None` | Ignora filtro de soft delete |
| `restore(id)` | `T` | Limpa `deleted_at` para restaurar |

### OrganizationScopeMixin

Adiciona escopo por organização com suporte a hierarquia familiar.

```python
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    SoftDeleteMixin,
)

class DocumentTypeRepository(
    OrganizationScopeMixin[DocumentType],
    SoftDeleteMixin[DocumentType],
    BaseRepository[DocumentType],
):
    model = DocumentType
    default_scope_policy = "FAMILY"
```

**Scope Policies:**

| Policy | Descrição |
|--------|-----------|
| `ORGANIZATION_ONLY` | Apenas a organização atual |
| `FAMILY` | Todas as orgs na família (parent + children) |

**Métodos:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_by_organization(id, org_id, family_ids, scope_policy)` | `T \| None` | Busca com escopo |
| `list_by_organization(org_id, family_ids, filters, sorting, ...)` | `PaginatedResponse[T]` | Lista com escopo |
| `list_all_by_organization(org_id, family_ids, ...)` | `list[T]` | Lista tudo com escopo |
| `exists_in_family(family_ids, **filters)` | `bool` | Verifica existência na família |
| `find_in_family(family_ids, exclude_id, **filters)` | `T \| None` | Busca na família |

### Ordem de Herança (CRÍTICO)

A ordem dos mixins importa devido ao MRO (Method Resolution Order) do Python:

```python
# ✅ CORRETO: Mais específico → Menos específico → Base
class MyRepository(
    OrganizationScopeMixin[Entity],  # 1º - mais específico
    SoftDeleteMixin[Entity],          # 2º
    BaseRepository[Entity],           # 3º - base
):
    model = Entity

# ❌ ERRADO: Ordem invertida
class MyRepository(
    BaseRepository[Entity],
    SoftDeleteMixin[Entity],
    OrganizationScopeMixin[Entity],
):
    ...
```

## Infraestrutura

### Database Connection

Conexão async com PostgreSQL via SQLAlchemy.

```python
from src.shared.infrastructure.database.connection import async_session_factory

async with async_session_factory() as session:
    # operações de banco
```

### Redis Cache

Cache distribuído com serialização JSON automática.

```python
from src.shared.infrastructure.cache import get_redis_cache

cache = get_redis_cache()

# Operações
await cache.get("key")                    # Busca valor
await cache.set("key", value, ttl=3600)   # Define com TTL
await cache.delete("key")                 # Remove
await cache.exists("key")                 # Verifica existência

# Helpers para chaves
RedisCache.token_cache_key(token_hash)    # "firebase_token:{hash}"
RedisCache.user_cache_key(firebase_uid)   # "user:fb:{uid}"
RedisCache.organization_cache_key(org_id) # "org:{org_id}"
RedisCache.membership_cache_key(u, o)     # "membership:{user}:{org}"
```

### Firebase Service

Verificação de tokens Firebase ID.

```python
from src.shared.infrastructure.firebase import FirebaseService

service = FirebaseService(settings)
service.initialize()

# Verifica token
token_info = service.verify_token(token, check_revoked=True)
# token_info.uid, token_info.email, token_info.email_verified, token_info.exp
```

**Erros:**
- `InvalidTokenError` - Token inválido ou malformado
- `ExpiredTokenError` - Token expirado
- `RevokedTokenError` - Token revogado
- `FirebaseAuthError` - Outros erros de autenticação

### Email Service

Envio de emails via Resend.

```python
from src.shared.infrastructure.email import EmailService

service = EmailService(settings)

await service.send_email(
    to="user@example.com",
    subject="Assunto",
    html="<h1>Conteúdo</h1>",
    reply_to="support@example.com",
    cc=["cc@example.com"],
    tags=[{"name": "type", "value": "notification"}],
)
```

### Message Broker

LavinMQ/RabbitMQ para processamento assíncrono via FastStream.

```python
from src.shared.infrastructure.messaging import broker

# Usado pelos workers em src/workers/
```

## Schemas Comuns

### ErrorResponse

Resposta de erro padronizada.

```python
from src.shared.domain.schemas import ErrorResponse

{
    "code": "AUTH_INVALID_TOKEN",
    "message": "Token de autenticação inválido",
    "details": {"hint": "Faça login novamente"}
}
```

### HealthResponse

Resposta de health check.

```python
from src.shared.domain.schemas import HealthResponse

{
    "status": "healthy",
    "version": "1.0.0",
    "environment": "production"
}
```

### PaginatedResponse

Re-exportado de `fastapi_restkit.pagination`.

```python
from src.shared.domain.schemas import PaginatedResponse

{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 25,
    "pages": 4
}
```

## Rotas Compartilhadas

### Specialties (Global, Read-Only)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/specialties` | Lista paginada com filtros |
| GET | `/specialties/search?q={term}` | Busca fuzzy |
| GET | `/specialties/code/{code}` | Busca por código |
| GET | `/specialties/{id}` | Busca por ID |

### Document Types (Organization-Scoped)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/document-types` | Criar tipo |
| GET | `/document-types` | Lista paginada |
| GET | `/document-types/all` | Lista tudo (cached) |
| GET | `/document-types/{id}` | Busca por ID |
| PATCH | `/document-types/{id}` | Atualizar tipo |
| POST | `/document-types/{id}/activate` | Ativar |
| POST | `/document-types/{id}/deactivate` | Desativar |
| DELETE | `/document-types/{id}` | Deletar (soft) |

### Enums

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/enums/professional-types` | Tipos de profissional com labels |

## FilterSet e SortingSet

### SpecialtyFilter

```python
from src.shared.infrastructure.filters import SpecialtyFilter

class Config:
    field_columns = {"search": ["code", "name"]}
```

| Filtro | Tipo | Descrição |
|--------|------|-----------|
| search | str | Busca em code e name (trigram) |

### SpecialtySorting

```python
from src.shared.infrastructure.filters import SpecialtySorting

class Config:
    default_sorting = ["name:asc"]
```

| Campo | Descrição |
|-------|-----------|
| id | UUID (time-ordered) |
| code | Código |
| name | Nome (default) |

### DocumentTypeFilter

```python
from src.shared.infrastructure.filters import DocumentTypeFilter

class Config:
    field_columns = {
        "search": ["name"],
        "category": "category",
        "is_active": "is_active",
    }
```

| Filtro | Tipo | Descrição |
|--------|------|-----------|
| search | str | Busca por nome |
| category | DocumentCategory | Filtrar por categoria |
| is_active | bool | Filtrar por status |

### DocumentTypeSorting

```python
from src.shared.infrastructure.filters import DocumentTypeSorting

class Config:
    default_sorting = ["display_order:asc", "name:asc"]
```

| Campo | Descrição |
|-------|-----------|
| id | UUID |
| name | Nome |
| display_order | Ordem de exibição (default) |
| created_at | Data de criação |

## Use Cases

### Specialty (Read-Only)

| Use Case | Descrição |
|----------|-----------|
| `ListSpecialtiesUseCase` | Lista paginada |
| `SearchSpecialtiesUseCase` | Busca por nome |
| `GetSpecialtyUseCase` | Busca por ID |
| `GetSpecialtyByCodeUseCase` | Busca por código |

### DocumentType (CRUD)

| Use Case | Descrição |
|----------|-----------|
| `CreateDocumentTypeUseCase` | Criar tipo |
| `UpdateDocumentTypeUseCase` | Atualizar (PATCH) |
| `DeleteDocumentTypeUseCase` | Soft delete |
| `ListDocumentTypesUseCase` | Lista paginada |
| `ListAllDocumentTypesUseCase` | Lista tudo (cached) |
| `GetDocumentTypeUseCase` | Busca por ID |
| `ToggleActiveDocumentTypeUseCase` | Ativar/desativar |

## Convenções de Uso

### Importando Models

```python
from src.shared.domain.models import (
    # Mixins
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    SoftDeleteMixin,
    AddressMixin,
    VersionMixin,
    VerificationMixin,
    
    # Fields
    AwareDatetimeField,
    CPFField,
    CNPJField,
    PhoneField,
    
    # Enums
    AccountType,
    PixKeyType,
    DocumentCategory,
    
    # Models
    Specialty,
    DocumentType,
    Bank,
    BankAccount,
    Company,
)
```

### Importando Value Objects

```python
from src.shared.domain.value_objects import (
    CPF,
    CNPJ,
    CPFOrCNPJ,
    Phone,
    PostalCode,
    StateUF,
    BRAZILIAN_STATES,
)
```

### Importando Repositories

```python
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeleteMixin,
    OrganizationScopeMixin,
    ScopePolicy,
)
```

### Importando Schemas

```python
from src.shared.domain.schemas import (
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    PaginationParams,
)
```

## Diagrama de Dependências

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  SHARED MODULE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────┐     ┌─────────────────────┐     ┌──────────────────┐   │
│  │   Domain       │     │   Infrastructure    │     │   Presentation   │   │
│  ├────────────────┤     ├─────────────────────┤     ├──────────────────┤   │
│  │ • models/      │────▶│ • repositories/     │────▶│ • routes/        │   │
│  │ • schemas/     │     │ • filters/          │     │ • dependencies/  │   │
│  │ • value_objects│     │ • cache/            │     └──────────────────┘   │
│  │ • events/      │     │ • database/         │                            │
│  └────────────────┘     │ • firebase/         │     ┌──────────────────┐   │
│                         │ • email/            │     │   Use Cases      │   │
│                         │ • messaging/        │────▶├──────────────────┤   │
│                         └─────────────────────┘     │ • specialty/     │   │
│                                                     │ • document_type/ │   │
│                                                     └──────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DOMAIN MODULES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Users                                                                    │
│  • Organizations                                                            │
│  • Professionals                                                            │
│  • Screening                                                                │
│  • Contracts                                                                │
│  • Units                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `domain/models/base.py` | BaseModel, naming conventions |
| `domain/models/mixins.py` | Todos os mixins de modelo |
| `domain/models/fields.py` | Custom field helpers |
| `domain/value_objects/__init__.py` | Exports de value objects |
| `infrastructure/repositories/base.py` | BaseRepository |
| `infrastructure/repositories/mixins.py` | SoftDeleteMixin (repo) |
| `infrastructure/repositories/organization_scope_mixin.py` | OrganizationScopeMixin |
| `infrastructure/cache/redis_cache.py` | RedisCache service |
| `infrastructure/database/connection.py` | Async engine e session |
| `infrastructure/firebase/firebase_service.py` | Firebase token verification |
| `infrastructure/email/email_service.py` | Resend email service |
| `infrastructure/messaging/broker.py` | LavinMQ/RabbitMQ broker |
| `presentation/dependencies/__init__.py` | Re-exports de dependencies |
| `presentation/routes/specialty_routes.py` | Rotas de especialidades |
| `presentation/routes/document_type_routes.py` | Rotas de tipos de documento |
