"""D2 target adapter for dbterd.

This module converts parsed dbt artifacts into D2 diagram format
for visualization with D2 tools.
"""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("d2", description="D2 diagram format")
class D2Adapter(BaseTargetAdapter):
    """D2 format target adapter.

    Generates D2 diagram syntax for rendering with D2 tools.
    https://play.d2lang.com/, https://github.com/terrastruct/d2
    """

    file_extension = ".d2"
    default_filename = "output.d2"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {}
    DEFAULT_SYMBOL = "->"  # D2 doesn't support relationship type symbols

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build D2 diagram content."""
        builder = TextERDBuilder()
        builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))
        builder.add_relationships(relationships, lambda r: self.format_relationship(r, **kwargs))

        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in D2 syntax."""
        columns = "\n".join(f"  {col.name}: {col.data_type}" for col in table.columns)
        return f'"{table.name}": {{\n  shape: sql_table\n{columns}\n}}'

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in D2 syntax."""
        key_from = f'"{relationship.table_map[1]}"'
        key_to = f'"{relationship.table_map[0]}"'
        connector = f"{relationship.column_map[1]} = {relationship.column_map[0]}"
        symbol = self.get_rel_symbol(relationship.type)
        return f'{key_from} {symbol} {key_to}: "{connector}"'
