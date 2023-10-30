from dbterd.adapters.algos import base
from dbterd.adapters.filter import is_selected_table
from dbterd.adapters.meta import Ref
from dbterd.constants import (
    DEFAULT_ALGO_RULE,
    TEST_META_IGNORE_IN_ERD,
    TEST_META_RELATIONSHIP_TYPE,
)
from dbterd.helpers.log import logger


def parse(manifest, catalog, **kwargs):
    """Get all information (tables, relationships) needed for building diagram

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(List[Table], List[Ref]): Info of parsed tables and relationships
    """
    # Parse Table
    tables = base.get_tables(manifest=manifest, catalog=catalog, **kwargs)

    # Apply selection
    tables = [
        table
        for table in tables
        if is_selected_table(
            table=table,
            select_rules=kwargs.get("select") or [],
            resource_types=kwargs.get("resource_type", []),
            exclude_rules=kwargs.get("exclude") or [],
        )
    ]

    # Parse Ref
    relationships = get_relationships(manifest=manifest, **kwargs)
    node_names = [x.node_name for x in tables]
    relationships = [
        Ref(
            name=x.name,
            table_map=[
                [t for t in tables if t.node_name == x.table_map[0]][0].name,
                [t for t in tables if t.node_name == x.table_map[1]][0].name,
            ],
            column_map=x.column_map,
            type=x.type,
        )
        for x in relationships
        if x.table_map[0] in node_names and x.table_map[1] in node_names
    ]

    # Fullfill columns in Tables (due to `select *`)
    tables = base.enrich_tables_from_relationships(
        tables=tables, relationships=relationships
    )

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (tables, relationships)


def get_relationships(manifest, **kwargs):
    """Extract relationships from dbt artifacts based on test relationship

    Args:
        manifest (dict): Manifest json

    Returns:
        List[Ref]: List of parsed relationship
    """
    rule = get_algo_rule(**kwargs)
    refs = [
        Ref(
            name=x,
            table_map=get_table_map(test_node=manifest.nodes[x], **kwargs),
            column_map=[
                str(
                    manifest.nodes[x].test_metadata.kwargs.get(rule.get("c_to"))
                    or "_and_".join(
                        manifest.nodes[x].test_metadata.kwargs.get(
                            f'{rule.get("c_to")}s', "unknown"
                        )
                    )
                )
                .replace('"', "")
                .lower(),
                str(
                    manifest.nodes[x].test_metadata.kwargs.get("column_name")
                    or manifest.nodes[x].test_metadata.kwargs.get(rule.get("c_from"))
                    or "_and_".join(
                        manifest.nodes[x].test_metadata.kwargs.get(
                            f'{rule.get("c_from")}s', "unknown"
                        )
                    )
                )
                .replace('"', "")
                .lower(),
            ],
            type=get_relationship_type(
                manifest.nodes[x].meta.get(TEST_META_RELATIONSHIP_TYPE, "")
            ),
        )
        for x in manifest.nodes
        if (
            x.startswith("test")
            and rule.get("name").lower() in x.lower()
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


def get_algo_rule(**kwargs):
    """Extract rule from the --algo option

    Args:
        kwargs.algo (str): |
            Algorithm name and optional rules.
            Samples:
            - test_relationship
            - test_relationship:(name:relationship|c_from:column_name|c_to:field)
            - test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)
            - test_relationship:(
                name:foreign_key|
                c_from:fk_column_name|
                c_to:pk_column_name|
                t_to:pk_table_name
            )

    Returns:
        dict: Rule object (
            name [default 'relationship', use contains],
            c_from [default 'column_name'],
            c_to [default 'field'],
            t_to [default 'to']
        )
    """
    algo_parts = (kwargs.get("algo") or "").replace(" ", "").split(":", 1)
    rules, _ = (
        algo_parts[1] if len(algo_parts) > 1 else DEFAULT_ALGO_RULE,
        algo_parts[0],
    )
    rules = rules[1:-1]  # remove brackets
    rules = dict(arg.split(":") for arg in rules.split("|"))
    return rules


def get_table_map(test_node, **kwargs):
    """Get the table map with order of [to, from] guaranteed

    Args:
        test_node (dict): Manifest Test node

    Returns:
        list: [to model, from model]
    """
    map = test_node.depends_on.nodes or []
    rule = get_algo_rule(**kwargs)
    to_model = str(test_node.test_metadata.kwargs.get(rule.get("t_to", "to"), {}))
    if f'("{map[1].split(".")[-1]}")'.lower() in to_model.replace("'", '"').lower():
        return [map[1], map[0]]

    return map


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
