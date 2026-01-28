# API Client Release Guide

## Quick Release

Use o comando interativo para criar uma release:

```bash
make client-release
```

Esse script irá:
1. Mostrar a versão atual
2. Perguntar qual tipo de bump (patch/minor/major/custom)
3. Gerar o client completo
4. Criar commit com a versão
5. Criar tag `api-client-v{version}`
6. Fazer push para o repositório
7. CI/CD publica automaticamente no GitHub Packages

## Processo Manual

### 1. Gerar e testar localmente

```bash
# Gerar tudo
make client-all

# Testar build
cd packages/api-client
pnpm run build
```

### 2. Atualizar versão

```bash
# Patch (0.1.0 → 0.1.1) - bug fixes
make client-version-patch

# Minor (0.1.0 → 0.2.0) - new features
make client-version-minor

# Major (0.1.0 → 1.0.0) - breaking changes
make client-version-major

# Ou manual
cd packages/api-client
npm version 0.2.0 --no-git-tag-version
```

### 3. Commit e criar tag

```bash
# Commit
git add packages/api-client/package.json
git commit -m "chore(api-client): release v0.2.0"

# Tag
git tag -a api-client-v0.2.0 -m "Release API Client v0.2.0"

# Push
git push origin main
git push origin api-client-v0.2.0
```

### 4. CI/CD publica automaticamente

O workflow `.github/workflows/publish-api-client.yml` detecta a tag e:
- Gera enums, error codes e client
- Builda o pacote
- Atualiza o package.json com a versão da tag
- Publica no GitHub Packages
- Cria um GitHub Release

## Formato de Tags

**Sempre use o formato:** `api-client-v{version}`

Exemplos:
- `api-client-v0.1.0`
- `api-client-v0.2.0`
- `api-client-v1.0.0`
- `api-client-v1.0.0-beta.1`

## Versionamento Semântico

| Tipo | Quando usar | Exemplo |
|------|-------------|---------|
| **Patch** | Bug fixes, typos | 0.1.0 → 0.1.1 |
| **Minor** | Novas features (backward compatible) | 0.1.0 → 0.2.0 |
| **Major** | Breaking changes | 0.1.0 → 1.0.0 |

## Trigger Manual

Você também pode disparar manualmente via GitHub Actions:

1. Vá para Actions → Publish API Client
2. Clique em "Run workflow"
3. Digite a versão (ex: 0.2.0)
4. Clique em "Run workflow"

## Verificar Publicação

```bash
# Ver todas as versões publicadas
npm view @queroplantao/api-client versions

# Ver última versão
npm view @queroplantao/api-client version

# Ver detalhes do pacote
npm view @queroplantao/api-client
```

## Troubleshooting

### Erro: "version already exists"

Se a versão já foi publicada, você precisa fazer bump:

```bash
make client-version-patch  # ou minor/major
git add packages/api-client/package.json
git commit -m "chore(api-client): bump to v0.1.2"
git tag api-client-v0.1.2
git push origin main api-client-v0.1.2
```

### Erro: "unauthorized" no CI/CD

Verifique que o workflow tem permissão para publicar:
- Settings → Actions → General
- Workflow permissions: "Read and write permissions"

### Tag errada

Para deletar e recriar:

```bash
# Local
git tag -d api-client-v0.1.0

# Remote
git push origin :refs/tags/api-client-v0.1.0

# Recriar
git tag api-client-v0.1.0
git push origin api-client-v0.1.0
```

## Instalação no Frontend

Após publicação, instalar no projeto frontend:

```bash
npm install @queroplantao/api-client@0.2.0
```

Ou adicionar ao `package.json`:

```json
{
  "dependencies": {
    "@queroplantao/api-client": "^0.2.0"
  }
}
```

Configurar `.npmrc` no frontend:

```bash
@queroplantao:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```
