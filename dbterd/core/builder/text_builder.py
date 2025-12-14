"""Text-based ERD Builder.

This module provides a builder for text-based ERD formats like DBML, Mermaid, PlantUML, Graphviz, D2.
"""

from dbterd.core.builder.base_builder import BaseERDBuilder


class TextERDBuilder(BaseERDBuilder):
    """Builder for text-based ERD formats (DBML, Mermaid, PlantUML, Graphviz, D2).

    Provides a chainable API for building ERD output from tables and relationships.
    Each method returns self to enable method chaining.

    Example:
        builder = TextERDBuilder()
        content = (
            builder
            .add_header("erDiagram")
            .add_tables(tables, format_table)
            .add_relationships(relationships, format_rel)
            .build()
        )

    """

    def build(self, separator: str = "\n") -> str:
        """Build the final ERD content string.

        Args:
            separator: String to join sections with (default: newline)

        Returns:
            Complete ERD content string with trailing newline

        """
        return separator.join(str(item) for item in self._content) + "\n"
