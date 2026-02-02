# Code Review: Consolidação do Upload de Documentos

**Data:** 2026-02-02  
**Revisor:** GitHub Copilot  
**Branch/PR:** N/A (revisão de mudanças locais)  
**Status:** ⚠️ Aprovado com ressalvas

---

## Resumo das Mudanças

Esta alteração consolida o fluxo de upload de documentos na triagem (screening), movendo a responsabilidade de upload para o Firebase Storage do frontend para o backend. Anteriormente, o frontend fazia upload direto ao Firebase e enviava o `professional_document_id` já criado. Agora, o backend recebe o arquivo via `multipart/form-data` e faz todo o processo internamente.

### Arquivos Modificados

| Arquivo | Tipo de Mudança |
|---------|-----------------|
| `src/modules/screening/use_cases/screening_step/document_upload/upload_document_use_case.py` | Refatoração completa |
| `src/shared/infrastructure/firebase/storage_service.py` | **Novo arquivo** |
| `src/shared/infrastructure/filters/base.py` | **Novo arquivo** |
| `src/modules/professionals/infrastructure/repositories/professional_qualification_repository.py` | Novo método |
| `src/modules/screening/infrastructure/repositories/step_repositories.py` | Novo método |
| `src/modules/screening/domain/schemas/steps/document_upload_step.py` | Schema renomeado |
| `src/modules/screening/presentation/routes/screening_document_routes.py` | Parâmetros de rota |
| `src/modules/screening/presentation/routes/screening_public_routes.py` | Parâmetros de rota |
| `src/app/config.py` | Nova configuração |
| `docs/bruno/screenings/documents/upload-document.bru` | Documentação |
| `docs/bruno/screenings/public/public-upload-document.bru` | Documentação |
| `docs/modules/SCREENING_MODULE.md` | Documentação |

---

## Análise Detalhada

### ✅ Pontos Positivos

#### 1. Arquitetura Consolidada
O fluxo agora é mais simples e seguro:
- Frontend envia arquivo → Backend faz upload, cria documento, vincula ao screening
- Remove necessidade de múltiplas chamadas do frontend
- Melhor controle de transações e consistência

#### 2. FirebaseStorageService Bem Estruturado
```python
@dataclass(frozen=True, slots=True)
class UploadedFile:
    url: str
    path: str
    content_type: str
    size: int
```
- Uso de `dataclass(frozen=True, slots=True)` para eficiência e imutabilidade
- Path bem organizado: `organizations/{org_id}/professionals/{prof_id}/screenings/{scr_id}/...`
- Validação de tipos MIME e tamanho de arquivo
- Logs estruturados

#### 3. Inferência Automática de Vínculos
Lógica clara para inferir `qualification_id` e `specialty_id`:

| Categoria | qualification_id | specialty_id |
|-----------|------------------|--------------|
| PROFILE | null | null |
| QUALIFICATION | primary/first qualification | null |
| SPECIALTY | primary/first qualification | expected_specialty_id |

#### 4. ExcludeListFilter Genérico
Filtro reutilizável para cláusulas NOT IN com validação automática de tipos:
```python
class ExcludeListFilter(BaseModel, Generic[T]):
    values: list[T] | None = Field(...)
```

#### 5. Documentação Atualizada
- Arquivos `.bru` com exemplos corretos de `multipart/form-data`
- Tabela de error codes documentada
- Fluxo consolidado descrito no `SCREENING_MODULE.md`

---

### ⚠️ Problemas Identificados

#### 🔴 CRÍTICO: Operações Síncronas Bloqueantes

**Arquivo:** `src/shared/infrastructure/firebase/storage_service.py`  
**Linhas:** 217-220, 253-268

O método `upload_file` é declarado como `async` mas as operações do Firebase SDK são síncronas, bloqueando o event loop:

```python
async def upload_file(self, ...) -> UploadedFile:
    # ...
    content = file.read()  # ❌ Bloqueante
    blob.upload_from_string(content, ...)  # ❌ Bloqueante
```

