# Quero Plantão MCP Server

MCP (Model Context Protocol) server providing technical documentation, schema information, business rules, and code analysis tools for the Quero Plantão API.

Built with **FastMCP 3.0** with:
- 🔄 **Namespace Transform**: All tools prefixed with `qp_` to avoid conflicts
- 📦 **ResourcesAsTools**: Resources exposed as tools for broader client compatibility
- ⏱️ **Tool Timeouts**: LLM-powered tools have 60s timeout for reliability
- 🔙 **Background Tasks**: Long-running LLM operations run as background tasks
- 💾 **Session State**: Development context persists across requests within sessions

## Purpose

This MCP server is designed to be consumed by LLMs (like GPT-5.2 mini or Claude) that are building the frontend for the Quero Plantão application. It provides structured access to:

- **API Schemas**: Endpoint details, request/response schemas, enums with PT-BR labels
- **Business Rules**: Workflow diagrams, state machines, validation rules
- **Database Structure**: Entity schemas, relationships, ER diagrams
- **Documentation**: Module docs, OpenAPI specs, Bruno examples
- **Code Analysis**: Use case analysis, code explanations (LLM-powered)

## Quick Start

```bash
# Complete setup and testing
make dev

# Run the server
make run
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make dev` | Complete setup (install deps, create .env, test, show info) |
| `make run` | Run MCP server in stdio mode (for Claude Desktop) |
| `make run-sse` | Run MCP server in SSE mode (HTTP server) |
| `make test` | Run comprehensive test suite |
| `make test-quick` | Quick import and structure test |
| `make info` | Show server information and environment status |
| `make setup` | Setup development environment |
| `make check-env` | Verify environment configuration |
| `make copilot-config` | Generate GitHub Copilot MCP configuration |
| `make lint` | Run code linter |
| `make format` | Format code |
| `make clean` | Clean cache files |

## Installation

```bash
cd packages/mcp-server
make setup
```

