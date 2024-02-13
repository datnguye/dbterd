from typing import Tuple

from dbterd.adapters.algos import test_relationship
from dbterd.types import Catalog, Manifest


def run(manifest: Manifest, catalog: Catalog, **kwargs) -> Tuple[str, str]:
    """Parse dbt artifacts and export D2 file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the D2 content
    """
    return ("output.d2", parse(manifest, catalog, **kwargs))


def parse(manifest: Manifest, catalog: Catalog, **kwargs) -> str:
    """Get the D2 content from dbt artifacts

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        str: D2 content
    """
    tables, relationships = test_relationship.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    # Build D2 content
    # https://play.d2lang.com/?script=qlDQtVOo5AIEAAD__w%3D%3D&, https://github.com/terrastruct/d2
    d2 = ""
    for table in tables:
        d2 += '"{table}": {{\n  shape: sql_table\n{columns}\n}}\n'.format(
            table=table.name,
            columns="\n".join([f"  {x.name}: {x.data_type}" for x in table.columns]),
        )

    for rel in relationships:
        key_from = f'"{rel.table_map[1]}"'
        key_to = f'"{rel.table_map[0]}"'
        connector = f"{rel.column_map[1]} = {rel.column_map[0]}"
        d2 += f'{key_from} {get_rel_symbol(rel.type)} {key_to}: "{connector}"\n'

    return d2


def get_rel_symbol(relationship_type: str) -> str:
    """Get D2 relationship symbol

    Args:
        relationship_type (str): relationship type

    Returns:
        str: Relation symbol supported in D2
    """
    return "->"  # no supports for rel type
