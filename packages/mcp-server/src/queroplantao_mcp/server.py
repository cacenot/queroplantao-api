"""
Quero Plantão MCP Server.

This is the main entry point for the MCP server.
Run with: uv run mcp-server
"""

from __future__ import annotations

import argparse
import logging

from fastmcp import Context, FastMCP
from fastmcp.server.transforms import Namespace, ResourcesAsTools

from queroplantao_mcp.config import (
    PROJECT_ROOT,
    SERVER_DESCRIPTION,
    SERVER_NAME,
    validate_project_structure,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=SERVER_DESCRIPTION,
)

# Add transforms for component organization
# Namespace prefix for all tools/resources to avoid conflicts
mcp.add_transform(Namespace("qp"))
# Expose resources as tools for clients that only support tools
mcp.add_transform(ResourcesAsTools(mcp))


# =============================================================================
# HEALTH CHECK TOOL
# =============================================================================


@mcp.tool()
def health_check() -> dict:
    """
    Check if the MCP server is running and project structure is accessible.

    Returns:
        Status information about the server and project structure.
    """
    structure = validate_project_structure()
    all_valid = all(structure.values())

    return {
        "status": "healthy" if all_valid else "degraded",
        "project_root": str(PROJECT_ROOT),
        "structure_check": structure,
    }


# =============================================================================
# API SCHEMAS TOOLS
# =============================================================================


@mcp.tool()
def list_modules() -> list[dict]:
    """
    List all API modules with descriptions.

    Returns:
        List of modules with name, description, and endpoint count.
    """
    from queroplantao_mcp.config import MODULE_DESCRIPTIONS
    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()

    try:
        modules = parser.list_modules()

        # Enrich with descriptions
        for mod in modules:
            name = mod["name"]
            if name in MODULE_DESCRIPTIONS:
                mod["description_pt"] = MODULE_DESCRIPTIONS[name]

        return modules
    except FileNotFoundError:
        # OpenAPI not generated yet
        from queroplantao_mcp.config import AVAILABLE_MODULES

        return [
            {
                "name": mod,
                "description_pt": MODULE_DESCRIPTIONS.get(mod, ""),
                "endpoint_count": 0,
                "note": "OpenAPI spec not found. Run 'make openapi' to generate.",
            }
            for mod in AVAILABLE_MODULES
        ]


@mcp.tool()
def get_endpoints(
    module: str | None = None,
    method: str | None = None,
) -> list[dict]:
    """
    Get API endpoints, optionally filtered by module or method.

    Args:
        module: Filter by module name (e.g., "screening", "professionals").
        method: Filter by HTTP method (GET, POST, PATCH, DELETE).

    Returns:
        List of endpoint definitions with path, method, schemas, and parameters.
    """
    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()
    return parser.get_endpoints(module=module, method=method)


@mcp.tool()
def get_schema(
    schema_name: str,
    format: str = "json_schema",
) -> dict | None:
    """
    Get detailed schema information for a Pydantic model.

    Args:
        schema_name: Name of the schema (e.g., "ScreeningProcessCreate").
        format: Output format - "json_schema" or "form_fields".

    Returns:
        Schema definition with properties, types, and constraints.
    """
    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()

    if format == "form_fields":
        return parser.get_schema_as_form_fields(schema_name)

    return parser.get_schema(schema_name)


@mcp.tool()
def list_schemas(search: str | None = None) -> list[dict]:
    """
    List all available schemas in the API.

    Args:
        search: Optional search term to filter schemas by name.

    Returns:
        List of schema summaries with name and property count.
    """
    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()
    schemas = parser.list_schemas()

    if search:
        search_lower = search.lower()
        schemas = [s for s in schemas if search_lower in s["name"].lower()]

    return schemas


@mcp.tool()
def get_enum(enum_name: str) -> dict | None:
    """
    Get detailed enum information with PT-BR labels.

    Args:
        enum_name: Name of the enum (e.g., "ScreeningStatus").

    Returns:
        Enum definition with values, labels, and descriptions.
    """
    from queroplantao_mcp.parsers import get_enum_parser

    parser = get_enum_parser()
    return parser.get_enum(enum_name)


@mcp.tool()
def list_enums(module: str | None = None) -> list[dict]:
    """
    List all available enums.

    Args:
        module: Optional module to filter by.

    Returns:
        List of enum summaries with name and member count.
    """
    from queroplantao_mcp.parsers import get_enum_parser

    parser = get_enum_parser()
    return parser.list_enums(module=module)


