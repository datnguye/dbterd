from dbterd.adapters.algos import test_relationship


def run(manifest, catalog, **kwargs):
    """Parse dbt artifacts and export DBML file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the DBML content
    """
    return ("output.dbml", parse(manifest, catalog, **kwargs))


def parse(manifest, catalog, **kwargs):
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
        dbml += """Table \"{table}\" {{\n{columns}\n}}\n""".format(
            table=table.name,
            columns="\n".join([f'  "{x.name}" "{x.data_type}"' for x in table.columns]),
        )

    dbml += "//Refs (based on the DBT Relationship Tests)\n"
    for rel in relationships:
        key_from = f'"{rel.table_map[1]}"."{rel.column_map[1]}"'
        key_to = f'"{rel.table_map[0]}"."{rel.column_map[0]}"'
        dbml += f"Ref: {key_from} > {key_to}\n"
    return dbml
