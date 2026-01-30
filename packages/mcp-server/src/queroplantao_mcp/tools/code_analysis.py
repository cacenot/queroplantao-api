"""
Code Analysis tools for the MCP server.

These tools provide LLM-powered code analysis, use case explanations,
and code search capabilities.
"""

from __future__ import annotations

from pathlib import Path

from queroplantao_mcp.config import MODULES_DIR, PROJECT_ROOT
from queroplantao_mcp.llm import get_llm_client


async def analyze_use_case(use_case: str) -> dict:
    """
    Analyze a use case and explain its logic.

    Args:
        use_case: Name of the use case (e.g., "CreateScreeningProcessUseCase",
                  "UpdateProfessionalUseCase").

    Returns:
        Analysis with summary, dependencies, validations, side effects,
        and frontend notes.
    """
    # Find the use case file
    use_case_file = await _find_use_case_file(use_case)

    if not use_case_file:
        return {
            "use_case": use_case,
            "error": f"Use case not found: {use_case}",
            "suggestion": "Try searching with find_related_code tool",
        }

    # Read the file
    code = use_case_file.read_text(encoding="utf-8")

    # Analyze with LLM
    llm = get_llm_client()
    analysis = await llm.analyze_code(
        code=code,
        question=f"""Analyze this use case '{use_case}' and provide:

1. **Summary**: What does this use case do? (1-2 sentences)
2. **Dependencies**: What repositories/services are injected?
3. **Validations**: What business rules are validated? List each with the error code raised.
4. **Side Effects**: What entities are created/updated/deleted?
5. **Frontend Notes**: What should the frontend developer know?
   - Which fields are really required vs optional?
   - Any special handling needed?
   - Suggested form sections?

Format as structured sections.""",
        context="This is from the Quero Plantão API, a medical shift management platform.",
    )

    return {
        "use_case": use_case,
        "file_path": str(use_case_file.relative_to(PROJECT_ROOT)),
        "analysis": analysis,
    }


async def _find_use_case_file(use_case_name: str) -> Path | None:
    """Find a use case file by name."""
    # Convert CamelCase to snake_case for file search
    import re

    # Handle common patterns
    name = use_case_name.replace("UseCase", "").strip()
    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    # Search in all modules
    for module_dir in MODULES_DIR.iterdir():
        if not module_dir.is_dir():
            continue

        use_cases_dir = module_dir / "use_cases"
        if not use_cases_dir.exists():
            continue

        # Search for matching files
        for py_file in use_cases_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Check file name
            if snake_name in py_file.stem:
                return py_file

            # Check file content for class name
            try:
                content = py_file.read_text(encoding="utf-8")
                if f"class {use_case_name}" in content:
                    return py_file
            except Exception:
                continue

    return None


async def find_related_code(
    concept: str,
    code_type: str = "all",
    module: str | None = None,
) -> dict:
    """
    Find code related to a concept.

    Args:
        concept: Concept to search for (e.g., "validação de documento",
                 "family scope", "soft delete").
        code_type: Type of code to search - "all", "use_cases", "repositories",
                   "routes", "schemas", "models".
        module: Optional module to limit search.

    Returns:
        List of matching files with relevant excerpts.
    """

    # Build search directories based on code_type
    search_dirs: list[Path] = []

    if module:
        module_path = MODULES_DIR / module
        if not module_path.exists():
            return {
                "concept": concept,
                "error": f"Module not found: {module}",
            }
        base_dirs = [module_path]
    else:
        base_dirs = [d for d in MODULES_DIR.iterdir() if d.is_dir()]

    for base in base_dirs:
        if code_type == "all":
            search_dirs.append(base)
        elif code_type == "use_cases":
            if (base / "use_cases").exists():
                search_dirs.append(base / "use_cases")
        elif code_type == "repositories":
            if (base / "infrastructure" / "repositories").exists():
                search_dirs.append(base / "infrastructure" / "repositories")
        elif code_type == "routes":
            if (base / "presentation").exists():
                search_dirs.append(base / "presentation")
        elif code_type == "schemas":
            if (base / "domain" / "schemas").exists():
                search_dirs.append(base / "domain" / "schemas")
        elif code_type == "models" and (base / "domain" / "models").exists():
            search_dirs.append(base / "domain" / "models")

    # Search for the concept
    results: list[dict] = []
    keywords = concept.lower().split()

    for search_dir in search_dirs:
        for py_file in search_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                content_lower = content.lower()

                # Check if any keyword matches
                matches = sum(1 for kw in keywords if kw in content_lower)
                if matches >= len(keywords) / 2:  # At least half the keywords match
                    # Find relevant lines
                    lines = content.split("\n")
                    relevant_lines: list[tuple[int, str]] = []

                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        if any(kw in line_lower for kw in keywords):
                            relevant_lines.append((i + 1, line.strip()))

                    if relevant_lines:
                        results.append(
                            {
                                "file": str(py_file.relative_to(PROJECT_ROOT)),
                                "match_count": matches,
                                "relevant_lines": relevant_lines[:5],  # Limit
                            }
                        )
            except Exception:
                continue

    # Sort by match count
    results.sort(key=lambda x: x["match_count"], reverse=True)

    return {
        "concept": concept,
        "code_type": code_type,
        "module": module,
        "results": results[:10],  # Limit to top 10
        "total_matches": len(results),
    }


