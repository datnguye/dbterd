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

        return (
            f"//--configured at schema: {table.database}.{table.schema}\n"
            f"Table {quote}{table.name}{quote} {{\n"
            f"{columns}\n\n"
            f"  Note: {json.dumps(table.description)}\n"
            f"}}"
        )

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in DBML syntax."""
        quote = kwargs.get("quote", '"')
        key_from = f'{quote}{relationship.table_map[1]}{quote}."{relationship.column_map[1]}"'
        key_to = f'{quote}{relationship.table_map[0]}{quote}."{relationship.column_map[0]}"'
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
