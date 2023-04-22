import copy
from dbterd.adapters.algos.meta import Column, Table


def get_tables(manifest, catalog):
    """Extract tables from dbt artifacts"""
    tables = []

    if hasattr(manifest, "nodes"):
        for table_name, node in manifest.nodes.items():
            if (
                table_name.startswith("model.")
                or table_name.startswith("seed.")
                or table_name.startswith("snapshot.")
            ):
                catalog_node = catalog.nodes.get(table_name)
                table = get_table(table_name, node, catalog_node)
                tables.append(table)

    if hasattr(manifest, "sources"):
        for table_name, source in manifest.sources.items():
            if table_name.startswith("source"):
                catalog_source = catalog.sources.get(table_name)
                table = get_table(table_name, source, catalog_source)
                tables.append(table)

    return tables


def enrich_tables_from_relationships(tables, relationships):
    copied_tables = copy.deepcopy(tables)
    for relationship in relationships:
        for table in copied_tables:
            table_columns = [x.name.lower() for x in table.columns]
            if (
                table.name == relationship.table_map[0]
                and relationship.column_map[0].lower() not in table_columns
            ):
                table.columns.append(Column(name=relationship.column_map[0]))
            if (
                table.name == relationship.table_map[1]
                and relationship.column_map[1].lower() not in table_columns
            ):
                table.columns.append(Column(name=relationship.column_map[1]))
    return copied_tables


def get_table(table_name, resource, catalog_resource=None):
    table = Table(
        name=table_name,
        raw_sql=get_compiled_sql(resource),
        database=resource.database.lower(),
        schema=resource.schema_.lower(),
        columns=[],
        resource_type=table_name.split(".")[0],
    )

    if catalog_resource:
        for column, metadata in catalog_resource.columns.items():
            table.columns.append(
                Column(
                    name=str(column).lower(),
                    data_type=str(metadata.type).lower(),
                )
            )

    for column_name, column_metadata in resource.columns.items():
        column_name = column_name.strip('"')
        if not any(c.name.lower() == column_name.lower() for c in table.columns):
            table.columns.append(
                Column(
                    name=column_name.lower(),
                    data_type=str(column_metadata.data_type or "unknown").lower(),
                )
            )

    if not table.columns:
        table.columns.append(Column())

    return table


def get_compiled_sql(manifest_node):
    if hasattr(manifest_node, "compiled_sql"):  # up to v6
        return manifest_node.compiled_sql

    if hasattr(manifest_node, "compiled_code"):  # from v7
        return manifest_node.compiled_code

    if hasattr(
        manifest_node, "columns"
    ):  # nodes having no compiled but just list of columns
        return """select
            {columns}
        from {table}""".format(
            columns=",\n".join([f"{x}" for x in manifest_node.columns]),
            table=f"{manifest_node.database}.{manifest_node.schema}.undefined",
        )

    return manifest_node.raw_sql  # fallback to raw dbt code
