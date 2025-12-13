"""Mermaid target adapter for dbterd.

This module converts parsed dbt artifacts into Mermaid ER diagram format
for visualization in Markdown files and documentation tools.
"""

import re
from typing import ClassVar, Optional

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("mermaid", description="Mermaid ER diagram format")
class MermaidAdapter(BaseTargetAdapter):
    """Mermaid format target adapter.

    Generates Mermaid ER diagram syntax for rendering in Markdown
    and documentation tools.
    https://mermaid.js.org/syntax/entityRelationshipDiagram.html
    """

    file_extension = ".md"
    default_filename = "output.md"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "}o--||",
        "11": "||--||",
        "0n": "}o--|{",
        "1n": "||--|{",
        "nn": "}|--|{",
    }
    DEFAULT_SYMBOL = "}|--||"  # n1

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build Mermaid ER diagram content."""
        builder = TextERDBuilder()
        builder.add_header("erDiagram")
        builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))
        builder.add_relationships(relationships, lambda r: self.format_relationship(r, **kwargs))

        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in Mermaid syntax."""
        table_name = table.name.upper()
        table_label = f'["{table.label.upper()}"]' if hasattr(table, "label") and table.label else ""

        if kwargs.get("omit_columns", False):
            return f'  "{table_name}"{table_label} {{\n  }}'

        columns = "\n".join(
            f"    {self.replace_column_type(col.data_type)} {self.replace_column_name(col.name)}"
            for col in table.columns
        )
        return f'  "{table_name}"{table_label} {{\n{columns}\n  }}'

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in Mermaid syntax."""
        key_from = f'"{relationship.table_map[1]}"'
        key_to = f'"{relationship.table_map[0]}"'

        reference_text = self.replace_column_name(relationship.column_map[0])
        if relationship.column_map[0] != relationship.column_map[1]:
            reference_text += f"--{self.replace_column_name(relationship.column_map[1])}"

        if hasattr(relationship, "relationship_label") and relationship.relationship_label:
            reference_text = self.replace_column_name(relationship.relationship_label)

        symbol = self.get_rel_symbol(relationship.type)
        return f"  {key_from.upper()} {symbol} {key_to.upper()}: {reference_text}"

    def replace_column_name(self, column_name: str) -> str:
        """Replace column names containing special characters.

        Prevents Mermaid from failing to render column names with special characters.

        Args:
            column_name: Column name to sanitize

        Returns:
            Column name with special characters substituted

        """
        return column_name.replace(" ", "-").replace(".", "__")

    def match_complex_column_type(self, column_type: str) -> Optional[str]:
        """Return the root type from nested complex types.

        For example, if the input is `Struct<field1 string, field2 string>`,
        returns `Struct`.

        Args:
            column_type: Column type to check

        Returns:
            Root type if input is nested complex type, None for primitive types

        """
        pattern = r"(\w+)<.*>"
        match = re.match(pattern, column_type)
        if match:
            return match.group(1)
        return None

    def replace_column_type(self, column_type: str) -> str:
        """Replace column types containing special characters.

        If type contains a nested complex type, omit it for readability.
        Some DWHs may have types like `Struct<first_name string, last_name string>`
        that cannot be drawn in Mermaid.

        Args:
            column_type: Column type to sanitize

        Returns:
            Type with special characters substituted or omitted

        """
        complex_column_type = self.match_complex_column_type(column_type)
        if complex_column_type:
            return f"{complex_column_type}[OMITTED]"
        return column_type.replace(" ", "-")
