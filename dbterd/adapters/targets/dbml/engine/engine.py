from dbterd.adapters.targets.dbml.engine.meta import Column, Ref, Table


def parse(manifest, catalog, **kwargs):
    # Parse Table
    tables = get_tables(manifest, catalog)
    # Apply selection
    select_rule = (kwargs.get("select") or "").lower().split(":")
    resource_type_rule = kwargs.get("resource_type") or ""

    def filter_table_select(table):
        if select_rule[0].startswith("schema"):
            schema = f"{table.database}.{table.schema}"
            return schema.startswith(select_rule[-1]) or table.schema.startswith(
                select_rule[-1]
            )
        else:
            return table.name.startswith(select_rule[-1])

    tables = [table for table in tables if filter_table_select(table)]
    tables = [table for table in tables if table.resource_type in resource_type_rule]

    # -- apply exclusion (take care of name only)

    exclude_rule = kwargs.get("exclude")
    if exclude_rule:
        tables = [table for table in tables if not table.name.startswith(exclude_rule)]

    # Parse Ref
    relationships = get_relationships(manifest)
    table_names = [x.name for x in tables]
    relationships = [
        x
        for x in relationships
        if x.table_map[0] in table_names and x.table_map[1] in table_names
    ]

    # Fullfill columns in Tables (due to `select *`)
    for relationship in relationships:
        for table in tables:
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


def get_tables(manifest, catalog):
    """Extract tables from dbt artifacts"""

    def create_table_and_columns(table_name, resource, catalog_resource=None):
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

    tables = []

    if hasattr(manifest, "nodes"):
        for table_name, node in manifest.nodes.items():
            if (
                table_name.startswith("model.")
                or table_name.startswith("seed.")
                or table_name.startswith("snapshot.")
            ):
                catalog_node = catalog.nodes.get(table_name)
                table = create_table_and_columns(table_name, node, catalog_node)
                tables.append(table)

    if hasattr(manifest, "sources"):
        for table_name, source in manifest.sources.items():
            if table_name.startswith("source"):
                catalog_source = catalog.sources.get(table_name)
                table = create_table_and_columns(table_name, source, catalog_source)
                tables.append(table)

    return tables


def get_relationships(manifest):
    """Extract relationships from dbt artifacts based on test relationship"""
    refs = [
        Ref(
            name=x,
            table_map=manifest.parent_map[x],
            column_map=[
                str(
                    manifest.nodes[x].test_metadata.kwargs.get("field", "unknown")
                ).lower(),
                str(
                    manifest.nodes[x].test_metadata.kwargs.get("column_name", "unknown")
                ).lower(),
            ],
        )
        for x in manifest.nodes
        if (
            x.startswith("test")
            and "relationship" in x.lower()
            and manifest.nodes[x].meta.get("ignore_in_erd", "0") == "0"
        )
    ]

    # remove duplicates
    if refs:
        distinct_list = [refs[0]]
        for ref in refs:
            distinct_maps = [str((x.table_map, x.column_map)) for x in distinct_list]
            if str((ref.table_map, ref.column_map)) not in distinct_maps:
                distinct_list.append(ref)

        return distinct_list

    return []


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
        from {table}
        """.format(
            columns=",\n".join([f"{x}" for x in manifest_node.columns]),
            table=f"{manifest_node.database}.{manifest_node.schema}.undefined",
        )

    return manifest_node.raw_sql  # fallback to raw dbt code
