from dbterd.adapters.algos import base
from dbterd.adapters.algos.filter import is_selected_table
from dbterd.adapters.algos.meta import Ref


def parse(manifest, catalog, **kwargs):
    """Get all information (tables, relationships) needed for building diagram

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(List[Table], List[Ref]): Info of parsed tables and relationships
    """
    # Parse Table
    tables = base.get_tables(manifest=manifest, catalog=catalog)

    # Apply selection
    tables = [
        table
        for table in tables
        if is_selected_table(
            table=table,
            select_rules=(kwargs.get("select") or []),
            resource_types=kwargs.get("resource_type", []),
            exclude_rules=kwargs.get("exclude", []),
        )
    ]

    # Parse Ref
    relationships = get_relationships(manifest=manifest)
    table_names = [x.name for x in tables]
    relationships = [
        x
        for x in relationships
        if x.table_map[0] in table_names and x.table_map[1] in table_names
    ]

    # Fullfill columns in Tables (due to `select *`)
    tables = base.enrich_tables_from_relationships(
        tables=tables, relationships=relationships
    )

    return (tables, relationships)


def get_relationships(manifest):
    """Extract relationships from dbt artifacts based on test relationship

    Args:
        manifest (dict): Manifest json

    Returns:
        List[Ref]: List of parsed relationship
    """
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
