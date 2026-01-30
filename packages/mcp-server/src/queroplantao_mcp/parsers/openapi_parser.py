"""
Parser for OpenAPI specification.

Extracts endpoint definitions, schemas, and other API information.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from queroplantao_mcp.config import OPENAPI_SPEC_PATH


@dataclass
class ParameterInfo:
    """Information about an endpoint parameter."""

    name: str
    location: str  # path, query, header
    required: bool
    schema_type: str
    description: str | None = None


@dataclass
class EndpointInfo:
    """Information about an API endpoint."""

    path: str
    method: str
    operation_id: str | None
    summary: str | None
    description: str | None
    tags: list[str]
    request_body_schema: str | None
    response_schema: str | None
    path_params: list[ParameterInfo]
    query_params: list[ParameterInfo]
    requires_auth: bool = True
    requires_org_header: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "method": self.method,
            "operation_id": self.operation_id,
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "request_body_schema": self.request_body_schema,
            "response_schema": self.response_schema,
            "path_params": [p.name for p in self.path_params],
            "query_params": [
                {
                    "name": p.name,
                    "required": p.required,
                    "type": p.schema_type,
                    "description": p.description,
                }
                for p in self.query_params
            ],
            "requires_auth": self.requires_auth,
            "requires_org_header": self.requires_org_header,
        }


@dataclass
class SchemaInfo:
    """Information about a Pydantic/OpenAPI schema."""

    name: str
    description: str | None
    properties: dict[str, dict]
    required: list[str]
    type_: str = "object"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type_,
            "properties": self.properties,
            "required": self.required,
        }


@dataclass
class ModuleInfo:
    """Information about an API module (based on tags)."""

    name: str
    description: str | None
    endpoint_count: int
    endpoints: list[str] = field(default_factory=list)


class OpenAPIParser:
    """Parser for the OpenAPI specification."""

    def __init__(self, spec_path: Path | None = None) -> None:
        self._spec_path = spec_path or OPENAPI_SPEC_PATH
        self._spec: dict[str, Any] | None = None
        self._endpoints: list[EndpointInfo] | None = None

    def _load_spec(self) -> dict[str, Any]:
        """Load the OpenAPI specification."""
        if self._spec is not None:
            return self._spec

        if not self._spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec not found at {self._spec_path}")

        with open(self._spec_path, encoding="utf-8") as f:
            self._spec = json.load(f)

        return self._spec

    def _resolve_ref(self, ref: str) -> dict[str, Any]:
        """Resolve a $ref pointer to its schema."""
        spec = self._load_spec()

        if not ref.startswith("#/"):
            return {}

        parts = ref[2:].split("/")
        current = spec

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return {}

        return current if isinstance(current, dict) else {}

    def _get_schema_name(self, schema: dict) -> str | None:
        """Extract schema name from a $ref or return None."""
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                return ref.split("/")[-1]
        return None

    def _parse_parameter(self, param: dict) -> ParameterInfo:
        """Parse a parameter definition."""
        schema = param.get("schema", {})
        schema_type = schema.get("type", "string")

        # Handle enums
        if "enum" in schema:
            schema_type = f"enum[{', '.join(str(v) for v in schema['enum'])}]"

        # Handle arrays
        if schema_type == "array" and "items" in schema:
            items = schema["items"]
            item_type = items["$ref"].split("/")[-1] if "$ref" in items else items.get("type", "any")
            schema_type = f"array[{item_type}]"

        return ParameterInfo(
            name=param.get("name", ""),
            location=param.get("in", "query"),
            required=param.get("required", False),
            schema_type=schema_type,
            description=param.get("description"),
        )

    def _parse_endpoints(self) -> list[EndpointInfo]:
        """Parse all endpoints from the spec."""
        if self._endpoints is not None:
            return self._endpoints

        spec = self._load_spec()
        paths = spec.get("paths", {})
        endpoints: list[EndpointInfo] = []

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    endpoints.append(self._parse_endpoint(path, method, operation))

        self._endpoints = endpoints
        return endpoints

    def _parse_endpoint(self, path: str, method: str, operation: dict) -> EndpointInfo:
        """Parse a single endpoint."""
        # Parse parameters
        params = operation.get("parameters", [])
        path_params = [self._parse_parameter(p) for p in params if p.get("in") == "path"]
        query_params = [self._parse_parameter(p) for p in params if p.get("in") == "query"]

        # Check for auth requirement (security)
        security = operation.get("security", [])
        requires_auth = len(security) > 0

        # Check for organization header
        header_params = [p for p in params if p.get("in") == "header"]
        requires_org_header = any(p.get("name") == "X-Organization-ID" for p in header_params)

        # Get request body schema
        request_body_schema = None
        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {})
            json_content = content.get("application/json", {})
            if "schema" in json_content:
                request_body_schema = self._get_schema_name(json_content["schema"])

        # Get response schema (from 200 or 201 response)
        response_schema = None
        responses = operation.get("responses", {})
        for status in ["200", "201"]:
            if status in responses:
                content = responses[status].get("content", {})
                json_content = content.get("application/json", {})
                if "schema" in json_content:
                    response_schema = self._get_schema_name(json_content["schema"])
                    break

        return EndpointInfo(
            path=path,
            method=method.upper(),
            operation_id=operation.get("operationId"),
            summary=operation.get("summary"),
            description=operation.get("description"),
            tags=operation.get("tags", []),
            request_body_schema=request_body_schema,
            response_schema=response_schema,
            path_params=path_params,
            query_params=query_params,
            requires_auth=requires_auth,
            requires_org_header=requires_org_header,
        )

    def get_spec(self) -> dict[str, Any]:
        """Get the full OpenAPI specification."""
        return self._load_spec()

    def get_info(self) -> dict[str, Any]:
        """Get API info (title, version, description)."""
        spec = self._load_spec()
        return spec.get("info", {})

    def list_modules(self) -> list[dict]:
        """
        List all modules based on tags.

        Returns:
            List of modules with name, description, and endpoint count.
        """
        spec = self._load_spec()
        endpoints = self._parse_endpoints()

        # Get tags from spec
        tags_info = {t["name"]: t.get("description") for t in spec.get("tags", [])}

        # Count endpoints per tag
        tag_counts: dict[str, list[str]] = {}
        for endpoint in endpoints:
            for tag in endpoint.tags:
                if tag not in tag_counts:
                    tag_counts[tag] = []
                tag_counts[tag].append(f"{endpoint.method} {endpoint.path}")

        modules = []
        for tag, endpoint_list in tag_counts.items():
            modules.append(
                {
                    "name": tag.lower().replace(" ", "_"),
                    "display_name": tag,
                    "description": tags_info.get(tag),
                    "endpoint_count": len(endpoint_list),
                }
            )

        return sorted(modules, key=lambda x: x["name"])

    def get_endpoints(
        self,
        module: str | None = None,
        method: str | None = None,
        tag: str | None = None,
    ) -> list[dict]:
        """
        Get endpoints, optionally filtered.

        Args:
            module: Filter by module/tag name.
            method: Filter by HTTP method (GET, POST, etc.).
            tag: Filter by exact tag name.

        Returns:
            List of endpoint definitions.
        """
        endpoints = self._parse_endpoints()
        result = []

        for endpoint in endpoints:
            # Filter by module/tag
            if module:
                module_lower = module.lower()
                if not any(t.lower() == module_lower for t in endpoint.tags):
                    continue

            # Filter by tag (exact match)
            if tag and tag not in endpoint.tags:
                continue

            # Filter by method
            if method and endpoint.method.upper() != method.upper():
                continue

            result.append(endpoint.to_dict())

        return result

    def get_endpoint(self, path: str, method: str) -> dict | None:
        """
        Get a specific endpoint by path and method.

        Args:
            path: The endpoint path (e.g., "/organizations/{organization_id}/screenings").
            method: The HTTP method (GET, POST, etc.).

        Returns:
            Endpoint definition or None if not found.
        """
        endpoints = self._parse_endpoints()

        for endpoint in endpoints:
            if endpoint.path == path and endpoint.method.upper() == method.upper():
                return endpoint.to_dict()

        return None

    def list_schemas(self) -> list[dict]:
        """
        List all schemas in the spec.

        Returns:
            List of schema summaries with name and property count.
        """
        spec = self._load_spec()
        schemas = spec.get("components", {}).get("schemas", {})

        result = []
        for name, schema in schemas.items():
            result.append(
                {
                    "name": name,
                    "type": schema.get("type", "object"),
                    "description": schema.get("description"),
                    "property_count": len(schema.get("properties", {})),
                }
            )

        return sorted(result, key=lambda x: x["name"])

    def get_schema(self, schema_name: str) -> dict | None:
        """
        Get detailed schema information.

        Args:
            schema_name: Name of the schema (e.g., "ScreeningProcessCreate").

        Returns:
            Schema definition with resolved properties.
        """
        spec = self._load_spec()
        schemas = spec.get("components", {}).get("schemas", {})

        if schema_name not in schemas:
            return None

        schema = schemas[schema_name]

        # Resolve property types
        properties = {}
        for prop_name, prop_def in schema.get("properties", {}).items():
            prop_info = self._resolve_property(prop_def)
            properties[prop_name] = prop_info

        return {
            "name": schema_name,
            "description": schema.get("description"),
            "type": schema.get("type", "object"),
            "properties": properties,
            "required": schema.get("required", []),
        }

    def _resolve_property(self, prop_def: dict) -> dict:
        """Resolve a property definition to a simple description."""
        result: dict[str, Any] = {}

        # Handle $ref
        if "$ref" in prop_def:
            ref_name = prop_def["$ref"].split("/")[-1]
            result["type"] = ref_name
            result["is_ref"] = True
            return result

        # Basic type
        result["type"] = prop_def.get("type", "any")
        result["is_ref"] = False

        # Handle anyOf/oneOf (for Optional types)
        if "anyOf" in prop_def:
            types = []
            for sub in prop_def["anyOf"]:
                if "$ref" in sub:
                    types.append(sub["$ref"].split("/")[-1])
                elif sub.get("type") == "null":
                    result["nullable"] = True
                else:
                    types.append(sub.get("type", "any"))
            if types:
                result["type"] = types[0] if len(types) == 1 else f"union[{', '.join(types)}]"

        # Handle enum
        if "enum" in prop_def:
            result["enum"] = prop_def["enum"]

        # Handle array
        if result["type"] == "array" and "items" in prop_def:
            items = prop_def["items"]
            item_type = items["$ref"].split("/")[-1] if "$ref" in items else items.get("type", "any")
            result["type"] = f"array[{item_type}]"

        # Additional metadata
        if "description" in prop_def:
            result["description"] = prop_def["description"]
        if "default" in prop_def:
            result["default"] = prop_def["default"]
        if "format" in prop_def:
            result["format"] = prop_def["format"]
        if "pattern" in prop_def:
            result["pattern"] = prop_def["pattern"]
        if "minLength" in prop_def:
            result["minLength"] = prop_def["minLength"]
        if "maxLength" in prop_def:
            result["maxLength"] = prop_def["maxLength"]

        return result

    def get_schema_as_form_fields(self, schema_name: str) -> dict | None:
        """
        Get schema as form fields with UI hints.

        This is useful for generating forms in the frontend.

        Args:
            schema_name: Name of the schema.

        Returns:
            Schema with fields formatted for form generation.
        """
        schema = self.get_schema(schema_name)
        if not schema:
            return None

        fields = []
        for prop_name, prop_def in schema["properties"].items():
            field_info = {
                "name": prop_name,
                "type": prop_def.get("type", "string"),
                "required": prop_name in schema.get("required", []),
                "nullable": prop_def.get("nullable", False),
            }

            # Add description
            if "description" in prop_def:
                field_info["description"] = prop_def["description"]

            # Add default
            if "default" in prop_def:
                field_info["default"] = prop_def["default"]

            # Add enum options
            if "enum" in prop_def:
                field_info["options"] = prop_def["enum"]

            # Determine input type hint
            field_info["input_type"] = self._get_input_type(prop_name, prop_def)

            fields.append(field_info)

        return {
            "name": schema_name,
            "description": schema.get("description"),
            "fields": fields,
        }

    def _get_input_type(self, prop_name: str, prop_def: dict) -> str:
        """Determine the appropriate input type for a property."""
        prop_type = prop_def.get("type", "string")
        prop_format = prop_def.get("format", "")

        # Check for enum
        if "enum" in prop_def or "options" in prop_def:
            return "select"

        # Check format
        if prop_format == "date":
            return "date"
        if prop_format == "date-time":
            return "datetime"
        if prop_format == "email":
            return "email"
        if prop_format == "uri":
            return "url"

        # Check name patterns
        name_lower = prop_name.lower()
        if "email" in name_lower:
            return "email"
        if "phone" in name_lower or "telefone" in name_lower:
            return "phone"
        if "cpf" in name_lower:
            return "cpf"
        if "cnpj" in name_lower:
            return "cnpj"
        if "password" in name_lower or "senha" in name_lower:
            return "password"
        if "date" in name_lower or "data" in name_lower:
            return "date"
        if "url" in name_lower or "link" in name_lower:
            return "url"

        # Check type
        if prop_type == "boolean":
            return "checkbox"
        if prop_type == "integer" or prop_type == "number":
            return "number"
        if prop_type.startswith("array"):
            return "multiselect"

        # Check if it's a reference to another schema
        if prop_def.get("is_ref"):
            return "reference"

        return "text"


# Singleton instance
_parser: OpenAPIParser | None = None


def get_openapi_parser() -> OpenAPIParser:
    """Get the singleton OpenAPI parser instance."""
    global _parser
    if _parser is None:
        _parser = OpenAPIParser()
    return _parser
