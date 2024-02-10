import json
from typing import Tuple

from dbterd.adapters.algos import test_relationship
from dbterd.types import Catalog, Manifest


def run(manifest: Manifest, catalog: Catalog, **kwargs) -> Tuple[str, str]:
    """Parse dbt artifacts and export DBML file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the DBML content
    """
    return ("output.dbml", parse(manifest, catalog, **kwargs))


def parse(manifest: Manifest, catalog: Catalog, **kwargs) -> str:
    """Get the DBML content from dbt artifacts

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        str: DBML content
    """
    tables, relationships = test_relationship.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    # Build DBML content
    dbml = "//Tables (based on the selection criteria)\n"
    for table in tables:
        dbml += f"//--configured at schema: {table.database}.{table.schema}\n"
        dbml += 'Table "{table}" {{\n{columns}\n\n  Note: {table_note}\n}}\n'.format(
            table=table.name,
            columns="\n".join(
                [
                    str.format(
                        '  "{0}" "{1}"{2}',
                        x.name,
                        x.data_type,
                        str.format(" [note: {0}]", json.dumps(x.description))
                        if x.description
                        else "",
                    )
                    for x in table.columns
                ]
            ),
            table_note=json.dumps(table.description),
        )

    dbml += "//Refs (based on the DBT Relationship Tests)\n"
    for rel in relationships:
        key_from = f'"{rel.table_map[1]}"."{rel.column_map[1]}"'
        key_to = f'"{rel.table_map[0]}"."{rel.column_map[0]}"'
        dbml += f"Ref: {key_from} {get_rel_symbol(rel.type)} {key_to}\n"
    return dbml


def get_rel_symbol(relationship_type: str) -> str:
    """Get DBML relationship symbol

    Args:
        relationship_type (str): relationship type

    Returns:
        str: Relation symbol supported in DBML
    """
    if relationship_type in ["01", "11"]:
        return "-"
    if relationship_type in ["0n", "1n"]:
        return "<"
    if relationship_type in ["nn"]:
        return "<>"
    return ">"  # n1