**Correção sugerida:**
```python
import asyncio

async def upload_file(self, ...) -> UploadedFile:
    # ...
    content = await asyncio.to_thread(file.read)
    await asyncio.to_thread(
        blob.upload_from_string,
        content,
        content_type=validated_content_type,
    )
```

**Impacto:** Sob carga, pode causar timeouts e degradação de performance.

---

#### 🟡 MODERADO: Signed URL com Validade de 1 Ano

**Arquivo:** `src/shared/infrastructure/firebase/storage_service.py`  
**Linhas:** 224-228

```python
url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(days=365),
    method="GET",
)
```

**Problema:** Documentos sensíveis (RG, CPF, diplomas) ficam acessíveis por muito tempo.

**Sugestões:**
1. Usar URLs de curta duração (ex: 1 hora) regeneradas sob demanda
2. Ou implementar um proxy de download que verifica permissões

---

#### 🟡 MODERADO: Falta Tratamento de Exceções do Firebase

**Arquivo:** `src/modules/screening/use_cases/screening_step/document_upload/upload_document_use_case.py`  
**Linhas:** 140-151

```python
# 7. Upload file to Firebase Storage
uploaded_file = await self.storage_service.upload_file(...)  # Pode falhar
```

**Problema:** Se o Firebase falhar, uma exceção genérica vaza para o usuário.

**Correção sugerida:**
```python
from google.cloud.exceptions import GoogleCloudError

try:
    uploaded_file = await self.storage_service.upload_file(...)
except GoogleCloudError as e:
    logger.error("firebase_upload_failed", error=str(e))
    raise ValidationError(
        message="Falha ao fazer upload do arquivo. Tente novamente.",
    )
```

---

#### 🟢 MENOR: Import Dentro de Método

**Arquivo:** `src/shared/infrastructure/filters/base.py`  
**Linhas:** 54-55, 68-69

```python
if field_info and hasattr(field_info, "annotation"):
    import typing  # ❌ Import dentro do método
```

**Sugestão:** Mover para o topo do arquivo.

---

### 🔍 Melhorias Futuras Sugeridas

#### 1. Rollback em Caso de Falha
Se a criação do `ProfessionalDocument` falhar após o upload, o arquivo fica órfão no Firebase.

**Opções:**
- Implementar cleanup com `try/finally`
- Job periódico de limpeza de arquivos órfãos
- Aceitar como dívida técnica documentada

#### 2. Validação de `file.size`
```python
file_size = file.size or 0  # Se None, passa com 0 e falha depois
```

Considerar ler o arquivo para determinar o tamanho se `file.size` for `None`.

#### 3. Exportar Constantes
`ALLOWED_MIME_TYPES` e `MAX_FILE_SIZE` podem ser exportados para uso em validação nos schemas da rota.

---

## Checklist de Revisão

- [x] Código segue os padrões do projeto
- [x] Documentação atualizada
- [x] Schemas e DTOs corretos
- [x] Repositórios seguem padrões de mixins
- [x] Use cases com responsabilidade única
- [ ] **Operações async são realmente async** ⚠️
- [ ] **Tratamento de exceções adequado** ⚠️
- [x] Logs estruturados
- [x] Testes (não verificados neste review)

---

## Decisão

| Aspecto | Status |
|---------|--------|
| Funcionalidade | ✅ Correta |
| Arquitetura | ✅ Boa |
| Performance | ⚠️ Precisa correção (operações bloqueantes) |
| Segurança | ⚠️ Considerar URLs de curta duração |
| Documentação | ✅ Completa |

### Recomendação

**Aprovado com ressalvas.** As mudanças podem ser mergeadas, mas os seguintes itens devem ser endereçados:

1. **Antes do merge (blocker):**
   - Corrigir operações síncronas no `FirebaseStorageService` usando `asyncio.to_thread()`

2. **Após o merge (follow-up):**
   - Adicionar tratamento de exceções do Firebase
   - Avaliar política de signed URLs
   - Mover imports para o topo do arquivo

---

## Referências

- [FastAPI UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [asyncio.to_thread()](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
