"""
Quero Plantão MCP Server.

This is the main entry point for the MCP server.
Run with: uv run mcp-server
"""

from __future__ import annotations

import argparse
import logging

from fastmcp import FastMCP

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
# DATABASE TOOLS
# =============================================================================


@mcp.tool()
def get_entity_schema(entity_name: str) -> dict | None:
    """
    Get SQLModel entity structure including columns and relationships.

    Args:
        entity_name: Name of the entity (e.g., "ScreeningProcess").

    Returns:
        Entity definition with columns, relationships, and indexes.
    """
    from queroplantao_mcp.parsers import get_sqlmodel_parser

    parser = get_sqlmodel_parser()
    return parser.get_entity(entity_name)


@mcp.tool()
def list_entities(module: str | None = None) -> list[dict]:
    """
    List all database entities.

    Args:
        module: Optional module to filter by.

    Returns:
        List of entity summaries.
    """
    from queroplantao_mcp.parsers import get_sqlmodel_parser

    parser = get_sqlmodel_parser()
    return parser.list_entities(module=module)


@mcp.tool()
def find_entities_by_field(
    field_name: str,
    field_type: str | None = None,
) -> list[dict]:
    """
    Find entities that contain a specific field.

    Args:
        field_name: Name of the field to search for.
        field_type: Optional type to filter by.

    Returns:
        List of matches with entity and field info.
    """
    from queroplantao_mcp.parsers import get_sqlmodel_parser

    parser = get_sqlmodel_parser()
    return parser.find_by_field(field_name, field_type)


@mcp.tool()
def get_er_diagram(
    module: str,
    format: str = "mermaid",
) -> str:
    """
    Generate an ER diagram for a module.

    Args:
        module: The module to generate diagram for.
        format: Output format - "mermaid" or "dbml".

    Returns:
        Diagram in the specified format.
    """
    from queroplantao_mcp.parsers import get_sqlmodel_parser

    parser = get_sqlmodel_parser()
    return parser.generate_er_diagram(module, format_=format)


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
        mcp.run(transport="sse", sse_host=args.host, sse_port=args.port)
    else:
        logger.info("Running in stdio mode")
        mcp.run()


if __name__ == "__main__":
    main()
