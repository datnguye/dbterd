"""JSON-based ERD Builder.

This module provides a builder for JSON-based ERD formats.
"""

import json
from typing import Any, Callable

from dbterd.core.builder.base_builder import BaseERDBuilder
from dbterd.core.models import Ref, Table


class JsonERDBuilder(BaseERDBuilder):
    """Builder for JSON-based ERD formats.

    Provides a chainable API for building JSON ERD output. The output structure
    is fully customizable via the schema parameter passed to build().

    The schema dict defines the output structure:
    - Keys become JSON keys in the output
    - Special placeholders are replaced with collected data:
      - "$header" -> spreads header dict fields at this position
      - "$footer" -> spreads footer dict fields at this position
      - "$tables" -> replaced with tables list
      - "$relationships" -> replaced with relationships list
      - Any other value -> used as-is in the output

    Example:
        builder = JsonERDBuilder()
        content = (
            builder
            .add_header({"author": "dbterd", "version": "1.0"})
            .add_tables(tables, format_table_func)
            .add_relationships(relationships, format_rel_func)
            .build(schema={
                "$header": None,           # Spread header fields at top
                "tables": "$tables",       # Tables array
                "relationships": "$relationships",  # Relationships array
                "notes": [],               # Static value
                "database": "generic",     # Static value
            })
        )

    """

    def __init__(self) -> None:
        """Initialize the JSON builder."""
        super().__init__()
        self._header_dict: dict[str, Any] = {}
        self._tables_list: list[dict] = []
        self._relationships_list: list[dict] = []
        self._footer_dict: dict[str, Any] = {}

    def add_header(self, header: dict[str, Any]) -> "JsonERDBuilder":
        """Add header fields to the JSON output.

        Args:
            header: Dict with header fields to include at top level

        Returns:
            Self for method chaining

        """
        if isinstance(header, dict):
            self._header_dict.update(header)
        return self

    def add_section(self, content: dict) -> "JsonERDBuilder":
        """Add a content section (merged into footer for JSON format).

        Args:
            content: Dict to merge into footer

        Returns:
            Self for method chaining

        """
        if isinstance(content, dict):
            self._footer_dict.update(content)
        return self

    def add_tables(self, tables: list[Table], formatter: Callable[[Table], dict]) -> "JsonERDBuilder":
        """Add formatted table dicts.

        Args:
            tables: List of Table objects to format
            formatter: Function that formats a Table to dict

        Returns:
            Self for method chaining

        """
        for table in tables:
            self._tables_list.append(formatter(table))
        return self

    def add_relationships(self, relationships: list[Ref], formatter: Callable[[Ref], dict]) -> "JsonERDBuilder":
        """Add formatted relationship dicts.

        Args:
            relationships: List of Ref objects to format
            formatter: Function that formats a Ref to dict

        Returns:
            Self for method chaining

        """
        for rel in relationships:
            self._relationships_list.append(formatter(rel))
        return self

    def add_footer(self, footer: dict[str, Any]) -> "JsonERDBuilder":
        """Add footer fields to the JSON output.

        Args:
            footer: Dict with additional fields to append after body

        Returns:
            Self for method chaining

        """
        if isinstance(footer, dict):
            self._footer_dict.update(footer)
        return self

    def build(self, schema: dict[str, Any]) -> str:
        """Build the final ERD content as JSON string.

        Args:
            schema: Dict defining the output structure.
                    Keys become JSON keys; values can be:
                    - "$header": spreads header dict fields
                    - "$footer": spreads footer dict fields
                    - "$tables": replaced with tables list
                    - "$relationships": replaced with relationships list
                    - Any other value: used as-is

        Returns:
            Complete ERD content as JSON string

        """
        result: dict[str, Any] = {}
        for key, value in schema.items():
            if key == "$header":
                result.update(self._header_dict)
            elif key == "$footer":
                result.update(self._footer_dict)
            elif value == "$tables":
                result[key] = self._tables_list
            elif value == "$relationships":
                result[key] = self._relationships_list
            else:
                result[key] = value

        return json.dumps(result) + "\n"

    def clear(self) -> "JsonERDBuilder":
        """Clear all content and reset the builder.

        Returns:
            Self for method chaining

        """
        super().clear()
        self._header_dict.clear()
        self._tables_list.clear()
        self._relationships_list.clear()
        self._footer_dict.clear()
        return self
