"""DBML target adapter for dbterd.

This module converts parsed dbt artifacts into DBML (Database Markup Language)
format for ERD visualization.
"""

import json
from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Column, Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("dbml", description="Database Markup Language format")
class DbmlAdapter(BaseTargetAdapter):
    """DBML format target adapter.

    Generates DBML output compatible with dbdiagram.io and other
    DBML-supporting tools.
    """

    file_extension = ".dbml"
    default_filename = "output.dbml"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "11": "-",
        "01": "-",
        "1n": "<",
        "0n": "<",
        "nn": "<>",
    }
    DEFAULT_SYMBOL = ">"  # n1

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build DBML content from tables and relationships."""
        quote = "" if kwargs.get("omit_entity_name_quotes") else '"'
        builder = TextERDBuilder()

        builder.add_section("//Tables (based on the selection criteria)")
        builder.add_tables(tables, lambda t: self.format_table(t, quote=quote))
        builder.add_section("//Refs (based on the DBT Relationship Tests)")
        builder.add_relationships(relationships, lambda r: self.format_relationship(r, quote=quote))

        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in DBML syntax."""
        quote = kwargs.get("quote", '"')
        columns = self._format_columns(table.columns)
        pk_columns = [col.name for col in table.columns if col.is_primary_key]
        indexes_block = self._format_indexes_block(pk_columns) if pk_columns else ""

        return (
            f"//--configured at schema: {table.database}.{table.schema}\n"
            f"Table {quote}{table.name}{quote} {{\n"
            f"{columns}\n\n"
            f"  Note: {json.dumps(table.description)}\n"
            f"{indexes_block}"
            f"}}"
        )

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in DBML syntax."""
        quote = kwargs.get("quote", '"')
        key_from = self._format_column_ref(relationship.table_map[1], relationship.column_map[1], quote)
        key_to = self._format_column_ref(relationship.table_map[0], relationship.column_map[0], quote)
        symbol = self.get_rel_symbol(relationship.type)
        return f"Ref: {key_from} {symbol} {key_to}"

    def _format_columns(self, columns: list[Column]) -> str:
        """Format columns for a table."""
        return "\n".join(
            str.format(
                '  "{0}" "{1}"{2}',
                col.name,
                col.data_type,
                (str.format(" [note: {0}]", json.dumps(col.description)) if col.description else ""),
            )
            for col in columns
        )

    def _format_column_ref(self, table: str, columns: list[str], quote: str) -> str:
        """Format a table.column(s) reference in DBML syntax.

        For a single column: `"table"."col"`
        For multiple columns: `"table".("col1", "col2")`
        """
        if len(columns) == 1:
            return f'{quote}{table}{quote}."{columns[0]}"'
        cols_str = ", ".join(f'"{c}"' for c in columns)
        return f"{quote}{table}{quote}.({cols_str})"

    def _format_indexes_block(self, pk_columns: list[str]) -> str:
        """Format a DBML indexes block for a composite or single primary key."""
        cols_str = ", ".join(pk_columns)
        return f"  indexes {{\n    ({cols_str}) [pk]\n  }}\n"
