# Quero Plantão MCP Server

MCP (Model Context Protocol) server providing technical documentation, schema information, business rules, and code analysis tools for the Quero Plantão API.

## Purpose

This MCP server is designed to be consumed by LLMs (like GPT-5.2 mini or Claude) that are building the frontend for the Quero Plantão application. It provides structured access to:

- **API Schemas**: Endpoint details, request/response schemas, enums with PT-BR labels
- **Business Rules**: Workflow diagrams, state machines, validation rules
- **Database Structure**: Entity schemas, relationships, ER diagrams
- **Documentation**: Module docs, OpenAPI specs, Bruno examples
- **Code Analysis**: Use case analysis, code explanations (LLM-powered)

## Installation

```bash
cd packages/mcp-server
uv sync
```

## Configuration

Set environment variables:

```bash
# Required for LLM-powered tools
export OPENAI_API_KEY="sk-..."

# Optional: customize LLM settings
export MCP_LLM_MODEL="gpt-4o-mini"  # or gpt-5.2-mini when available
export MCP_LLM_TEMPERATURE="0.1"
export MCP_LLM_MAX_TOKENS="4096"
```

## Running the Server

### Stdio Mode (for MCP clients like Claude Desktop)

```bash
uv run mcp-server
```

### SSE Mode (for HTTP-based clients)

```bash
uv run mcp-server --sse
```

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

### Database (Deterministic)
- `list_entities` - List all database entities
- `get_entity_schema` - Get SQLModel entity structure
- `find_entities_by_field` - Find entities containing a specific field
- `get_er_diagram` - Get ER diagram for a module (Mermaid/DBML)

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
| Database | 4 | Deterministic |
| Business Rules | 4 | LLM-powered |
| Code Analysis | 4 | LLM-powered |
| Context | 5 | Mixed |
| **Total** | **24** | |

## License

MIT