## Configuration

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Set your OpenAI API key:**
```bash
# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key for LLM-powered tools |
| `MCP_LLM_MODEL` | No | `gpt-4o-mini` | Model for analysis (gpt-4o-mini, gpt-4o, gpt-3.5-turbo) |
| `MCP_LLM_TEMPERATURE` | No | `0.1` | Response creativity (0.0-1.0) |
| `MCP_LLM_MAX_TOKENS` | No | `4096` | Max tokens per response |

*Required for LLM-powered tools. Server works without it but with limited functionality.

## Testing

Run the comprehensive test suite to verify everything is working:

```bash
uv run python test_server.py
```

This will test:
- ✅ Project structure validation
- ✅ OpenAPI specification parsing (70 endpoints, 120 schemas)
- ✅ Enum parsing (22 enums found)
- ✅ SQLModel entity parsing (38 entities found)
- ✅ Business rules tools (state machines, workflows)
- ✅ MCP server initialization (25 tools registered with `qp_` prefix)

## Running the Server

### Test First

Before running the server, test that everything is working:

```bash
uv run python test_server.py
```

### Stdio Mode (for MCP clients like Claude Desktop)

```bash
uv run mcp-server
```

### SSE Mode (for HTTP-based clients)

```bash
uv run mcp-server --sse
```

## GitHub Copilot Integration

O GitHub Copilot tem suporte experimental a MCP servers. Para usar este servidor:

### Configuração Automática (Recomendado)

```bash
cd packages/mcp-server
./setup-copilot.sh
```

Este script irá:
- ✅ Detectar automaticamente os caminhos
- ✅ Ler sua API key do arquivo `.env`
- ✅ Gerar arquivo `github-copilot-config-generated.json`
- ✅ Mostrar instruções de como colar no VS Code

### Configuração Manual

1. **Abra as configurações do VS Code** (`Ctrl/Cmd + Shift + P` → "Preferences: Open Settings (JSON)")
2. **Adicione a configuração MCP:**

```json
{
  "github.copilot.chat.mcp": {
    "queroplantao-api": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/your/queroplantao-api/packages/mcp-server",
        "mcp-server"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-your-openai-api-key-here"
      }
    }
  }
}
```

### Verificação

1. **Reinicie o VS Code**
2. **Abra o Chat do GitHub Copilot** (`Ctrl/Cmd + Shift + P` → "GitHub Copilot: Open Chat")
3. **Teste a conexão:**

```
What MCP servers do you have access to?
```

### Exemplos de Uso

Agora você pode perguntar ao Copilot sobre a API:

```
Show me all available endpoints in the screening module
```

```
What are the business rules for professional validation?
```

```
Generate a checklist for implementing a screening process form
```

```
Explain the state machine for ScreeningProcess entity
```

### Troubleshooting

**Se o servidor não conectar:**
- Execute `make test` para verificar se funciona
- Verifique se o caminho no arquivo de configuração está correto
- Certifique-se que `OPENAI_API_KEY` está definida

**Se as tools não aparecerem:**
- Reinicie o VS Code completamente
- Verifique os logs: `Ctrl/Cmd + Shift + P` → "Developer: Show Logs" → "GitHub Copilot Chat"

## Available Tools

### API Schemas (Deterministic)
- `list_modules` - List all API modules with descriptions
- `get_endpoints` - Get endpoints for a module
- `get_schema` - Get request/response schema details
- `list_schemas` - List all available schemas
- `get_enum` - Get enum values with PT-BR labels
- `list_enums` - List all available enums

### Business Rules (LLM-powered)
- `explain_business_rule` - Explain a business rule in natural language
- `get_workflow_diagram` - Get workflow diagram for a process
- `get_state_machine` - Get state machine for an entity
- `validate_user_story` - Validate if a user story is implementable

### Database & Entities (Deterministic)
- `get_entity_schema` - Get complete SQLModel entity schema with relationships
- `get_er_diagram` - Generate ER diagram (Mermaid/DBML/ASCII)
- `find_entity_by_field` - Find entities containing a specific field with insights

### Code Analysis (LLM-powered)
- `analyze_use_case` - Analyze a use case and explain its logic
- `find_related_code` - Find code related to a concept
- `explain_code_snippet` - Explain a code snippet
- `get_error_codes` - Get all error codes for a module

### Context Management
- `set_development_context` - Set context for focused responses
- `get_development_context` - Get current development context
- `clear_development_context` - Clear the current context
- `get_implementation_checklist` - Get implementation checklist for a feature
- `suggest_api_integration` - Get API integration suggestions

## Available Resources

- `docs://modules/{module}` - Module documentation (Markdown)
- `openapi://spec` - Full OpenAPI specification (JSON)
- `openapi://paths/{path}` - OpenAPI spec for specific path
- `client://types/{type_name}` - TypeScript type definitions from API client
- `bruno://{module}/{endpoint}` - Bruno request examples
- `bruno://list` - List all available Bruno examples
- `errors://all` - All error codes organized by module

- `openapi://spec` - Full OpenAPI specification (JSON)
- `bruno://{module}/{endpoint}` - Bruno request examples
- `bruno://list` - List all Bruno examples by module
- `errors://all` - All error codes organized by class

## Project Structure

```
src/queroplantao_mcp/
├── __init__.py
├── config.py              # Configuration and paths
├── server.py              # FastMCP server entry point (24 tools)
├── parsers/
│   ├── __init__.py
│   ├── openapi_parser.py  # Parse OpenAPI spec
│   ├── enum_parser.py     # Parse Python enums with PT-BR labels
│   └── sqlmodel_parser.py # Parse SQLModel entities
├── tools/
│   ├── __init__.py
│   ├── business_rules.py  # Workflow diagrams, state machines
│   ├── code_analysis.py   # Use case analysis, code search
│   └── context.py         # Development context management
└── llm/
    ├── __init__.py
    ├── client.py          # OpenAI client wrapper
    └── prompts.py         # System prompts for analysis
```

## Tool Count Summary

| Category | Tools | Type |
|----------|-------|------|
| Health | 1 | Deterministic |
| API Schemas | 6 | Deterministic |
| Business Rules | 4 | LLM-powered |
| Database & Entities | 3 | Deterministic |
| Code Analysis | 4 | LLM-powered |
| Context Management | 5 | Mixed |
| **Total Tools** | **23** | |
| **Resources** | **7** | (3 static + 4 templated) |

**Resources:**
- `docs://modules/{module}` - Module documentation
- `openapi://spec` - Full OpenAPI spec
- `openapi://paths/{path}` - OpenAPI spec for specific path
- `client://types/{type_name}` - TypeScript types from API client
- `bruno://{module}/{endpoint}` - Bruno request examples
- `bruno://list` - List all Bruno examples
- `errors://all` - All error codes

## License

MIT
