"""
Context tools for the MCP server.

These tools help manage development context and generate
implementation checklists for frontend development.
"""

from __future__ import annotations

from queroplantao_mcp.config import MODULES_DIR
from queroplantao_mcp.llm import get_llm_client
from queroplantao_mcp.parsers.openapi_parser import OpenAPIParser

# Development context storage (in-memory for session)
_development_context: dict = {}


async def set_development_context(
    feature: str,
    module: str,
    user_story: str | None = None,
    notes: str | None = None,
) -> dict:
    """
    Set the current development context.

    This helps the LLM understand what the developer is working on
    and provide more relevant responses.

    Args:
        feature: Name of the feature being developed (e.g., "tela de triagem",
                 "lista de profissionais").
        module: Module being worked on (e.g., "screening", "professionals").
        user_story: Optional user story being implemented.
        notes: Optional additional notes.

    Returns:
        Confirmation of context set with relevant resources.
    """
    global _development_context

    _development_context = {
        "feature": feature,
        "module": module,
        "user_story": user_story,
        "notes": notes,
    }

    # Gather relevant resources
    resources = await _gather_context_resources(module, feature)

    return {
        "status": "Context set successfully",
        "context": _development_context,
        "relevant_resources": resources,
        "tip": "Use get_implementation_checklist to get a step-by-step guide",
    }


async def get_development_context() -> dict:
    """
    Get the current development context.

    Returns:
        Current context if set, or empty state.
    """
    if not _development_context:
        return {
            "status": "No context set",
            "tip": "Use set_development_context to set your current focus",
        }

    return {
        "status": "Context active",
        "context": _development_context,
    }


async def clear_development_context() -> dict:
    """
    Clear the current development context.

    Returns:
        Confirmation message.
    """
    global _development_context
    _development_context = {}

    return {
        "status": "Context cleared",
    }


async def _gather_context_resources(module: str, feature: str) -> dict:
    """Gather relevant resources for the context."""
    resources: dict = {
        "endpoints": [],
        "schemas": [],
        "docs": None,
    }

    # Find relevant endpoints
    try:
        parser = OpenAPIParser()
        endpoints = parser.get_endpoints()

        feature_keywords = feature.lower().split()

        for endpoint in endpoints:
            path_lower = endpoint.get("path", "").lower()
            # Check if endpoint matches module or feature
            if module in path_lower or any(kw in path_lower for kw in feature_keywords):
                resources["endpoints"].append(
                    {
                        "method": endpoint.get("method"),
                        "path": endpoint.get("path"),
                        "summary": endpoint.get("summary"),
                    }
                )
    except Exception:
        pass

    # Find relevant schemas
    try:
        parser = OpenAPIParser()
        schemas = parser.list_schemas()

        for schema_name in schemas:
            name_lower = schema_name.lower()
            if module.lower() in name_lower:
                resources["schemas"].append(schema_name)
    except Exception:
        pass

    # Check for module docs
    docs_path = MODULES_DIR.parent.parent / "docs" / "modules" / f"{module.upper()}_MODULE.md"
    if docs_path.exists():
        resources["docs"] = str(docs_path.name)

    return resources


async def get_implementation_checklist(
    feature: str | None = None,
    module: str | None = None,
) -> dict:
    """
    Generate an implementation checklist for a feature.

    Uses the current context if feature/module not provided.

    Args:
        feature: Optional feature name (uses context if not provided).
        module: Optional module name (uses context if not provided).

    Returns:
        Step-by-step implementation checklist.
    """
    # Use context if not provided
    if not feature:
        feature = _development_context.get("feature")
    if not module:
        module = _development_context.get("module")

    if not feature or not module:
        return {
            "error": "No feature or module specified",
            "tip": "Either provide feature/module or use set_development_context first",
        }

    # Gather module info
    resources = await _gather_context_resources(module, feature)

    # Generate checklist with LLM
    llm = get_llm_client()

    prompt = f"""Generate an implementation checklist for a frontend developer building:

Feature: {feature}
Module: {module}
Available endpoints: {len(resources["endpoints"])} endpoints
Available schemas: {len(resources["schemas"])} schemas

Provide a step-by-step checklist that includes:

1. **API Integration Setup**
   - Which endpoints to call
   - Request/response handling
   - Error codes to handle

2. **State Management**
   - What data to store
   - Loading/error states

3. **UI Components**
   - Form fields needed
   - Validation rules
   - User feedback

4. **Edge Cases**
   - What can go wrong
   - How to handle each case

5. **Testing Considerations**
   - What to test
   - Mock data suggestions

Format as a practical checklist with [ ] checkboxes."""

    checklist = await llm.chat(prompt)

    return {
        "feature": feature,
        "module": module,
        "checklist": checklist,
        "endpoints": resources["endpoints"][:5],  # Limit for readability
        "schemas": resources["schemas"][:10],  # Limit for readability
    }


async def suggest_api_integration(
    feature: str,
    existing_code: str | None = None,
) -> dict:
    """
    Suggest how to integrate the API for a feature.

    Args:
        feature: Feature being implemented (e.g., "professional listing with filters").
        existing_code: Optional existing frontend code to analyze.

    Returns:
        API integration suggestions with code examples.
    """
    # Get relevant endpoints
    parser = OpenAPIParser()
    endpoints = parser.get_endpoints()

    feature_keywords = feature.lower().split()
    relevant_endpoints = []

    for endpoint in endpoints:
        path_lower = endpoint.get("path", "").lower()
        summary_lower = (endpoint.get("summary") or "").lower()

        if any(kw in path_lower or kw in summary_lower for kw in feature_keywords):
            relevant_endpoints.append(endpoint)

    if not relevant_endpoints:
        return {
            "feature": feature,
            "error": "No matching endpoints found",
            "suggestion": "Try with different keywords or use list_endpoints",
        }

    # Generate suggestions with LLM
    llm = get_llm_client()

    prompt = f"""Suggest how to integrate these API endpoints for the feature: {feature}

Endpoints:
{_format_endpoints_for_prompt(relevant_endpoints)}

{"Existing code:\n" + existing_code if existing_code else ""}

Provide:
1. **Recommended Approach**: Best way to structure the integration
2. **TypeScript Code Example**: Using the api-client package
3. **Error Handling**: Which errors to expect and how to handle them
4. **Loading States**: Suggested loading state management

Focus on practical, copy-paste ready code."""

    suggestions = await llm.chat(prompt)

    return {
        "feature": feature,
        "endpoints": relevant_endpoints,
        "suggestions": suggestions,
    }


def _format_endpoints_for_prompt(endpoints: list[dict]) -> str:
    """Format endpoints for LLM prompt."""
    lines = []
    for ep in endpoints[:5]:  # Limit to 5
        method = ep.get("method", "").upper()
        path = ep.get("path", "")
        summary = ep.get("summary", "")
        lines.append(f"- {method} {path}: {summary}")
    return "\n".join(lines)