# =============================================================================
# DOCUMENTATION RESOURCES
# =============================================================================


@mcp.resource("docs://modules/{module}")
def get_module_documentation(module: str) -> str:
    """
    Get the documentation for a specific module.

    Args:
        module: Module name (screening, professionals, etc.)

    Returns:
        Full markdown documentation for the module.
    """
    from queroplantao_mcp.config import get_module_docs_path

    doc_path = get_module_docs_path(module)
    if doc_path and doc_path.exists():
        return doc_path.read_text(encoding="utf-8")

    return f"Documentation not found for module: {module}"


@mcp.resource("openapi://spec")
def get_openapi_spec() -> str:
    """
    Get the full OpenAPI specification as JSON.

    Returns:
        OpenAPI spec JSON string.
    """
    import json

    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()
    spec = parser.get_spec()
    return json.dumps(spec, indent=2)


@mcp.resource("openapi://paths/{path}")
def get_openapi_path(path: str) -> str:
    """
    Get OpenAPI specification for a specific path.

    Args:
        path: API path (e.g., "/screenings", "/professionals/{id}")

    Returns:
        OpenAPI path spec as JSON.
    """
    import json

    from queroplantao_mcp.parsers import get_openapi_parser

    parser = get_openapi_parser()
    spec = parser.get_spec()

    # Normalize path (remove leading slash if present)
    normalized_path = f"/{path}" if not path.startswith("/") else path

    paths = spec.get("paths", {})
    if normalized_path in paths:
        return json.dumps({normalized_path: paths[normalized_path]}, indent=2)

    return json.dumps({"error": f"Path not found: {normalized_path}", "available_paths": list(paths.keys())[:20]})


@mcp.resource("client://types/{type_name}")
def get_client_type(type_name: str) -> str:
    """
    Get TypeScript type definition from API client.

    Args:
        type_name: Type name (e.g., "ScreeningProcessResponse", "ProfessionalCreate")

    Returns:
        TypeScript type definition.
    """
    from queroplantao_mcp.config import PROJECT_ROOT

    # Try to find in generated API client
    api_client_dir = PROJECT_ROOT / "packages" / "api-client" / "src"

    # Search in model files
    models_file = api_client_dir / "model" / "index.ts"
    if models_file.exists():
        content = models_file.read_text(encoding="utf-8")

        # Look for type/interface definition
        lines = content.split("\n")
        in_type = False
        type_lines = []

        for line in lines:
            if f"export type {type_name}" in line or f"export interface {type_name}" in line:
                in_type = True
                type_lines.append(line)
            elif in_type:
                type_lines.append(line)
                if line.strip().startswith("}"):
                    # End of type definition
                    break

        if type_lines:
            return "\n".join(type_lines)

    return f"Type not found in API client: {type_name}\nNote: Run 'make client-all' to regenerate the API client"


@mcp.resource("bruno://{module}/{endpoint}")
def get_bruno_example(module: str, endpoint: str) -> str:
    """
    Get a Bruno request example for an endpoint.

    Args:
        module: Module name (screenings, professionals, etc.)
        endpoint: Endpoint name (create-screening, list-professionals, etc.)

    Returns:
        Bruno request file content.
    """
    from queroplantao_mcp.config import PROJECT_ROOT

    bruno_path = PROJECT_ROOT / "docs" / "bruno" / module / f"{endpoint}.bru"
    if bruno_path.exists():
        return bruno_path.read_text(encoding="utf-8")

    return f"Bruno example not found: {module}/{endpoint}"


@mcp.resource("bruno://list")
def list_bruno_examples() -> str:
    """
    List all available Bruno request examples.

    Returns:
        JSON list of available examples by module.
    """
    import json

    from queroplantao_mcp.config import PROJECT_ROOT

    bruno_dir = PROJECT_ROOT / "docs" / "bruno"
    examples: dict[str, list[str]] = {}

    for module_dir in bruno_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith("."):
            module_examples = []
            for bru_file in module_dir.glob("*.bru"):
                if bru_file.name != "folder.bru":
                    module_examples.append(bru_file.stem)
            if module_examples:
                examples[module_dir.name] = sorted(module_examples)

    return json.dumps(examples, indent=2)