async def explain_code_snippet(
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> dict:
    """
    Explain a code snippet.

    Args:
        file_path: Path to the file (relative to project root or absolute).
        start_line: Optional starting line number (1-indexed).
        end_line: Optional ending line number (1-indexed).

    Returns:
        Explanation of the code with implications.
    """
    # Resolve file path
    full_path = Path(file_path) if file_path.startswith("/") else PROJECT_ROOT / file_path

    if not full_path.exists():
        return {
            "file_path": file_path,
            "error": f"File not found: {file_path}",
        }

    # Read file content
    content = full_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Extract snippet
    if start_line and end_line:
        snippet_lines = lines[start_line - 1 : end_line]
        snippet = "\n".join(snippet_lines)
        line_range = f"L{start_line}-L{end_line}"
    elif start_line:
        snippet_lines = lines[start_line - 1 : start_line + 50]  # 50 lines from start
        snippet = "\n".join(snippet_lines)
        line_range = f"L{start_line}+"
    else:
        snippet = content
        line_range = "full file"

    # Analyze with LLM
    llm = get_llm_client()
    explanation = await llm.analyze_code(
        code=snippet,
        question="""Explain this code:

1. What does this code do?
2. What are the key patterns or techniques used?
3. Are there any important side effects or considerations?
4. How would this affect frontend implementation?

Be concise and practical.""",
        context=f"File: {file_path} ({line_range}). This is from the Quero Plantão API.",
    )

    return {
        "file_path": str(full_path.relative_to(PROJECT_ROOT)),
        "line_range": line_range,
        "explanation": explanation,
    }


async def get_error_codes(
    module: str | None = None,
) -> dict:
    """
    Get all error codes defined in the project.

    Args:
        module: Optional module to filter by.

    Returns:
        List of error codes with their messages and HTTP status.
    """
    error_codes_path = PROJECT_ROOT / "src" / "app" / "constants" / "error_codes.py"

    if not error_codes_path.exists():
        return {
            "error": "Error codes file not found",
            "path": str(error_codes_path),
        }

    content = error_codes_path.read_text(encoding="utf-8")

    # Parse error codes using AST
    import ast

    tree = ast.parse(content)

    error_codes: list[dict] = []
    current_class = None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("ErrorCodes"):
            current_class = node.name
            # Extract prefix from class name
            prefix = node.name.replace("ErrorCodes", "").upper()

            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and isinstance(item.value, ast.Constant):
                            code_value = item.value.value

                            # Determine module from prefix
                            code_module = _get_module_from_prefix(prefix)

                            if module and code_module != module:
                                continue

                            error_codes.append(
                                {
                                    "code": code_value,
                                    "enum_class": current_class,
                                    "module": code_module,
                                }
                            )

    return {
        "module": module,
        "error_codes": error_codes,
        "total": len(error_codes),
    }


def _get_module_from_prefix(prefix: str) -> str:
    """Map error code prefix to module name."""
    prefix_map = {
        "AUTH": "auth",
        "ORG": "organizations",
        "PROF": "professionals",
        "SCREENING": "screening",
        "USER": "users",
        "CONTRACT": "contracts",
        "RESOURCE": "shared",
        "VALIDATION": "shared",
    }
    return prefix_map.get(prefix, "unknown")
