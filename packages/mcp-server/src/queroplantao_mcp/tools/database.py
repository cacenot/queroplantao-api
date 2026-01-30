"""
Database & Entities tools for the MCP server.

These tools provide access to database schema information,
entity structures, and ER diagrams.
"""

from __future__ import annotations

from queroplantao_mcp.parsers import get_sqlmodel_parser


async def get_entity_schema(entity: str) -> dict:
    """
    Get the complete schema for a SQLModel entity.

    Args:
        entity: Name of the entity (e.g., "ScreeningProcess", "Professional").

    Returns:
        Entity schema with columns, relationships, constraints, and soft delete info.
    """
    parser = get_sqlmodel_parser()

    try:
        schema = parser.get_entity(entity)

        # Enrich with additional information
        if schema:
            # Add soft delete info
            has_soft_delete = any(field["name"] == "deleted_at" for field in schema.get("fields", []))

            if has_soft_delete:
                schema["soft_delete"] = {
                    "enabled": True,
                    "field": "deleted_at",
                    "note": "Use _exclude_deleted() in repository queries. Unique indexes must be partial: postgresql_where=text('deleted_at IS NULL')",
                }

            # Add multi-tenancy info
            has_org_id = any(field["name"] == "organization_id" for field in schema.get("fields", []))

            if has_org_id:
                schema["multi_tenancy"] = {
                    "enabled": True,
                    "scope": "organization",
                    "note": "Entity is scoped by organization_id. Use _base_query_for_organization() in repositories.",
                }

            # Identify relationships
            relationships = []
            for field in schema.get("fields", []):
                if field.get("is_foreign_key"):
                    relationships.append(
                        {
                            "field": field["name"],
                            "type": "many-to-one",
                            "references": field.get("foreign_key"),
                        }
                    )

            if relationships:
                schema["relationships"] = relationships

        return schema

    except Exception as e:
        return {
            "entity": entity,
            "error": str(e),
            "note": "Entity not found or failed to parse",
        }


async def get_er_diagram(
    module: str | None = None,
    format: str = "mermaid",
) -> dict:
    """
    Generate an Entity-Relationship diagram.

    Args:
        module: Optional module to filter entities (e.g., "screening", "professionals").
        format: Output format - "mermaid", "dbml", or "ascii".

    Returns:
        ER diagram in the specified format.
    """
    parser = get_sqlmodel_parser()

    try:
        # Get all entities
        all_entities = parser.list_entities()

        # Filter by module if specified
        if module:
            entities = [e for e in all_entities if e.get("module", "").lower() == module.lower()]
        else:
            entities = all_entities

        if not entities:
            return {
                "module": module,
                "error": "No entities found",
                "available_modules": list({e.get("module") for e in all_entities if e.get("module")}),
            }

        # Generate diagram based on format
        if format == "mermaid":
            diagram = _generate_mermaid_er(entities)
        elif format == "dbml":
            diagram = _generate_dbml_er(entities)
        elif format == "ascii":
            diagram = _generate_ascii_er(entities)
        else:
            return {
                "error": f"Unsupported format: {format}",
                "supported_formats": ["mermaid", "dbml", "ascii"],
            }

        return {
            "module": module or "all",
            "format": format,
            "entity_count": len(entities),
            "diagram": diagram,
        }

    except Exception as e:
        return {
            "module": module,
            "format": format,
            "error": str(e),
        }


async def find_entity_by_field(field_name: str) -> dict:
    """
    Find all entities that have a specific field.

    Args:
        field_name: Name of the field to search for (e.g., "organization_id",
                   "deleted_at", "created_at").

    Returns:
        List of entities containing the field with field details.
    """
    parser = get_sqlmodel_parser()

    try:
        all_entities = parser.list_entities()

        matches = []
        for entity_info in all_entities:
            entity_name = entity_info["name"]
            try:
                entity_schema = parser.get_entity(entity_name)

                # Check if field exists
                matching_fields = [field for field in entity_schema.get("fields", []) if field["name"] == field_name]

                if matching_fields:
                    field = matching_fields[0]
                    matches.append(
                        {
                            "entity": entity_name,
                            "module": entity_info.get("module"),
                            "field": {
                                "name": field["name"],
                                "type": field["type"],
                                "nullable": field.get("nullable", False),
                                "is_foreign_key": field.get("is_foreign_key", False),
                                "foreign_key": field.get("foreign_key"),
                            },
                        }
                    )
            except Exception:
                # Skip entities that can't be parsed
                continue

        # Add insights based on common fields
        insights = _get_field_insights(field_name, matches)

        return {
            "field_name": field_name,
            "match_count": len(matches),
            "matches": matches,
            "insights": insights,
        }

    except Exception as e:
        return {
            "field_name": field_name,
            "error": str(e),
        }


