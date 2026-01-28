# Fase 1: Infraestrutura de Versionamento + Personal Info

## Objetivo

Implementar a infraestrutura completa de versionamento de profissionais, incluindo schemas, repositories, services e use cases. O `SnapshotApplierService` deve suportar apenas `personal_info` nesta fase.

## Contexto

- **Modelos existentes**: `ProfessionalVersion`, `ProfessionalChangeDiff` em `src/modules/professionals/domain/models/`
- **TypeDicts para snapshot**: `version_snapshot.py` define a estrutura do `data_snapshot` JSONB
- **Enums**: `SourceType`, `ChangeType` em `src/modules/screening/domain/models/enums.py`
- **Padrões a seguir**: Ver `.github/copilot-instructions.md`

## Decisões de Design

### TypedDict vs Pydantic

- **TypedDict** (manter): Para tipagem do `data_snapshot` JSONB no storage
- **Pydantic** (criar): Schemas de input para validação na API, convertidos para dict antes de salvar

### Validação

- Validar regras de negócio (CPF único, council registration) no `CreateProfessionalVersionUseCase`
- Isso evita criar versões inválidas que falhariam na aplicação

### Entidades não suportadas

- Se snapshot contiver `qualifications`, `companies` ou `bank_accounts`, lançar exception clara indicando que não é suportado ainda

---

## Tarefas

### 1. Error Codes e Exceptions

**Arquivo**: `src/app/constants/error_codes.py`

Adicionar ao `ProfessionalErrorCodes`:
- `PROF_VERSION_NOT_FOUND` - Versão não encontrada
- `PROF_VERSION_ALREADY_APPLIED` - Versão já foi aplicada
- `PROF_VERSION_ALREADY_REJECTED` - Versão já foi rejeitada
- `PROF_VERSION_NOT_PENDING` - Versão não está pendente (para apply/reject)
- `PROF_VERSION_FEATURE_NOT_SUPPORTED` - Feature do snapshot não suportada ainda

**Arquivo**: `src/app/exceptions/professional_exceptions.py`

Criar exceptions correspondentes seguindo o padrão existente.

### 2. Mensagens i18n

**Arquivos**: `src/app/i18n/messages.py` e `src/app/i18n/locales/pt_br.py`

Adicionar mensagens em português para cada nova exception.

### 3. Schemas Pydantic

**Arquivo**: `src/modules/professionals/domain/schemas/version_schemas.py`

Criar schemas de input que espelham os TypeDicts:

```
PersonalInfoInput          → Valida dados pessoais
QualificationInput         → Valida qualificação (com specialties/educations aninhados)
CompanyInput               → Valida empresa
BankAccountInput           → Valida conta bancária
ProfessionalVersionCreate  → Schema principal de criação
ProfessionalVersionResponse → Response com dados da versão
ProfessionalChangeDiffResponse → Response dos diffs
```

**Referências**:
- TypeDicts em `src/modules/professionals/domain/models/version_snapshot.py`
- Schemas existentes em `src/modules/professionals/domain/schemas/`

### 4. Repositories

**Arquivo**: `src/modules/professionals/infrastructure/repositories/professional_version_repository.py`

Métodos necessários:
- `get_by_id(version_id)` - Buscar versão por ID
- `get_by_id_for_organization(version_id, organization_id)` - Com validação de tenant
- `get_current_for_professional(professional_id, organization_id)` - Versão atual (is_current=True)
- `get_pending_for_professional(professional_id, organization_id)` - Versões pendentes
- `list_for_professional(professional_id, organization_id, pagination)` - Histórico paginado
- `create(version)` - Criar nova versão
- `mark_as_current(version_id)` - Marcar como atual
- `mark_previous_as_not_current(professional_id, exclude_version_id)` - Desmarcar anteriores

**Arquivo**: `src/modules/professionals/infrastructure/repositories/professional_change_diff_repository.py`

Métodos necessários:
- `create_many(diffs)` - Criar múltiplos diffs de uma vez
- `list_for_version(version_id)` - Listar diffs de uma versão

**Referência**: Padrão de repository em `src/modules/professionals/infrastructure/repositories/organization_professional_repository.py`

### 5. Services

**Diretório**: `src/modules/professionals/use_cases/professional_version/services/`

#### DiffCalculatorService

Compara dois snapshots e retorna lista de `ProfessionalChangeDiff`:
- Detecta campos ADDED (existe no novo, não no antigo)
- Detecta campos MODIFIED (existe em ambos, valores diferentes)
- Detecta campos REMOVED (existe no antigo, não no novo)
- Gera `field_path` no formato JSON path (ex: `personal_info.email`, `qualifications[0].council_number`)

