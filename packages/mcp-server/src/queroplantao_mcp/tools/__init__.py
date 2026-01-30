"""
Tools package for the MCP server.

This package contains specialized tools organized by category:
- business_rules: LLM-powered business rule explanations and workflows
- code_analysis: Code analysis, use case explanation, error codes
- context: Development context management and implementation checklists
"""

from __future__ import annotations

from queroplantao_mcp.tools.business_rules import (
    explain_business_rule,
    get_state_machine,
    get_workflow_diagram,
    validate_user_story,
)
from queroplantao_mcp.tools.code_analysis import (
    analyze_use_case,
    explain_code_snippet,
    find_related_code,
    get_error_codes,
)
from queroplantao_mcp.tools.context import (
    clear_development_context,
    get_development_context,
    get_implementation_checklist,
    set_development_context,
    suggest_api_integration,
)

__all__ = [
    # Business Rules
    "explain_business_rule",
    "get_workflow_diagram",
    "get_state_machine",
    "validate_user_story",
    # Code Analysis
    "analyze_use_case",
    "find_related_code",
    "explain_code_snippet",
    "get_error_codes",
    # Context
    "set_development_context",
    "get_development_context",
    "clear_development_context",
    "get_implementation_checklist",
    "suggest_api_integration",
]
