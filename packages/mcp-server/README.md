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
- `get_enum` - Get enum values with PT-BR labels
- `list_enums` - List all available enums
- `get_error_codes` - Get error codes for a module/endpoint

### Business Rules (LLM-powered)
- `explain_business_rule` - Explain a business rule in natural language
- `get_workflow_diagram` - Get workflow diagram for a process
- `get_state_machine` - Get state machine for an entity
- `validate_user_story` - Validate if a user story is implementable

### Database (Deterministic)
- `get_entity_schema` - Get SQLModel entity structure
- `get_er_diagram` - Get ER diagram for a module
- `find_entity_by_field` - Find entities containing a field

### Code Analysis (LLM-powered)
- `analyze_use_case` - Analyze a use case and explain its logic
- `find_related_code` - Find code related to a concept
- `explain_code_snippet` - Explain a code snippet

### Context
- `set_development_context` - Set context for focused responses
- `get_implementation_checklist` - Get implementation checklist for a feature

## Available Resources

- `docs://modules/{module}` - Module documentation
- `openapi://spec` - Full OpenAPI specification
- `openapi://paths/{path}` - OpenAPI path details
- `bruno://{module}/{endpoint}` - Bruno request/response examples

## Project Structure

```
src/queroplantao_mcp/
├── __init__.py
├── config.py              # Configuration and paths
├── server.py              # FastMCP server entry point
├── parsers/
│   ├── openapi_parser.py  # Parse OpenAPI spec
│   ├── enum_parser.py     # Parse Python enums
│   ├── pydantic_parser.py # Parse Pydantic schemas
│   └── sqlmodel_parser.py # Parse SQLModel entities
├── tools/
│   ├── api_schemas.py     # API schema tools
│   ├── business_rules.py  # Business rule tools (LLM)
│   ├── database.py        # Database structure tools
│   └── code_analysis.py   # Code analysis tools (LLM)
├── resources/
│   ├── docs.py            # Documentation resources
│   └── openapi.py         # OpenAPI resources
└── llm/
    ├── client.py          # OpenAI client wrapper
    └── prompts.py         # System prompts
```

## License

MIT
