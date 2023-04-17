from dbterd.adapters.algos.base import get_tables
from dbterd.adapters.algos.meta import Column, Ref


def parse(manifest, catalog, **kwargs):
    # Parse Table
    tables = get_tables(manifest, catalog)
    # Apply selection
    select_rule = (kwargs.get("select") or "").lower().split(":")
    resource_types = kwargs.get("resource_type") or ""

    def filter_table_select(table):
        if select_rule[0].startswith("schema"):
            schema = f"{table.database}.{table.schema}"
            return schema.startswith(select_rule[-1]) or table.schema.startswith(
                select_rule[-1]
            )
        else:
            return table.name.startswith(select_rule[-1])

    tables = [table for table in tables if filter_table_select(table)]
    tables = [table for table in tables if table.resource_type in resource_types]

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

    return (tables, relationships)


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
