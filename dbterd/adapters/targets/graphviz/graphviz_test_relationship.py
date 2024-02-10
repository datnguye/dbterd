from typing import Tuple

from dbterd.adapters.algos import test_relationship
from dbterd.types import Catalog, Manifest


def run(manifest: Manifest, catalog: Catalog, **kwargs) -> Tuple[str, str]:
    """Parse dbt artifacts and export GraphViz file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the GraphViz content
    """
    return ("output.graphviz", parse(manifest, catalog, **kwargs))


def parse(manifest: Manifest, catalog: Catalog, **kwargs) -> str:
    """Get the GraphViz content from dbt artifacts

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        str: GraphViz content
    """
    tables, relationships = test_relationship.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    # Build GraphViz content
    # https://dreampuf.github.io/GraphvizOnline/, https://graphviz.org/
    graphviz = (
        "digraph g {\n"
        '  fontname="Helvetica,Arial,sans-serif"\n'
        '  node [fontname="Helvetica,Arial,sans-serif"]\n'
        '  edge [fontname="Helvetica,Arial,sans-serif"]\n'
        '  graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];\n'
        "  ratio=auto;\n"
    )
    for table in tables:
        graphviz += (
            '  "{table}" [\n'
            '    style = "filled, bold"\n'
            "    penwidth = 1\n"
            '    fillcolor = "white"\n'
            '    fontname = "Courier New"\n'
            '    shape = "Mrecord"\n'
            "    label =<\n"
            '      <table border="0" cellborder="0" cellpadding="3" bgcolor="white">\n'
            '         <tr><td bgcolor="black" align="center" colspan="2">'
            '<font color="white">{table}</font></td></tr>\n{columns}\n'
            "      </table>> ];\n"
        ).format(
            table=table.name,
            columns="\n".join(
                [
                    f'         <tr><td align="left">({x.data_type}) {x.name}</td></tr>'
                    for x in table.columns
                ]
            ),
        )

    for rel in relationships:
        key_from = f'"{rel.table_map[1]}"'
        key_to = f'"{rel.table_map[0]}"'
        connector = f"{rel.column_map[1]} = {rel.column_map[0]}"
        graphviz += (
            f"  {key_from} {get_rel_symbol(rel.type)} {key_to} [ \n"
            "    penwidth = 1\n"
            "    fontsize = 12\n"
            '    fontcolor = "black"\n'
            f'    label = "{connector}"\n'
            "  ];\n"
        )

    graphviz += "}"

    return graphviz


def get_rel_symbol(relationship_type: str) -> str:
    """Get GraphViz relationship symbol

    Args:
        relationship_type (str): relationship type

    Returns:
        str: Relation symbol supported in GraphViz
    """
    return "->"  # no supports for rel type
