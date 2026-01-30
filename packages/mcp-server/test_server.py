#!/usr/bin/env python3
"""
Test script for the Quero Plantão MCP Server.

This script demonstrates the basic functionality of the MCP server
without requiring an OpenAI API key for the deterministic tools.

Usage:
    cd packages/mcp-server
    uv run python test_server.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from queroplantao_mcp.config import validate_project_structure
from queroplantao_mcp.parsers.openapi_parser import OpenAPIParser
from queroplantao_mcp.parsers.enum_parser import EnumParser
from queroplantao_mcp.parsers.sqlmodel_parser import SQLModelParser
from queroplantao_mcp.tools.business_rules import get_state_machine


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_project_structure():
    """Test project structure validation."""
    print_header("PROJECT STRUCTURE VALIDATION")

    structure = validate_project_structure()
    all_valid = all(structure.values())

    print(f"Status: {'✓ All OK' if all_valid else '✗ Issues found'}")
    print()

    for component, valid in structure.items():
        status = "✓" if valid else "✗"
        print(f"  {status} {component}")

    return all_valid


def test_openapi_parser():
    """Test OpenAPI specification parsing."""
    print_header("OPENAPI SPECIFICATION PARSING")

    try:
        parser = OpenAPIParser()

        # Test endpoints
        endpoints = parser.get_endpoints()
        print(f"✓ Endpoints loaded: {len(endpoints)}")

        # Group by module
        by_module = {}
        for ep in endpoints:
            module = ep.get("tags", ["unknown"])[0] if ep.get("tags") else "unknown"
            by_module[module] = by_module.get(module, 0) + 1

        print("Endpoints by module:")
        for module, count in sorted(by_module.items()):
            print(f"  - {module}: {count} endpoints")

        # Test schemas
        schemas = parser.list_schemas()
        print(f"✓ Schemas available: {len(schemas)}")

        # Test specific schema
        screening_schema = parser.get_schema("ScreeningProcessCreate")
        if screening_schema:
            props = screening_schema.get("properties", {})
            print(f"✓ ScreeningProcessCreate: {len(props)} properties")
            print(f"  Sample properties: {list(props.keys())[:5]}")
        else:
            print("⚠ ScreeningProcessCreate schema not found")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_enum_parser():
    """Test enum parsing."""
    print_header("ENUM PARSING")

    try:
        parser = EnumParser()

        # List all enums
        enums = parser.list_enums()
        print(f"✓ Enums found: {len(enums)}")

        # Group by module
        by_module = {}
        for enum in enums:
            module = enum.get("module", "unknown")
            by_module[module] = by_module.get(module, 0) + 1

        print("Enums by module:")
        for module, count in sorted(by_module.items()):
            print(f"  - {module}: {count} enums")

        # Test specific enum
        screening_status = parser.get_enum("ScreeningStatus")
        if screening_status:
            values = screening_status.get("values", {})
            print(f"✓ ScreeningStatus: {len(values)} values")
            if values:
                sample = list(values.keys())[:3]
                print(f"  Sample values: {sample}")
        else:
            print("⚠ ScreeningStatus enum not found")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sqlmodel_parser():
    """Test SQLModel entity parsing."""
    print_header("SQLMODEL ENTITY PARSING")

    try:
        parser = SQLModelParser()

        # List entities
        entities = parser.list_entities()
        print(f"✓ Entities found: {len(entities)}")

        # Group by module
        by_module = {}
        for entity in entities:
            module = entity.get("module", "unknown")
            by_module[module] = by_module.get(module, 0) + 1

        print("Entities by module:")
        for module, count in sorted(by_module.items()):
            print(f"  - {module}: {count} entities")

        # Test specific entity
        screening_process = parser.get_entity("ScreeningProcess")
        if screening_process:
            columns = screening_process.get("columns", [])
            relationships = screening_process.get("relationships", [])
            print(f"✓ ScreeningProcess: {len(columns)} columns, {len(relationships)} relationships")

            if columns:
                print(f"  Sample columns: {', '.join(col['name'] for col in columns[:3])}")
        else:
            print("⚠ ScreeningProcess entity not found")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_business_rules():
    """Test business rules tools."""
    print_header("BUSINESS RULES TOOLS")

    try:
        # Test state machine
        result = await get_state_machine("ScreeningProcess")
        print(f"✓ State machine for ScreeningProcess:")
        print(f"  - States: {len(result['states'])}")
        print(f"  - Transitions: {len(result['transitions'])}")
        print(f"  - UI hints: {len(result['ui_hints'])}")

        # Show sample transition
        if result['transitions']:
            transition = result['transitions'][0]
            print(f"  - Sample transition: {transition['from']} → {transition['to']}")
            print(f"    Trigger: {transition['trigger']}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_server_import():
    """Test MCP server import and tool registration."""
    print_header("MCP SERVER INITIALIZATION")

    try:
        from queroplantao_mcp.server import mcp
        from queroplantao_mcp.config import SERVER_NAME, SERVER_DESCRIPTION

        print(f"✓ Server name: {SERVER_NAME}")
        print(f"✓ Description: {SERVER_DESCRIPTION[:50]}...")

        tools_count = len(mcp._tool_manager._tools)
        print(f"✓ Tools registered: {tools_count}")

        # List tool categories
        tool_names = list(mcp._tool_manager._tools.keys())
        categories = {
            "Health": [t for t in tool_names if "health" in t],
            "API Schemas": [t for t in tool_names if any(x in t for x in ["module", "endpoint", "schema", "enum"])],
            "Database": [t for t in tool_names if any(x in t for x in ["entity", "er_diagram"])],
            "Business Rules": [t for t in tool_names if any(x in t for x in ["business_rule", "workflow", "state_machine", "user_story"])],
            "Code Analysis": [t for t in tool_names if any(x in t for x in ["use_case", "code", "error_code"])],
            "Context": [t for t in tool_names if "context" in t or "checklist" in t or "integration" in t],
        }

        print("Tools by category:")
        for category, tools in categories.items():
            if tools:
                print(f"  - {category}: {len(tools)} tools")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Quero Plantão MCP Server - Test Suite")
    print("=" * 60)

    tests = [
        ("Project Structure", test_project_structure),
        ("OpenAPI Parser", test_openapi_parser),
        ("Enum Parser", test_enum_parser),
        ("SQLModel Parser", test_sqlmodel_parser),
        ("Business Rules", test_business_rules),
        ("Server Import", test_server_import),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔍 Running {name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append(False)

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! MCP server is ready for use.")
        print("\nNext steps:")
        print("1. Set up your OpenAI API key: cp .env.example .env")
        print("2. Run the server: uv run mcp-server")
        print("3. Connect your MCP client (Claude Desktop, etc.)")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)