# Helper functions


def _generate_mermaid_er(entities: list[dict]) -> str:
    """Generate Mermaid ER diagram."""
    lines = ["erDiagram"]

    # Get entity schemas
    parser = get_sqlmodel_parser()

    for entity_info in entities:
        entity_name = entity_info["name"]
        try:
            schema = parser.get_entity(entity_name)

            # Add entity with key fields
            lines.append(f"    {entity_name} {{")
            for field in schema.get("fields", [])[:10]:  # Limit to 10 fields
                field_type = field.get("type", "unknown")
                nullable = "NULL" if field.get("nullable") else "NOT NULL"
                pk = "PK" if field.get("is_primary_key") else ""
                fk = "FK" if field.get("is_foreign_key") else ""
                key_marker = f" {pk}{fk}".strip()

                lines.append(f"        {field_type} {field['name']}{key_marker} {nullable}")

            lines.append("    }")

            # Add relationships
            for field in schema.get("fields", []):
                if field.get("is_foreign_key") and field.get("foreign_key"):
                    ref_entity = field["foreign_key"].split(".")[0]
                    # Many-to-one relationship
                    lines.append(f"    {entity_name} }}o--|| {ref_entity} : has")

        except Exception:
            continue

    return "\n".join(lines)


def _generate_dbml_er(entities: list[dict]) -> str:
    """Generate DBML ER diagram."""
    lines = ["// Database Schema in DBML format"]
    lines.append("// Use https://dbdiagram.io to visualize")
    lines.append("")

    parser = get_sqlmodel_parser()

    for entity_info in entities:
        entity_name = entity_info["name"]
        try:
            schema = parser.get_entity(entity_name)

            # Table definition
            lines.append(f"Table {entity_name} {{")
            for field in schema.get("fields", []):
                field_type = field.get("type", "unknown")
                constraints = []
                if field.get("is_primary_key"):
                    constraints.append("pk")
                if not field.get("nullable", True):
                    constraints.append("not null")
                if field.get("unique"):
                    constraints.append("unique")

                constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
                lines.append(f"  {field['name']} {field_type}{constraint_str}")

            lines.append("}")
            lines.append("")

            # Foreign key relationships
            for field in schema.get("fields", []):
                if field.get("is_foreign_key") and field.get("foreign_key"):
                    ref = field["foreign_key"]
                    lines.append(f"Ref: {entity_name}.{field['name']} > {ref}")

            lines.append("")

        except Exception:
            continue

    return "\n".join(lines)


def _generate_ascii_er(entities: list[dict]) -> str:
    """Generate ASCII ER diagram."""
    lines = []
    parser = get_sqlmodel_parser()

    for entity_info in entities:
        entity_name = entity_info["name"]
        try:
            schema = parser.get_entity(entity_name)

            # Entity box
            lines.append(f"+{'-' * (len(entity_name) + 2)}+")
            lines.append(f"| {entity_name} |")
            lines.append(f"+{'-' * (len(entity_name) + 2)}+")

            # Key fields
            for field in schema.get("fields", [])[:5]:  # Limit to 5
                marker = "🔑" if field.get("is_primary_key") else "  "
                lines.append(f"  {marker} {field['name']}: {field.get('type', 'unknown')}")

            if len(schema.get("fields", [])) > 5:
                lines.append(f"  ... ({len(schema.get('fields', []))} fields total)")

            lines.append("")

        except Exception:
            continue

    return "\n".join(lines)


def _get_field_insights(field_name: str, matches: list[dict]) -> list[str]:
    """Get insights about a field based on common patterns."""
    insights = []

    if field_name == "organization_id":
        insights.append("🏢 Multi-tenancy: These entities are scoped by organization")
        insights.append("   Repositories should use _base_query_for_organization()")
        insights.append("   Unique constraints must include organization_id")

    elif field_name == "deleted_at":
        insights.append("🗑️  Soft Delete: These entities use soft delete pattern")
        insights.append("   Repositories must use _exclude_deleted() in queries")
        insights.append("   Unique indexes must be partial: postgresql_where=text('deleted_at IS NULL')")

    elif field_name == "created_at":
        insights.append("📅 Timestamp tracking: These entities track creation time")
        insights.append("   Use TimestampMixin for automatic timestamps")

    elif field_name == "created_by":
        insights.append("👤 User tracking: These entities track who created them")
        insights.append("   Use TrackingMixin for automatic user tracking")

    elif field_name == "is_active":
        insights.append("✅ Active flag: These entities can be enabled/disabled")
        insights.append("   Consider filtering by is_active in list queries")

    if len(matches) > 10:
        insights.append(f"⚠️  Common field: Found in {len(matches)} entities - likely a cross-cutting concern")

    return insights
