# Code Review: DocumentUploadStep - Campo `is_configured`

**Data:** 2026-02-02  
**Autor:** GitHub Copilot  
**Módulo:** Screening - Document Upload Step

## Resumo

Implementação da flag `is_configured` no `DocumentUploadStep` para controlar o fluxo de duas fases do step de upload de documentos, impedindo upload/reutilização/complete antes da configuração e bloqueando reconfiguração após a configuração inicial.

## Problema

O fluxo anterior permitia:
- Upload de documentos antes de serem configurados (lista de documentos vazia)
- Reconfiguração de documentos após já ter começado os uploads
- Ambiguidade sobre quando o step estava pronto para receber uploads

## Solução Implementada

### Nova Flag `is_configured`

Adicionado campo booleano `is_configured` ao modelo `DocumentUploadStep`:

- **Valor inicial:** `false`
- **Transição:** `false → true` quando `/configure` é chamado
- **Imutável:** Uma vez `true`, não pode voltar para `false`

### Fluxo de Duas Fases

```
Fase 1 (is_configured = false)    Fase 2 (is_configured = true)
───────────────────────────────   ───────────────────────────────
✅ Configure                      ❌ Configure (erro 409)
❌ Upload (erro 422)              ✅ Upload
❌ Reuse (erro 422)               ✅ Reuse
❌ Complete (erro 422)            ✅ Complete
```

## Arquivos Modificados

### Modelo e Migração

| Arquivo | Mudança |
|---------|---------|
| `domain/models/steps/document_upload_step.py` | Adicionado `is_configured: bool = Field(default=False)` e propriedade `all_required_uploaded` |
| `domain/schemas/steps/document_upload_step.py` | Adicionado `is_configured: bool = False` no response schema |
| `alembic/versions/000000000015_*.py` | Nova migração para adicionar coluna |

### Error Codes e i18n

| Arquivo | Mudança |
|---------|---------|
| `app/constants/error_codes.py` | Adicionados `SCREENING_STEP_NOT_CONFIGURED`, `SCREENING_STEP_ALREADY_CONFIGURED` |
| `app/i18n/messages.py` | Adicionadas keys de mensagem |
| `app/i18n/locales/pt_br.py` | Adicionadas traduções pt-BR |
| `app/exceptions/screening_exceptions.py` | Novas classes de exceção |
| `app/exceptions/__init__.py` | Re-exports |

### Use Cases Atualizados

| Arquivo | Mudança |
|---------|---------|
| `use_cases/screening_step/document_upload/configure_documents_use_case.py` | Valida `is_configured=false`, define `is_configured=true` após sucesso |
| `use_cases/screening_step/document_upload/upload_document_use_case.py` | Valida `is_configured=true` antes de permitir upload |
| `use_cases/screening_step/document_upload/reuse_document_use_case.py` | Valida `is_configured=true` antes de permitir reutilização |
| `use_cases/screening_step/document_upload/complete_document_upload_step_use_case.py` | Valida `is_configured=true` antes de permitir complete |

### Refatoração: DRY

| Arquivo | Mudança |
|---------|---------|
| `infrastructure/repositories/screening_document_repository.py` | Novo método `count_uploaded_documents(step_id)` |
| `upload_document_use_case.py` | Removido método duplicado `_count_uploaded_documents`, usa repositório |
| `reuse_document_use_case.py` | Removido método duplicado `_count_uploaded_documents`, usa repositório |

### Documentação Atualizada

| Arquivo | Mudança |
|---------|---------|
| `docs/modules/SCREENING_MODULE.md` | Atualizado fluxo de documentos, tabelas, error codes, guia de frontend |
| `docs/bruno/screenings/steps/configure-documents.bru` | Documentação de fases e error codes |
| `docs/bruno/screenings/steps/complete-document-upload.bru` | Novo error code |
| `docs/bruno/screenings/documents/upload-document.bru` | Novo error code e pré-requisitos |
| `docs/bruno/screenings/documents/reuse-document.bru` | Novo error code e pré-requisitos |
| `docs/bruno/screenings/public/public-upload-document.bru` | Novo error code |

## Error Codes

| Código | Status HTTP | Contexto |
|--------|-------------|----------|
| `SCREENING_STEP_NOT_CONFIGURED` | 422 | Upload, Reuse, Complete quando `is_configured=false` |
| `SCREENING_STEP_ALREADY_CONFIGURED` | 409 | Configure quando `is_configured=true` |

## Mensagens i18n (pt-BR)

| Key | Mensagem |
|-----|----------|
| `STEP_NOT_CONFIGURED` | "A etapa ainda não foi configurada. Configure os documentos antes de prosseguir." |
| `STEP_ALREADY_CONFIGURED` | "A etapa já foi configurada. Não é possível reconfigurar os documentos." |

## Testes

### Cenários a Validar

1. **Configure quando is_configured=false** → ✅ Sucesso, is_configured=true
2. **Configure quando is_configured=true** → ❌ Erro 409 ALREADY_CONFIGURED
3. **Upload quando is_configured=false** → ❌ Erro 422 NOT_CONFIGURED
4. **Upload quando is_configured=true** → ✅ Sucesso
5. **Reuse quando is_configured=false** → ❌ Erro 422 NOT_CONFIGURED
6. **Reuse quando is_configured=true** → ✅ Sucesso
7. **Complete quando is_configured=false** → ❌ Erro 422 NOT_CONFIGURED
8. **Complete quando is_configured=true** → ✅ Sucesso

## Impacto no Frontend

O frontend deve:

1. **Verificar `is_configured`** no response do step para determinar qual UI mostrar
2. **Fase 1:** Mostrar interface de seleção de tipos de documento
3. **Fase 2:** Mostrar interface de upload com lista de documentos configurados
4. **Tratar erros 409/422** dos novos códigos de erro

## Notas de Migração

- A migração adiciona coluna `is_configured BOOLEAN DEFAULT FALSE NOT NULL`
- Triagens existentes terão `is_configured=false`, o que está correto pois steps já em andamento continuarão funcionando normalmente
- Para triagens novas, o fluxo de duas fases será obrigatório

## Decisões de Design

1. **Não permitir reconfiguração:** Simplifica o fluxo e evita edge cases complexos
2. **is_configured como flag booleana:** Mais simples que adicionar novo status enum
3. **Validação no use case:** Mantém regras de negócio fora do repositório
4. **Refatoração DRY:** `count_uploaded_documents` movido para repositório para evitar duplicação
