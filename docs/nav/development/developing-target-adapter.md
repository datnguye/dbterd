# Developing a Target Adapter

So you want to add a shiny new output format to `dbterd`? Maybe you've discovered some fancy diagram tool that speaks its own language, or perhaps your team has a secret internal format that makes everyone's eyes sparkle. Either way, you're in the right place!

## What is a Target Adapter?

A target adapter transforms parsed dbt artifacts (tables and relationships) into a specific ERD output format. Think of it as a translator: it takes the universal language of tables and refs, and converts them into Mermaid, DBML, GraphViz, or whatever format your heart desires.

The existing adapters live in `dbterd/adapters/targets/` and include:

- **DBML** - Database Markup Language for dbdiagram.io
- **Mermaid** - For embedding in Markdown docs
- **PlantUML** - The classic UML diagramming tool
- **GraphViz** - DOT language for graph visualization
- **D2** - Modern declarative diagramming
- **DrawDB** - JSON format for DrawDB tool

## Quick Start

Here's the minimal skeleton to get you started:

```python
"""My awesome target adapter for dbterd."""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("myformat", description="My Awesome Format for cool diagrams")
class MyFormatAdapter(BaseTargetAdapter):
    """My format target adapter."""

    file_extension = ".myext"
    default_filename = "output.myext"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "?--",
        "11": "---",
        "0n": "?--<",
        "1n": "---<",
        "nn": ">--<",
    }
    DEFAULT_SYMBOL = ">--"  # n1 (many-to-one)

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build the ERD content."""
        # Your magic goes here
        pass

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table."""
        pass

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship."""
        pass
```

## The Base Class

Your adapter must inherit from `BaseTargetAdapter` which provides:

