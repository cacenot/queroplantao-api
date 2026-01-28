# Fase 2: Sync de Qualifications + Nested Entities

## Objetivo

Expandir o `SnapshotApplierService` para suportar sync de qualifications, specialties e educations. Extrair lógica reutilizável do composite use case existente.

## Pré-requisitos

- Fase 1 completa e funcionando
- Endpoints de versão operacionais

## Contexto

### Código Existente para Reutilizar

O `UpdateOrganizationProfessionalCompositeUseCase` em `src/modules/professionals/use_cases/organization_professional/organization_professional_update_composite_use_case.py` já implementa:

- Lógica de sync para qualifications (create/update/delete)
- Lógica de sync para specialties aninhadas
- Lógica de sync para educations aninhadas
- Estratégia de identificação: ID presente = update, ID ausente = create, ID não na lista = delete

### Entidades Envolvidas

```
ProfessionalQualification (1:N do Professional)
├── ProfessionalSpecialty (1:N da Qualification)
│   └── Specialty (N:1 - lookup global)
└── ProfessionalEducation (1:N da Qualification)
```

---

## Tarefas

### 1. Extrair Service de Sync de Qualifications

**Novo arquivo**: `src/modules/professionals/use_cases/shared/services/qualification_sync_service.py`

Extrair a lógica de sync do composite use case para um service reutilizável:

```python
class QualificationSyncService:
    """Syncs qualification data between snapshot and entities."""
    
    async def sync_qualifications(
        self,
        professional_id: UUID,
        organization_id: UUID,
        qualifications_data: list[QualificationInput],
        updated_by: UUID,
    ) -> list[ProfessionalQualification]:
        """Sync qualifications with nested specialties and educations."""
```

**Referência**: Métodos `_sync_qualifications`, `_sync_qualification_specialties`, `_sync_qualification_educations` em `organization_professional_update_composite_use_case.py`

### 2. Refatorar Composite Use Case

**Arquivo**: `src/modules/professionals/use_cases/organization_professional/organization_professional_update_composite_use_case.py`

- Remover métodos privados de sync
- Injetar e usar `QualificationSyncService`
- Manter comportamento idêntico

### 3. Expandir SnapshotApplierService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/snapshot_applier_service.py`

Adicionar:
- `_apply_qualifications()` - Usa `QualificationSyncService`
- Remover qualifications da validação de features não suportadas

### 4. Atualizar Schemas de Versão

**Arquivo**: `src/modules/professionals/domain/schemas/version_schemas.py`

Garantir que `QualificationInput` está completo com:
- Todos os campos de `ProfessionalQualification`
- `specialties: list[SpecialtyInput]` aninhado
- `educations: list[EducationInput]` aninhado

### 5. Atualizar SnapshotBuilderService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/snapshot_builder_service.py`

Garantir que `build_snapshot()` inclui qualifications com nested data.

### 6. Atualizar DiffCalculatorService

**Arquivo**: `src/modules/professionals/use_cases/professional_version/services/diff_calculator_service.py`

Garantir que calcula diffs para:
- `qualifications[N].field`
- `qualifications[N].specialties[M].field`
- `qualifications[N].educations[M].field`

---

## Validações

- Composite use case continua funcionando igual (não quebrar regressão)
- Aplicar versão com qualifications funciona corretamente
- Diffs são calculados para todos os níveis de aninhamento

## Testes

- Testar sync de qualification nova
- Testar update de qualification existente
- Testar remoção de qualification
- Testar sync de specialties aninhadas
- Testar sync de educations aninhadas

## Entregáveis

- [ ] `QualificationSyncService` extraído
- [ ] Composite use case refatorado
- [ ] `SnapshotApplierService` com `_apply_qualifications()`
- [ ] Schemas de qualification completos
- [ ] SnapshotBuilder incluindo qualifications
- [ ] DiffCalculator para qualifications nested
- [ ] Testes de regressão passando
