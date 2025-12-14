"""GraphViz target adapter for dbterd.

This module converts parsed dbt artifacts into GraphViz DOT format
for visualization with GraphViz tools.
"""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("graphviz", description="GraphViz DOT format")
class GraphvizAdapter(BaseTargetAdapter):
    """GraphViz format target adapter.

    Generates GraphViz DOT syntax for rendering with GraphViz tools.
    https://dreampuf.github.io/GraphvizOnline/, https://graphviz.org/
    """

    file_extension = ".graphviz"
    default_filename = "output.graphviz"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {}
    DEFAULT_SYMBOL = "->"  # GraphViz doesn't support relationship type symbols

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build GraphViz DOT content."""
        builder = TextERDBuilder()

        header = (
            "digraph g {\n"
            '  fontname="Helvetica,Arial,sans-serif"\n'
            '  node [fontname="Helvetica,Arial,sans-serif"]\n'
            '  edge [fontname="Helvetica,Arial,sans-serif"]\n'
            '  graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];\n'
            "  ratio=auto;"
        )
        builder.add_header(header)
        builder.add_tables(tables, lambda t: self.format_table(t, **kwargs))
        builder.add_relationships(relationships, lambda r: self.format_relationship(r, **kwargs))
        builder.add_footer("}")

        return builder.build()

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in GraphViz syntax."""
        columns = "\n".join(
            f'         <tr><td align="left">({col.data_type}) {col.name}</td></tr>' for col in table.columns
        )

        return (
            f'  "{table.name}" [\n'
            '    style = "filled, bold"\n'
            "    penwidth = 1\n"
            '    fillcolor = "white"\n'
            '    fontname = "Courier New"\n'
            '    shape = "Mrecord"\n'
            "    label =<\n"
            '      <table border="0" cellborder="0" cellpadding="3" bgcolor="white">\n'
            f'         <tr><td bgcolor="black" align="center" colspan="2">'
            f'<font color="white">{table.name}</font></td></tr>\n'
            f"{columns}\n"
            "      </table>> ];"
        )

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in GraphViz syntax."""
        key_from = f'"{relationship.table_map[1]}"'
        key_to = f'"{relationship.table_map[0]}"'
        connector = f"{relationship.column_map[1]} = {relationship.column_map[0]}"
        symbol = self.get_rel_symbol(relationship.type)

        return (
            f"  {key_from} {symbol} {key_to} [\n"
            "    penwidth = 1\n"
            "    fontsize = 12\n"
            '    fontcolor = "black"\n'
            f'    label = "{connector}"\n'
            "  ];"
        )
