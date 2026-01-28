# Fase 3: Sync de Payment Data (Bank Accounts + Companies)

## Objetivo

Completar o `SnapshotApplierService` com suporte a bank accounts e companies. Criar infraestrutura necessária para Company upsert.

## Pré-requisitos

- Fase 1 e 2 completas
- `SnapshotApplierService` suportando personal_info e qualifications

## Contexto

### Entidades Envolvidas

```
BankAccount (1:N do Professional)
└── Bank (N:1 - lookup global por código)

ProfessionalCompany (1:N do Professional)
└── Company (N:1 - upsert por CNPJ)
```

### Complexidades

1. **BankAccount**: Precisa criar `BankAccountRepository` (não existe)
2. **Company**: Pode precisar criar Company se não existir (upsert por CNPJ)
3. **Bank**: Lookup apenas, não cria (dados de referência)

---

## Tarefas

### 1. Criar BankAccountRepository

**Novo arquivo**: `src/modules/professionals/infrastructure/repositories/bank_account_repository.py`

Métodos necessários:
- `list_for_professional(professional_id, organization_id)`
- `get_by_id_for_professional(id, professional_id, organization_id)`
- `create(bank_account)`
- `create_many(bank_accounts)`
- `update(bank_account)`
- `soft_delete(id)`
- `soft_delete_many(ids)`

**Referência**: Padrão em outros repositories do módulo

### 2. Adicionar Company Upsert

**Arquivo**: `src/modules/professionals/infrastructure/repositories/company_repository.py`

Adicionar método:
```python
async def get_or_create_by_cnpj(
    self,
    cnpj: str,
    company_data: CompanyCreate,
    created_by: UUID,
) -> tuple[Company, bool]:
    """Returns (company, was_created)."""
```

### 3. Criar BankAccountSyncService

**Novo arquivo**: `src/modules/professionals/use_cases/shared/services/bank_account_sync_service.py`

```python
class BankAccountSyncService:
    """Syncs bank account data between snapshot and entities."""
    
    async def sync_bank_accounts(
        self,
        professional_id: UUID,
        organization_id: UUID,
        bank_accounts_data: list[BankAccountInput],
        updated_by: UUID,
    ) -> list[BankAccount]:
```

Comportamento:
- Lookup de Bank por código
- Validar que Bank existe (ou lançar exception)
- Sync padrão: create/update/delete

### 4. Criar CompanySyncService

**Novo arquivo**: `src/modules/professionals/use_cases/shared/services/company_sync_service.py`

```python
class CompanySyncService:
    """Syncs company data between snapshot and entities."""
    
    async def sync_companies(
        self,
        professional_id: UUID,
        organization_id: UUID,
        companies_data: list[CompanyInput],
        updated_by: UUID,
    ) -> list[ProfessionalCompany]:
```

Comportamento:
- Para cada company no snapshot:
  - Buscar Company por CNPJ
  - Se não existe, criar Company
  - Criar/atualizar ProfessionalCompany (junction)
- Remover ProfessionalCompany para companies não no snapshot

### 5. Expandir SnapshotApplierService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/snapshot_applier_service.py`

Adicionar:
- `_apply_bank_accounts()` - Usa `BankAccountSyncService`
- `_apply_companies()` - Usa `CompanySyncService`
- Remover bank_accounts e companies da validação de features não suportadas
- `_validate_snapshot_support()` pode ser removido quando tudo estiver suportado

### 6. Atualizar Schemas de Versão

**Arquivo**: `src/modules/professionals/domain/schemas/version_schemas.py`

Garantir que estão completos:
- `BankAccountInput` com todos os campos necessários
- `CompanyInput` com dados da Company + dados do vínculo (ProfessionalCompany)

### 7. Atualizar SnapshotBuilderService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/snapshot_builder_service.py`

Garantir que `build_snapshot()` inclui:
- `bank_accounts` com dados do Bank
- `companies` com dados da Company + vínculo

### 8. Atualizar DiffCalculatorService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/diff_calculator_service.py`

Garantir que calcula diffs para:
- `bank_accounts[N].field`
- `companies[N].field`

---

## Considerações Especiais

### Bank Lookup

- Banks são dados de referência (seed)
- Se código do banco não existir, lançar exception clara
- Não criar banco automaticamente

### Company Upsert

- Company é identificada por CNPJ
- Se CNPJ existe: usar Company existente, opcionalmente atualizar dados
- Se CNPJ não existe: criar Company nova
- ProfessionalCompany é o vínculo (junction table)

### Validações

- CNPJ válido (já validado pelo value object)
- Código do banco existe
- Dados bancários consistentes (agência, conta, dígitos)

---

## Validações

- `SnapshotApplierService` suporta todos os tipos de dados
- `_validate_snapshot_support()` não lança mais exceptions
- Aplicar versão completa funciona

## Testes

- Testar sync de bank account novo
- Testar update de bank account existente
- Testar remoção de bank account
- Testar criação de Company via upsert
- Testar uso de Company existente
- Testar sync de ProfessionalCompany

## Entregáveis

- [ ] `BankAccountRepository` criado
- [ ] `Company.get_or_create_by_cnpj()` implementado
- [ ] `BankAccountSyncService` criado
- [ ] `CompanySyncService` criado
- [ ] `SnapshotApplierService` completo
- [ ] Schemas de payment data completos
- [ ] SnapshotBuilder incluindo payment data
- [ ] DiffCalculator para payment data
- [ ] Remover `_validate_snapshot_support()` ou torná-lo no-op
- [ ] Testes completos

---

## Conclusão

Após esta fase, o sistema de versionamento estará completo e poderá:
- Criar versões com snapshot completo de qualquer profissional
- Aplicar versões pendentes (de screening ou outras fontes)
- Rejeitar versões com motivo
- Manter histórico completo de alterações com diffs granulares