@mcp.resource("errors://all")
def get_all_error_codes() -> str:
    """
    Get all error codes defined in the project.

    Returns:
        JSON with all error codes organized by module.
    """
    import ast
    import json

    from queroplantao_mcp.config import PROJECT_ROOT

    error_codes_path = PROJECT_ROOT / "src" / "app" / "constants" / "error_codes.py"
    if not error_codes_path.exists():
        return json.dumps({"error": "error_codes.py not found"})

    content = error_codes_path.read_text(encoding="utf-8")
    tree = ast.parse(content)

    error_codes: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("ErrorCodes"):
            class_name = node.name
            codes = []

            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and isinstance(item.value, ast.Constant):
                            codes.append(item.value.value)

            if codes:
                error_codes[class_name] = codes

    return json.dumps(error_codes, indent=2)


# =============================================================================
# BUSINESS RULES TOOLS (LLM-powered)
# =============================================================================


@mcp.tool(timeout=60.0, task=True)
async def explain_business_rule(
    topic: str,
    module: str | None = None,
    context: str | None = None,
) -> dict:
    """
    Explain a business rule using LLM analysis.

    Args:
        topic: Topic to explain (e.g., "validação de CPF", "family scope").
        module: Optional module to focus on.
        context: Optional additional context.

    Returns:
        Detailed explanation with examples.
    """
    from queroplantao_mcp.tools import explain_business_rule as _impl

    return await _impl(topic, module, context)


@mcp.tool(timeout=60.0, task=True)
async def get_workflow_diagram(
    workflow: str,
    format: str = "mermaid",
) -> dict:
    """
    Get a workflow diagram for a business process.

    Args:
        workflow: Workflow name (e.g., "screening_process", "document_review").
        format: Output format - "mermaid", "ascii", or "steps".

    Returns:
        Diagram in the specified format.
    """
    from queroplantao_mcp.tools import get_workflow_diagram as _impl

    return await _impl(workflow, format)


@mcp.tool()
async def get_state_machine(entity: str) -> dict:
    """
    Get state machine definition for an entity.

    Args:
        entity: Entity name (e.g., "ScreeningProcess", "ScreeningDocument").

    Returns:
        State machine with states, transitions, and UI hints.
    """
    from queroplantao_mcp.tools import get_state_machine as _impl

    return await _impl(entity)


@mcp.tool(timeout=60.0, task=True)
async def validate_user_story(
    story: str,
    module: str | None = None,
) -> dict:
    """
    Validate if a user story is implementable with the current API.

    Args:
        story: User story description.
        module: Optional module context.

    Returns:
        Validation result with feasibility and suggestions.
    """
    from queroplantao_mcp.tools import validate_user_story as _impl

    return await _impl(story, module)


# =============================================================================
# CODE ANALYSIS TOOLS (LLM-powered)
# =============================================================================


@mcp.tool(timeout=60.0, task=True)
async def analyze_use_case(use_case: str) -> dict:
    """
    Analyze a use case and explain its logic.

    Args:
        use_case: Name of the use case (e.g., "CreateScreeningProcessUseCase").

    Returns:
        Analysis with dependencies, validations, and frontend notes.
    """
    from queroplantao_mcp.tools import analyze_use_case as _impl

    return await _impl(use_case)


@mcp.tool(timeout=30.0)
async def find_related_code(
    concept: str,
    code_type: str = "all",
    module: str | None = None,
) -> dict:
    """
    Find code related to a concept.

    Args:
        concept: Concept to search for (e.g., "family scope", "soft delete").
        code_type: Type - "all", "use_cases", "repositories", "routes", "schemas", "models".
        module: Optional module to limit search.

    Returns:
        List of matching files with relevant excerpts.
    """
    from queroplantao_mcp.tools import find_related_code as _impl

    return await _impl(concept, code_type, module)