#### SnapshotBuilderService

Constrói snapshot a partir das entidades atuais do profissional:
- Carrega `OrganizationProfessional` com todas as relações
- Converte para estrutura `ProfessionalDataSnapshot`
- Usado para calcular diffs entre estado atual e nova versão

#### SnapshotApplierService (Fase 1: apenas personal_info)

Aplica snapshot às entidades:
- `_apply_personal_info()` - Atualiza campos do `OrganizationProfessional`
- `_validate_snapshot_support()` - Lança exception se snapshot tiver qualifications/companies/bank_accounts

### 6. Use Cases

**Diretório**: `src/modules/professionals/use_cases/professional_version/`

#### CreateProfessionalVersionUseCase

Input:
- `organization_id: UUID`
- `professional_id: UUID`
- `data: ProfessionalVersionCreate`
- `source_type: SourceType`
- `source_id: UUID | None` (ex: screening_process_id)
- `created_by: UUID`
- `family_org_ids: tuple[UUID, ...]`

Comportamento:
1. Validar que profissional existe
2. Validar regras de negócio (CPF único no family scope, etc.)
3. Construir snapshot atual via `SnapshotBuilderService`
4. Calcular diffs via `DiffCalculatorService`
5. Criar `ProfessionalVersion` com `data_snapshot`
6. Criar `ProfessionalChangeDiff` entries
7. Se `source_type == DIRECT`: chamar `ApplyProfessionalVersionUseCase`
8. Retornar versão criada

#### ApplyProfessionalVersionUseCase

Input:
- `organization_id: UUID`
- `version_id: UUID`
- `applied_by: UUID`

Comportamento:
1. Buscar versão e validar que está pendente
2. Validar suporte do snapshot via `SnapshotApplierService._validate_snapshot_support()`
3. Aplicar snapshot via `SnapshotApplierService.apply_snapshot()`
4. Marcar versões anteriores como `is_current=False`
5. Atualizar versão: `is_current=True`, `applied_at=now()`, `applied_by`
6. Retornar profissional atualizado

#### RejectProfessionalVersionUseCase

Input:
- `organization_id: UUID`
- `version_id: UUID`
- `rejection_reason: str`
- `rejected_by: UUID`

Comportamento:
1. Buscar versão e validar que está pendente
2. Atualizar: `rejected_at=now()`, `rejected_by`, `rejection_reason`
3. Retornar versão rejeitada

### 7. Dependencies e Routes

**Arquivo**: `src/modules/professionals/presentation/dependencies/professional_version.py`

Criar factory functions e type aliases para os 3 use cases.

**Arquivo**: `src/modules/professionals/presentation/routes/professional_version_routes.py`

Endpoints:
- `POST /professionals/{professional_id}/versions` - Criar versão
- `GET /professionals/{professional_id}/versions` - Listar histórico
- `GET /professionals/{professional_id}/versions/{version_id}` - Detalhe da versão
- `POST /professionals/{professional_id}/versions/{version_id}/apply` - Aplicar versão
- `POST /professionals/{professional_id}/versions/{version_id}/reject` - Rejeitar versão

**Referência**: Padrão de routes em `src/modules/professionals/presentation/routes/`

### 8. Atualizar Exports

Atualizar `__init__.py` em:
- `src/modules/professionals/domain/schemas/`
- `src/modules/professionals/infrastructure/repositories/`
- `src/modules/professionals/use_cases/`
- `src/modules/professionals/presentation/dependencies/`
- `src/modules/professionals/presentation/routes/`

### 9. Documentação Bruno

**Diretório**: `docs/bruno/professionals/versions/`

Criar arquivos:
- `folder.bru` - Metadata da pasta
- `create.bru` - POST criar versão
- `list.bru` - GET listar versões
- `get.bru` - GET detalhe da versão
- `apply.bru` - POST aplicar versão
- `reject.bru` - POST rejeitar versão

**Referência**: Padrão em `docs/bruno/professionals/`

---

## Validações e Testes

- Rodar `make lint` após implementação
- Rodar `make test` para garantir que não quebrou nada
- Testar manualmente via Bruno os endpoints criados

## Entregáveis

- [ ] Error codes e exceptions
- [ ] Mensagens i18n
- [ ] Schemas de versão
- [ ] Repositories de versão e diff
- [ ] Services (DiffCalculator, SnapshotBuilder, SnapshotApplier)
- [ ] 3 Use cases (Create, Apply, Reject)
- [ ] Dependencies e routes
- [ ] Exports atualizados
- [ ] Documentação Bruno
