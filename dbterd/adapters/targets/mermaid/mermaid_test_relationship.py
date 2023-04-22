from dbterd.adapters.algos import test_relationship


def run(manifest, catalog, **kwargs):
    """Parse dbt artifacts and export Mermaid file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the Mermaid content
    """
    return ("output.md", parse(manifest, catalog, **kwargs))


def parse(manifest, catalog, **kwargs):
    """Get the Mermaid content from dbt artifacts

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        str: Mermaid content
    """
    tables, relationships = test_relationship.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    # Build Mermaid content
    # https://mermaid.js.org/syntax/entityRelationshipDiagram.html
    mermaid = "erDiagram\n"
    for table in tables:
        mermaid += """  \"{table}\" {{\n{columns}\n  }}\n""".format(
            table=table.name.upper(),
            columns="\n".join(
                [
                    f'    {x.data_type.replace(" ","-")} {x.name.replace(" ","-")}'
                    for x in table.columns
                ]
            ),
        )

    for rel in relationships:
        key_from = f'"{rel.table_map[0]}"'
        key_to = f'"{rel.table_map[1]}"'
        reference_text = rel.column_map[1].replace(" ", "-")
        if rel.column_map[1] != rel.column_map[0]:
            reference_text += f"--{ rel.column_map[0].replace(' ','-')}"
        mermaid += f"  {key_from.upper()} ||--o{{ {key_to.upper()}: {reference_text}\n"

    return mermaid