| Attribute/Method | Type | Description |
|------------------|------|-------------|
| `file_extension` | `str` | Output file extension (e.g., `.dbml`) |
| `default_filename` | `str` | Default output filename |
| `RELATIONSHIP_SYMBOLS` | `dict[str, str]` | Maps relationship types to format-specific symbols |
| `DEFAULT_SYMBOL` | `str` | Fallback symbol when type not found |
| `run()` | method | Entry point called by executor (don't override) |
| `build_erd()` | abstract | **You implement this** - builds full ERD content |
| `format_table()` | abstract | **You implement this** - formats one table |
| `format_relationship()` | abstract | **You implement this** - formats one relationship |
| `get_rel_symbol()` | method | Helper to look up relationship symbols |

## Step-by-Step Guide

### 1. Create Your Adapter File

Create a new file in `dbterd/adapters/targets/`:

```bash
touch dbterd/adapters/targets/myformat.py
```

### 2. Implement the Required Methods

**`build_erd()`** - This is your main orchestrator. It receives all tables and relationships and returns the complete ERD string.

```python
def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
    """Build the complete ERD content."""
    lines = ["# My ERD Format"]

    # Add tables
    for table in tables:
        lines.append(self.format_table(table, **kwargs))

    # Add relationships
    for rel in relationships:
        lines.append(self.format_relationship(rel, **kwargs))

    return "\n".join(lines)
```

**`format_table()`** - Formats a single table. You get a `Table` object with all the juicy details.

```python
def format_table(self, table: Table, **kwargs) -> str:
    """Format a single table in my format."""
    # Check if columns should be omitted
    if kwargs.get("omit_columns", False):
        return f"TABLE {table.name}"

    columns = ", ".join(f"{col.name}: {col.data_type}" for col in table.columns)
    return f"TABLE {table.name} ({columns})"
```

**`format_relationship()`** - Formats a single relationship between tables.

```python
def format_relationship(self, relationship: Ref, **kwargs) -> str:
    """Format a single relationship."""
    symbol = self.get_rel_symbol(relationship.type)
    return f"{relationship.table_map[1]} {symbol} {relationship.table_map[0]}"
```

### 3. Define Relationship Symbols

The relationship type codes and their meanings:

| Code | Meaning | Example |
|------|---------|---------|
| `01` | Zero-to-one | Optional FK |
| `11` | One-to-one | Strict 1:1 |
| `0n` | Zero-to-many | Optional collection |
| `1n` | One-to-many | Required collection |
| `nn` | Many-to-many | Junction table |
| `n1` | Many-to-one | Default FK (uses `DEFAULT_SYMBOL`) |

Map these to your format's notation:

```python
RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
    "01": "}o--||",   # Mermaid's zero-or-one to exactly-one
    "11": "||--||",   # Mermaid's exactly-one to exactly-one
    "0n": "}o--|{",   # Mermaid's zero-or-one to one-or-more
    "1n": "||--|{",   # Mermaid's exactly-one to one-or-more
    "nn": "}|--|{",   # Mermaid's one-or-more to one-or-more
}
DEFAULT_SYMBOL = "}|--||"  # n1: many-to-one
```

## Understanding the Data Models

### Table Model

```python
@dataclass
class Table:
    name: str                    # Formatted table name (based on entity_name_format)
    database: str                # Database name
    schema: str                  # Schema name
    columns: list[Column]        # List of columns
    raw_sql: str | None          # Compiled SQL (if available)
    resource_type: str           # "model", "source", "seed", "snapshot"
    exposures: list[str]         # Associated exposure names
    node_name: str | None        # Full dbt node ID (e.g., "model.jaffle_shop.orders")
    description: str             # Model description from dbt
    label: str | None            # Custom label from meta
```

### Column Model

```python
@dataclass
class Column:
    name: str = "unknown"        # Column name
    data_type: str = "unknown"   # Data type (e.g., "varchar", "integer")
    description: str = ""        # Column description
```

### Ref (Relationship) Model

```python
@dataclass
class Ref:
    name: str                    # Unique identifier (test name or semantic model)
    table_map: tuple[str, str]   # (to_table, from_table) - direction matters!
    column_map: tuple[str, str]  # (to_column, from_column)
    type: str = "n1"             # Relationship type code
    relationship_label: str | None  # Custom label override
```

!!! warning "Table Map Order"
    The `table_map` tuple is `(to_table, from_table)` - the "to" table comes first! This represents the direction of the foreign key: `from_table.column -> to_table.column`.

## Helper: TextERDBuilder

For text-based formats, use the `TextERDBuilder` helper to keep your code clean:

```python
from dbterd.core.builder.text_builder import TextERDBuilder

def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
    builder = TextERDBuilder()

    builder.add_header("erDiagram")  # Optional header line
    builder.add_section("// Tables")  # Optional section comment
    builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))
    builder.add_section("// Relationships")
    builder.add_relationships(relationships, lambda r: self.format_relationship(r, **kwargs))

    return builder.build()
```

## Complete Example

Here's a complete adapter that generates a simple custom format:

```python
"""Simple ERD target adapter for dbterd.

Generates a human-readable text format for quick ERD visualization.
"""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("simple", description="Simple human-readable ERD format")
class SimpleAdapter(BaseTargetAdapter):
    """Simple text format target adapter.

    Generates easy-to-read ERD output for documentation and quick reviews.
    """

    file_extension = ".txt"
    default_filename = "erd.txt"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "?-->",
        "11": "--->",
        "0n": "?-->>",
        "1n": "--->>",
        "nn": "<<-->>",
    }
    DEFAULT_SYMBOL = "<<--"  # n1

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build simple ERD content."""
        builder = TextERDBuilder()

        builder.add_header("=== Entity Relationship Diagram ===")
        builder.add_section("\n--- Tables ---")
        builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))
        builder.add_section("\n--- Relationships ---")
        builder.add_relationships(relationships, lambda r: self.format_relationship(r, **kwargs))

        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table."""
        lines = [f"\n[{table.name}]"]

        if table.description:
            lines.append(f"  Description: {table.description}")

        if not kwargs.get("omit_columns", False):
            lines.append("  Columns:")
            for col in table.columns:
                col_line = f"    - {col.name} ({col.data_type})"
                if col.description:
                    col_line += f" -- {col.description}"
                lines.append(col_line)

        return "\n".join(lines)

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship."""
        from_table = relationship.table_map[1]
        to_table = relationship.table_map[0]
        from_col = relationship.column_map[1]
        to_col = relationship.column_map[0]
        symbol = self.get_rel_symbol(relationship.type)

        label = relationship.relationship_label or f"{from_col} -> {to_col}"
        return f"  {from_table} {symbol} {to_table} : {label}"
```

## Testing Your Adapter

Create tests in `tests/unit/adapters/targets/test_myformat.py`:

```python
"""Tests for MyFormat target adapter."""

import pytest

from dbterd.adapters.targets.myformat import MyFormatAdapter
from dbterd.core.models import Column, Ref, Table


@pytest.fixture
def adapter():
    return MyFormatAdapter()


@pytest.fixture
def sample_table():
    return Table(
        name="users",
        database="mydb",
        schema="public",
        columns=[
            Column(name="id", data_type="integer"),
            Column(name="name", data_type="varchar"),
        ],
        node_name="model.myproject.users",
    )


@pytest.fixture
def sample_relationship():
    return Ref(
        name="test.relationship",
        table_map=("users", "orders"),
        column_map=("id", "user_id"),
        type="1n",
    )


class TestMyFormatAdapter:
    def test_format_table(self, adapter, sample_table):
        result = adapter.format_table(sample_table)
        assert "users" in result
        # Add your assertions

    def test_format_relationship(self, adapter, sample_relationship):
        result = adapter.format_relationship(sample_relationship)
        assert "users" in result
        assert "orders" in result

    def test_build_erd(self, adapter, sample_table, sample_relationship):
        result = adapter.build_erd([sample_table], [sample_relationship])
        # Add your assertions

    def test_get_rel_symbol(self, adapter):
        assert adapter.get_rel_symbol("1n") == adapter.RELATIONSHIP_SYMBOLS["1n"]
        assert adapter.get_rel_symbol("unknown") == adapter.DEFAULT_SYMBOL
```

Run tests:

```bash
poe test tests/unit/adapters/targets/test_myformat.py
```

## Tips and Best Practices

1. **Study existing adapters** - Look at `mermaid.py` and `dbml.py` for inspiration. They handle edge cases you might not think of initially.

2. **Handle special characters** - Column names and types can contain spaces, dots, and other characters that may break your format. Sanitize them!

3. **Support `omit_columns`** - Users can pass `--omit-columns` to generate simpler diagrams. Respect this option in `format_table()`.

4. **Use the label override** - Check for `table.label` and `relationship.relationship_label` to support user customization.

5. **Keep output deterministic** - Tables and relationships are sorted before reaching your adapter, but if you do any additional processing, maintain consistent ordering.

6. **Document your format** - Add a doc page in `docs/nav/guide/targets/` explaining how to use your new format and what tools can render it.

Happy adapter building! 🎨
