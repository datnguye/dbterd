"""PlantUML target adapter for dbterd.

This module converts parsed dbt artifacts into PlantUML IE diagram format
for visualization with PlantUML tools.
"""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("plantuml", description="PlantUML IE diagram format")
class PlantumlAdapter(BaseTargetAdapter):
    """PlantUML format target adapter.

    Generates PlantUML IE diagram syntax for rendering with PlantUML tools.
    https://plantuml.com/ie-diagram, https://www.plantuml.com/plantuml/uml
    """

    file_extension = ".plantuml"
    default_filename = "output.plantuml"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "}o--||",
        "11": "||--||",
        "0n": "}o--|{",
        "1n": "||--|{",
        "nn": "}|--|{",
    }
    DEFAULT_SYMBOL = "}|--||"  # n1

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build PlantUML IE diagram content."""
        builder = TextERDBuilder()
        builder.add_header("@startuml")
        builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))

        # Track added relationships to avoid duplicates
        added_relationships: set[str] = set()
        for rel in relationships:
            rel_str = self.format_relationship(rel, **kwargs)
            if rel_str not in added_relationships:
                builder.add_section(rel_str)
                added_relationships.add(rel_str)

        builder.add_footer("@enduml")
        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in PlantUML syntax."""
        columns = "\n".join(f"    {col.name} : {col.data_type}" for col in table.columns)
        return f'entity "{table.name}" {{\n{columns}\n  }}'

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in PlantUML syntax."""
        key_from = f'"{relationship.table_map[1]}"'
        key_to = f'"{relationship.table_map[0]}"'
        symbol = self.get_rel_symbol(relationship.type)
        # NOTE: PlantUML doesn't have columns defined in the connector
        return f"  {key_from} {symbol} {key_to}"
