"""
Parser for SQLModel entity files.

Extracts entity definitions, columns, relationships, and constraints.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from queroplantao_mcp.config import MODULES_DIR, SHARED_DIR

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class ColumnInfo:
    """Information about a database column."""

    name: str
    type_: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str | None = None
    default: Any = None
    description: str | None = None
    unique: bool = False
    index: bool = False


@dataclass
class RelationshipInfo:
    """Information about a relationship."""

    name: str
    target: str
    type_: str  # one-to-one, one-to-many, many-to-one, many-to-many
    back_populates: str | None = None
    lazy: str | None = None


@dataclass
class IndexInfo:
    """Information about a database index."""

    name: str | None
    columns: list[str]
    unique: bool = False
    partial_condition: str | None = None


@dataclass
class EntityInfo:
    """Information about a SQLModel entity."""

    name: str
    table_name: str | None
    module: str
    file_path: str
    docstring: str | None = None
    base_classes: list[str] = field(default_factory=list)
    columns: list[ColumnInfo] = field(default_factory=list)
    relationships: list[RelationshipInfo] = field(default_factory=list)
    indexes: list[IndexInfo] = field(default_factory=list)
    mixins: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "module": self.module,
            "file_path": self.file_path,
            "docstring": self.docstring,
            "base_classes": self.base_classes,
            "mixins": self.mixins,
            "columns": [
                {
                    "name": c.name,
                    "type": c.type_,
                    "nullable": c.nullable,
                    "primary_key": c.primary_key,
                    "foreign_key": c.foreign_key,
                    "default": str(c.default) if c.default is not None else None,
                    "description": c.description,
                    "unique": c.unique,
                    "index": c.index,
                }
                for c in self.columns
            ],
            "relationships": [
                {
                    "name": r.name,
                    "target": r.target,
                    "type": r.type_,
                    "back_populates": r.back_populates,
                }
                for r in self.relationships
            ],
            "indexes": [
                {
                    "name": i.name,
                    "columns": i.columns,
                    "unique": i.unique,
                    "partial_condition": i.partial_condition,
                }
                for i in self.indexes
            ],
        }


# Known mixins and what they provide
KNOWN_MIXINS = {
    "PrimaryKeyMixin": ["id (UUID primary key)"],
    "TimestampMixin": ["created_at", "updated_at"],
    "SoftDeleteMixin": ["deleted_at"],
    "TrackingMixin": ["created_by", "updated_by"],
    "VerificationMixin": ["verification_status", "verified_at", "verified_by"],
}


def _get_module_from_path(file_path: Path) -> str:
    """Determine the module name from a file path."""
    path_str = str(file_path)

    if str(SHARED_DIR) in path_str:
        return "shared"

    for module_name in [
        "professionals",
        "screening",
        "users",
        "organizations",
        "contracts",
        "units",
        "shifts",
        "schedules",
        "job_postings",
    ]:
        if f"/modules/{module_name}/" in path_str:
            return module_name

    return "unknown"


def _extract_docstring(node: ast.ClassDef) -> str | None:
    """Extract docstring from a class definition."""
    if (
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    ):
        return node.body[0].value.value.strip()
    return None


def _get_base_names(node: ast.ClassDef) -> list[str]:
    """Get names of base classes."""
    names = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _is_sqlmodel_entity(node: ast.ClassDef, source: str) -> bool:
    """Check if a class is a SQLModel entity (has table=True or inherits from known base)."""
    # Check for table=True in class keywords
    for keyword in node.keywords:
        if keyword.arg == "table" and isinstance(keyword.value, ast.Constant):
            if keyword.value.value is True:
                return True

    # Check base classes for known patterns
    base_names = _get_base_names(node)
    model_patterns = ["BaseModel", "SQLModel"]

    # Only consider as entity if it has table=True somewhere or ends with known suffixes
    name = node.name
    if any(name.endswith(suffix) for suffix in ["Base", "Mixin"]):
        return False

    return any(base in model_patterns for base in base_names)


def _extract_field_info(node: ast.AnnAssign, source_lines: list[str]) -> ColumnInfo | None:
    """Extract field information from an annotated assignment."""
    if not isinstance(node.target, ast.Name):
        return None

    field_name = node.target.id

    # Skip private fields
    if field_name.startswith("_"):
        return None

    # Get type annotation
    type_str = _get_type_str(node.annotation)

    # Check if it's a Field() call
    field_kwargs: dict[str, Any] = {}

    if node.value and isinstance(node.value, ast.Call):
        func = node.value.func
        if isinstance(func, ast.Name) and func.id == "Field":
            field_kwargs = _extract_field_kwargs(node.value)
        elif isinstance(func, ast.Name) and func.id == "Relationship":
            return None  # Skip relationships here

    # Determine if nullable
    nullable = "Optional" in type_str or "None" in type_str or field_kwargs.get("default") is not None

    return ColumnInfo(
        name=field_name,
        type_=type_str,
        nullable=nullable,
        primary_key=field_kwargs.get("primary_key", False),
        foreign_key=field_kwargs.get("foreign_key"),
        default=field_kwargs.get("default"),
        description=field_kwargs.get("description"),
        unique=field_kwargs.get("unique", False),
        index=field_kwargs.get("index", False),
    )


def _extract_relationship_info(node: ast.AnnAssign) -> RelationshipInfo | None:
    """Extract relationship information from an annotated assignment."""
    if not isinstance(node.target, ast.Name):
        return None

    if not node.value or not isinstance(node.value, ast.Call):
        return None

    func = node.value.func
    if not isinstance(func, ast.Name) or func.id != "Relationship":
        return None

    field_name = node.target.id
    target_type = _get_type_str(node.annotation)

    # Clean up target type
    target_type = target_type.replace('"', "").replace("'", "")
    target_type = target_type.replace("Optional[", "").rstrip("]")
    target_type = target_type.replace("list[", "").rstrip("]")

    # Determine relationship type
    type_str = _get_type_str(node.annotation)
    if "list[" in type_str.lower():
        rel_type = "one-to-many"
    else:
        rel_type = "many-to-one"

    # Extract kwargs
    kwargs = _extract_field_kwargs(node.value)

    return RelationshipInfo(
        name=field_name,
        target=target_type,
        type_=rel_type,
        back_populates=kwargs.get("back_populates"),
        lazy=kwargs.get("sa_relationship_kwargs", {}).get("lazy"),
    )


def _get_type_str(annotation: ast.expr) -> str:
    """Convert AST annotation to string."""
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Constant):
        return str(annotation.value)
    elif isinstance(annotation, ast.Subscript):
        base = _get_type_str(annotation.value)
        if isinstance(annotation.slice, ast.Tuple):
            args = ", ".join(_get_type_str(elt) for elt in annotation.slice.elts)
        else:
            args = _get_type_str(annotation.slice)
        return f"{base}[{args}]"
    elif isinstance(annotation, ast.Attribute):
        return annotation.attr
    elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        # Handle Union types with | operator
        left = _get_type_str(annotation.left)
        right = _get_type_str(annotation.right)
        return f"{left} | {right}"
    else:
        return "Any"


def _extract_field_kwargs(call_node: ast.Call) -> dict[str, Any]:
    """Extract keyword arguments from a Field() call."""
    kwargs: dict[str, Any] = {}

    for keyword in call_node.keywords:
        if keyword.arg is None:
            continue

        value = keyword.value
        if isinstance(value, ast.Constant):
            kwargs[keyword.arg] = value.value
        elif isinstance(value, ast.Name):
            kwargs[keyword.arg] = value.id
        elif isinstance(value, ast.Attribute):
            kwargs[keyword.arg] = f"{_get_attr_chain(value)}"

    return kwargs


def _get_attr_chain(node: ast.Attribute) -> str:
    """Get the full attribute chain (e.g., 'ScreeningStatus.IN_PROGRESS')."""
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _extract_table_name(node: ast.ClassDef) -> str | None:
    """Extract table name from __tablename__ or class config."""
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "__tablename__":
                    if isinstance(item.value, ast.Constant):
                        return item.value.value
    return None


def _parse_entity_file(file_path: Path) -> Iterator[EntityInfo]:
    """Parse a Python file and yield entity definitions."""
    if not file_path.exists():
        return

    source = file_path.read_text(encoding="utf-8")
    source_lines = source.splitlines()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    module = _get_module_from_path(file_path)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        if not _is_sqlmodel_entity(node, source):
            continue

        base_names = _get_base_names(node)

        # Identify mixins
        mixins = [name for name in base_names if name.endswith("Mixin")]

        # Extract columns
        columns: list[ColumnInfo] = []
        relationships: list[RelationshipInfo] = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                # Try as column first
                col = _extract_field_info(item, source_lines)
                if col:
                    columns.append(col)
                else:
                    # Try as relationship
                    rel = _extract_relationship_info(item)
                    if rel:
                        relationships.append(rel)

        yield EntityInfo(
            name=node.name,
            table_name=_extract_table_name(node),
            module=module,
            file_path=str(file_path),
            docstring=_extract_docstring(node),
            base_classes=base_names,
            columns=columns,
            relationships=relationships,
            mixins=mixins,
        )


class SQLModelParser:
    """Parser for extracting SQLModel entity definitions from the project."""

    def __init__(self) -> None:
        self._cache: dict[str, EntityInfo] = {}
        self._loaded = False

    def _load_all(self) -> None:
        """Load all entities from the project."""
        if self._loaded:
            return

        # Find all model files
        model_dirs = [
            MODULES_DIR,
            SHARED_DIR,
        ]

        for base_dir in model_dirs:
            if not base_dir.exists():
                continue

            for model_file in base_dir.rglob("*.py"):
                # Skip non-model files
                if "__pycache__" in str(model_file):
                    continue
                if model_file.name.startswith("_"):
                    continue
                if "schemas" in str(model_file):
                    continue

                for entity in _parse_entity_file(model_file):
                    self._cache[entity.name] = entity

        self._loaded = True

    def list_entities(self, module: str | None = None) -> list[dict]:
        """
        List all available entities.

        Args:
            module: Optional module to filter by.

        Returns:
            List of entity summaries.
        """
        self._load_all()

        result = []
        for entity in self._cache.values():
            if module and entity.module != module:
                continue

            result.append(
                {
                    "name": entity.name,
                    "module": entity.module,
                    "table_name": entity.table_name,
                    "column_count": len(entity.columns),
                    "relationship_count": len(entity.relationships),
                    "mixins": entity.mixins,
                }
            )

        return sorted(result, key=lambda x: (x["module"], x["name"]))

    def get_entity(self, entity_name: str) -> dict | None:
        """
        Get detailed information about a specific entity.

        Args:
            entity_name: Name of the entity (e.g., "ScreeningProcess").

        Returns:
            Entity definition with all columns and relationships.
        """
        self._load_all()

        entity = self._cache.get(entity_name)
        if entity:
            return entity.to_dict()
        return None

    def find_by_field(self, field_name: str, field_type: str | None = None) -> list[dict]:
        """
        Find entities that contain a specific field.

        Args:
            field_name: Name of the field to search for.
            field_type: Optional type to filter by.

        Returns:
            List of matches with entity and field info.
        """
        self._load_all()

        results = []
        for entity in self._cache.values():
            for col in entity.columns:
                if col.name == field_name or field_name in col.name:
                    if field_type and field_type not in col.type_:
                        continue
                    results.append(
                        {
                            "entity": entity.name,
                            "module": entity.module,
                            "field": col.name,
                            "type": col.type_,
                            "nullable": col.nullable,
                        }
                    )

        return results

    def get_relationships_for(self, entity_name: str) -> list[dict]:
        """
        Get all relationships for an entity.

        Args:
            entity_name: Name of the entity.

        Returns:
            List of relationships (both incoming and outgoing).
        """
        self._load_all()

        entity = self._cache.get(entity_name)
        if not entity:
            return []

        outgoing = [
            {
                "direction": "outgoing",
                "name": r.name,
                "target": r.target,
                "type": r.type_,
            }
            for r in entity.relationships
        ]

        # Find incoming relationships
        incoming = []
        for other_entity in self._cache.values():
            if other_entity.name == entity_name:
                continue
            for rel in other_entity.relationships:
                if rel.target == entity_name:
                    incoming.append(
                        {
                            "direction": "incoming",
                            "name": rel.name,
                            "source": other_entity.name,
                            "type": rel.type_,
                        }
                    )

        return outgoing + incoming

    def generate_er_diagram(self, module: str, format_: str = "mermaid") -> str:
        """
        Generate an ER diagram for a module.

        Args:
            module: The module to generate diagram for.
            format_: Output format (mermaid, dbml).

        Returns:
            Diagram in the specified format.
        """
        self._load_all()

        entities = [e for e in self._cache.values() if e.module == module]

        if format_ == "mermaid":
            return self._generate_mermaid(entities)
        elif format_ == "dbml":
            return self._generate_dbml(entities)
        else:
            return self._generate_mermaid(entities)

    def _generate_mermaid(self, entities: list[EntityInfo]) -> str:
        """Generate Mermaid ER diagram."""
        lines = ["erDiagram"]

        for entity in entities:
            # Entity definition
            lines.append(f"    {entity.name} {{")
            for col in entity.columns[:10]:  # Limit columns for readability
                pk = "PK" if col.primary_key else ""
                fk = "FK" if col.foreign_key else ""
                key_marker = f" {pk}{fk}" if pk or fk else ""
                lines.append(f"        {col.type_.split('[')[0]} {col.name}{key_marker}")
            if len(entity.columns) > 10:
                lines.append(f"        ... {len(entity.columns) - 10} more columns")
            lines.append("    }")

        # Relationships
        for entity in entities:
            for rel in entity.relationships:
                if rel.type_ == "one-to-many":
                    lines.append(f"    {entity.name} ||--o{{ {rel.target} : {rel.name}")
                elif rel.type_ == "many-to-one":
                    lines.append(f"    {entity.name} }}o--|| {rel.target} : {rel.name}")
                elif rel.type_ == "one-to-one":
                    lines.append(f"    {entity.name} ||--|| {rel.target} : {rel.name}")

        return "\n".join(lines)

    def _generate_dbml(self, entities: list[EntityInfo]) -> str:
        """Generate DBML diagram."""
        lines = []

        for entity in entities:
            table_name = entity.table_name or entity.name.lower()
            lines.append(f"Table {table_name} {{")
            for col in entity.columns:
                pk = "[pk]" if col.primary_key else ""
                nullable = "null" if col.nullable else "not null"
                lines.append(f"  {col.name} {col.type_} [{nullable}] {pk}")
            lines.append("}")
            lines.append("")

        return "\n".join(lines)


# Singleton instance
_parser: SQLModelParser | None = None


def get_sqlmodel_parser() -> SQLModelParser:
    """Get the singleton SQLModel parser instance."""
    global _parser
    if _parser is None:
        _parser = SQLModelParser()
    return _parser