@mcp.tool(timeout=60.0, task=True)
async def explain_code_snippet(
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> dict:
    """
    Explain a code snippet.

    Args:
        file_path: Path to file (relative or absolute).
        start_line: Optional start line (1-indexed).
        end_line: Optional end line (1-indexed).

    Returns:
        LLM explanation of the code.
    """
    from queroplantao_mcp.tools import explain_code_snippet as _impl

    return await _impl(file_path, start_line, end_line)


@mcp.tool()
async def get_error_codes(module: str | None = None) -> dict:
    """
    Get error codes defined in the project.

    Args:
        module: Optional module to filter by.

    Returns:
        List of error codes with messages.
    """
    from queroplantao_mcp.tools import get_error_codes as _impl

    return await _impl(module)


# =============================================================================
# DATABASE & ENTITIES TOOLS
# =============================================================================


@mcp.tool()
async def get_entity_schema(entity: str) -> dict:
    """
    Get complete schema for a SQLModel entity.

    Args:
        entity: Entity name (e.g., "ScreeningProcess", "Professional").

    Returns:
        Entity schema with columns, relationships, constraints, and patterns.
    """
    from queroplantao_mcp.tools import get_entity_schema as _impl

    return await _impl(entity)


@mcp.tool()
async def get_er_diagram(
    module: str | None = None,
    format: str = "mermaid",
) -> dict:
    """
    Generate Entity-Relationship diagram.

    Args:
        module: Optional module to filter entities.
        format: Output format - "mermaid", "dbml", or "ascii".

    Returns:
        ER diagram in the specified format.
    """
    from queroplantao_mcp.tools import get_er_diagram as _impl

    return await _impl(module, format)


@mcp.tool()
async def find_entity_by_field(field_name: str) -> dict:
    """
    Find all entities containing a specific field.

    Args:
        field_name: Field to search for (e.g., "organization_id", "deleted_at").

    Returns:
        List of entities with the field and pattern insights.
    """
    from queroplantao_mcp.tools import find_entity_by_field as _impl

    return await _impl(field_name)


# =============================================================================
# CONTEXT MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
async def set_development_context(
    feature: str,
    module: str,
    ctx: Context,
    user_story: str | None = None,
    notes: str | None = None,
) -> dict:
    """
    Set the current development context.

    Args:
        feature: Feature being developed.
        module: Module being worked on.
        ctx: FastMCP Context for session state.
        user_story: Optional user story.
        notes: Optional notes.

    Returns:
        Context confirmation with relevant resources.
    """
    from queroplantao_mcp.tools import set_development_context as _impl

    return await _impl(feature, module, ctx, user_story, notes)


@mcp.tool()
async def get_development_context(ctx: Context) -> dict:
    """
    Get the current development context.

    Args:
        ctx: FastMCP Context for session state.

    Returns:
        Current context if set.
    """
    from queroplantao_mcp.tools import get_development_context as _impl

    return await _impl(ctx)


@mcp.tool()
async def clear_development_context(ctx: Context) -> dict:
    """
    Clear the current development context.

    Args:
        ctx: FastMCP Context for session state.

    Returns:
        Confirmation message.
    """
    from queroplantao_mcp.tools import clear_development_context as _impl

    return await _impl(ctx)


@mcp.tool(timeout=60.0)
async def get_implementation_checklist(
    ctx: Context,
    feature: str | None = None,
    module: str | None = None,
) -> dict:
    """
    Generate an implementation checklist for a feature.

    Args:
        ctx: FastMCP Context for session state.
        feature: Optional feature name (uses context if not provided).
        module: Optional module name (uses context if not provided).

    Returns:
        Step-by-step implementation checklist.
    """
    from queroplantao_mcp.tools import get_implementation_checklist as _impl

    return await _impl(ctx, feature, module)


@mcp.tool(timeout=60.0, task=True)
async def suggest_api_integration(
    feature: str,
    existing_code: str | None = None,
) -> dict:
    """
    Suggest API integration for a feature.

    Args:
        feature: Feature being implemented.
        existing_code: Optional existing frontend code.

    Returns:
        Integration suggestions with code examples.
    """
    from queroplantao_mcp.tools import suggest_api_integration as _impl

    return await _impl(feature, existing_code)


# =============================================================================
# ENTRY POINT
# =============================================================================


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Quero Plantão MCP Server")
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run in SSE mode for HTTP-based clients",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE mode (default: 8080)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for SSE mode (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    logger.info(f"Starting {SERVER_NAME}...")
    logger.info(f"Project root: {PROJECT_ROOT}")

    # Validate structure
    structure = validate_project_structure()
    for key, valid in structure.items():
        status = "✓" if valid else "✗"
        logger.info(f"  {status} {key}")

    if args.sse:
        logger.info(f"Running in SSE mode on http://{args.host}:{args.port}")
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        logger.info("Running in stdio mode")
        mcp.run()


if __name__ == "__main__":
    main()
