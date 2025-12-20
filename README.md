"""README - Quero Plantão API."""

# Quero Plantão API

REST API para gestão de plantões médicos - Infraestrutura escalável de HR Tech para ecossistema médico.

## Stack Tecnológico

- **Python 3.12+**
- **FastAPI** - Framework web moderno e performático
- **SQLModel** - ORM com Pydantic integrado
- **PostgreSQL** - Banco de dados relacional
- **FastStream + LavinMQ** - Workers assíncronos e mensageria
- **Alembic** - Gerenciamento de migrations
- **uv** - Gerenciador de pacotes ultra-rápido
- **Ruff** - Linting e formatação

## Arquitetura

Clean Architecture com camadas bem definidas:

```
app/
├── core/                    # Configurações, segurança, contexto
├── domain/                  # Modelos, schemas, eventos, serviços
├── infrastructure/          # Repositórios, banco de dados, mensageria
├── presentation/            # Routers e endpoints FastAPI
├── use_cases/               # Orquestração de fluxos
└── workers/                 # Consumidores de eventos (FastStream)
```

## Multi-tenancy

- Implementado via `tenant_id` em todas as tabelas de dados de tenant
- Isolamento automático via `TenantRepository` base
- JWT interno carrega `tenant_id` do BFF
- Context vars para acesso em qualquer camada

## Configuração

### Instalação

```bash
# Clonar repositório
git clone <repo>
cd queroplantao-api

# Instalar dependências
make install

# Ou com extras de desenvolvimento
make dev
```

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

### Docker

Inicie os serviços (PostgreSQL + LavinMQ):

```bash
make docker-up
```

Parar:

```bash
make docker-down
```

## Desenvolvimento

### Rodar a API

```bash
make run
# ou
uv run uvicorn app.main:app --reload
```

API estará disponível em `http://localhost:8000`

Documentação: `http://localhost:8000/docs` (em development)

### Rodar Workers

```bash
make worker
# ou
uv run python -m app.workers.main
```

### Testes

```bash
# Rodar testes
make test

# Com coverage
make test-cov
```

### Qualidade de Código

```bash
# Lint
make lint

# Formatar
make format

# Pre-commit
make pre-commit-install
make pre-commit
```

## Migrations

```bash
# Criar migration
make migrate-create msg="descrição"

# Aplicar migrations
make migrate

# Reverter última migration
make migrate-rollback
```

## Estrutura de Projetos

### Endpoints

Todos os endpoints versionados com `/api/v1/` prefix:

- `GET /health` - Health check
- `GET /api/v1/...` - Endpoints de negócio (a implementar)

### Autenticação

JWT interno recebido do BFF no header `Authorization: Bearer <token>`

Claims esperados:
```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "roles": ["role1", "role2"],
  "exp": 1234567890
}
```

## Contribuindo

1. Instale pre-commit hooks: `make pre-commit-install`
2. Crie uma branch: `git checkout -b feature/sua-feature`
3. Commit mudanças: `git commit -am "feat: descrição"`
4. Push: `git push origin feature/sua-feature`
5. Abra um Pull Request

## Licença

MIT
