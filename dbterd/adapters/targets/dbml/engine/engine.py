from sql_metadata import Parser

from dbterd.adapters.targets.dbml.engine.meta import Column, Ref, Table


def parse(manifest, **kwargs):
    # Parse Table
    tables = get_tables(manifest)
    # -- apply selection
    select_rule = (kwargs.get("select") or "").lower().split(":")
    if select_rule[0].startswith("schema"):
        select_rule = select_rule[-1]
        tables = [
            x
            for x in tables
            if x.schema.startswith(select_rule)  # --select schema:analytics
            or f"{x.database}.{x.schema}".startswith(
                select_rule
            )  # --select schema:db.analytics
        ]
    else:
        select_rule = select_rule[-1]  # only take care of name
        tables = [x for x in tables if x.name.startswith(select_rule)]

    # -- apply exclusion (take care of name only)
    tables = [
        x
        for x in tables
        if kwargs.get("exclude") is None or not x.name.startswith(kwargs.get("exclude"))
    ]

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
            table_columns = [x.name for x in table.columns]
            if (
                table.name == relationship.table_map[0]
                and relationship.column_map[0] not in table_columns
            ):
                table.columns.append(Column(name=relationship.column_map[0]))
            if (
                table.name == relationship.table_map[1]
                and relationship.column_map[1] not in table_columns
            ):
                table.columns.append(Column(name=relationship.column_map[1]))

    # Build DBML content
    dbml = "//Tables (based on the selection criteria)\n"
    for table in tables:
        dbml += f"//--configured at schema: {table.database}.{table.schema}\n"
        dbml += """Table \"{table}\"{{\n{columns}\n}}\n""".format(
            table=table.name,
            columns="\n".join([f'    "{x.name}" {x.data_type}' for x in table.columns]),
        )

    dbml += "//Refs (based on the DBT Relationship Tests)\n"
    for rel in relationships:
        key_from = f'"{rel.table_map[1]}"."{rel.column_map[1]}"'
        key_to = f'"{rel.table_map[0]}"."{rel.column_map[0]}"'
        dbml += f"Ref: {key_from} > {key_to}\n"

    return dbml


def get_tables(manifest):
    tables = [
        Table(
            name=x,
            raw_sql=get_compiled_sql(manifest.nodes[x]),
            database=manifest.nodes[x].database.lower(),
            schema=manifest.nodes[x].schema_.lower(),
            columns=[],
        )
        for x in manifest.nodes
        if x.startswith("model")
    ]
    for table in tables:
        parser = Parser(table.raw_sql)
        try:
            column_names = parser.columns_aliases_names
        except AttributeError:
            # Object has no associated column names, continue to next object
            pass

        if column_names:
            for column in column_names:
                table.columns.append(
                    Column(
                        name=column,
                    )
                )
        else:
            table.columns.append(
                Column(
                    name="(*)",
                )
            )

    return tables


def get_relationships(manifest):
    refs = [
        Ref(
            name=x,
            table_map=manifest.parent_map[x],
            column_map=[
                manifest.nodes[x].test_metadata.kwargs.get("field", "unknown"),
                manifest.nodes[x].test_metadata.kwargs.get("column_name", "unknown"),
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
            columns="\n".join(
                [
                    f"{x} as {manifest_node.columns[x].data_type or 'varchar'},"
                    for x in manifest_node.columns
                ]
            ),
            table=f"{manifest_node.database}.{manifest_node.schema}.undefined",
        )

    return manifest_node.raw_sql  # fallback to raw dbt code
