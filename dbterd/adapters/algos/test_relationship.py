from dbterd.adapters.algos import base
from dbterd.adapters.algos.filter import is_selected_table
from dbterd.adapters.algos.meta import Ref
from dbterd.constants import (
    DEFAULT_ALGO_RULE,
    TEST_META_IGNORE_IN_ERD,
    TEST_META_RELATIONSHIP_TYPE,
)


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
    relationships = get_relationships(manifest=manifest, **kwargs)
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


def get_relationships(manifest, **kwargs):
    """Extract relationships from dbt artifacts based on test relationship

    Args:
        manifest (dict): Manifest json
        kwargs.algo (str): |
            Algorithm name and optional rules.
            Smaples:
            - test_relationship
            - test_relationship:(name:relationship|c_from:column_name|c_to:field)
            - test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)

    Returns:
        List[Ref]: List of parsed relationship
    """
    algo_parts = (kwargs.get("algo") or "").replace(" ", "").split(":", 1)
    rules, _ = (
        algo_parts[1] if len(algo_parts) > 1 else DEFAULT_ALGO_RULE,
        algo_parts[0],
    )
    rules = rules[1:-1]  # remove brackets
    rules = dict(arg.split(":") for arg in rules.split("|"))

    refs = [
        Ref(
            name=x,
            table_map=manifest.parent_map[x],
            column_map=[
                str(
                    manifest.nodes[x].test_metadata.kwargs.get(rules.get("c_to"))
                    or "_and_".join(
                        manifest.nodes[x].test_metadata.kwargs.get(
                            f'{rules.get("c_to")}s', "unknown"
                        )
                    )
                ).lower(),
                str(
                    manifest.nodes[x].test_metadata.kwargs.get("column_name")
                    or manifest.nodes[x].test_metadata.kwargs.get(rules.get("c_from"))
                    or "_and_".join(
                        manifest.nodes[x].test_metadata.kwargs.get(
                            f'{rules.get("c_from")}s', "unknown"
                        )
                    )
                ).lower(),
            ],
            type=get_relationship_type(
                manifest.nodes[x].meta.get(TEST_META_RELATIONSHIP_TYPE, "")
            ),
        )
        for x in manifest.nodes
        if (
            x.startswith("test")
            and rules.get("name").lower() in x.lower()
            and manifest.nodes[x].meta.get(TEST_META_IGNORE_IN_ERD, "0") == "0"
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


def get_relationship_type(meta: str) -> str:
    """Get short form of the relationship type configured in test meta

    Args:
        meta (str): meta value

    Returns:
        str: |
            Short relationship type. Accepted values: '0n','01','11','nn','n1' and '1n'.
            And `1n` is default/fallback value
    """
    if meta.lower() == "zero-to-many":
        return "0n"
    if meta.lower() == "zero-to-one":
        return "01"
    if meta.lower() == "one-to-one":
        return "11"
    if meta.lower() == "many-to-many":
        return "nn"
    if meta.lower() == "one-to-many":
        return "1n"
    return "n1"  # "many-to-one"
