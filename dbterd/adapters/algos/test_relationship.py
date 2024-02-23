from typing import List, Tuple, Union

import click

from dbterd.adapters.algos import base
from dbterd.adapters.filter import is_selected_table
from dbterd.adapters.meta import Ref, Table
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def parse_metadata(data, **kwargs) -> Tuple[List[Table], List[Ref]]:
    """Get all information (tables, relationships) needed for building diagram
    (from Metadata)

    Args:
        data (dict): metadata dict

    Returns:
        Tuple(List[Table], List[Ref]): Info of parsed tables and relationships
    """
    tables = []
    relationships = []

    # Parse Table
    tables = base.get_tables_from_metadata(data=data, **kwargs)

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
    relationships = base.get_relationships_from_metadata(data=data, **kwargs)
    relationships = base.make_up_relationships(
        relationships=relationships, tables=tables
    )

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (tables, relationships)


def parse(
    manifest: Manifest, catalog: Union[str, Catalog], **kwargs
) -> Tuple[List[Table], List[Ref]]:
    """Get all information (tables, relationships) needed for building diagram

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(List[Table], List[Ref]): Info of parsed tables and relationships
    """
    # Parse metadata
    if catalog == "metadata":
        return parse_metadata(data=manifest, **kwargs)

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
    relationships = base.get_relationships(manifest=manifest, **kwargs)
    relationships = base.make_up_relationships(
        relationships=relationships, tables=tables
    )

    # Fullfill columns in Tables (due to `select *`)
    tables = base.enrich_tables_from_relationships(
        tables=tables, relationships=relationships
    )

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (
        sorted(tables, key=lambda tbl: tbl.node_name),
        sorted(relationships, key=lambda rel: rel.name),
    )


def find_related_nodes_by_id(
    manifest: Union[Manifest, dict], node_unique_id: str, type: str = None, **kwargs
) -> List[str]:
    """Find the FK models which are related to the input model ID inclusively

    given the manifest data of dbt project

    Args:
        manifest (Union[Manifest, dict]): Manifest data
        node_unique_id (str): Manifest node unique ID
        type (str, optional): Manifest type (local file or metadata). Defaults to None.

    Raises:
        click.BadParameter: Not Supported manifest type

    Returns:
        List[str]: Manifest nodes' unique ID
    """
    if type is not None:
        raise click.BadParameter("Not supported manifest type")

    rule = base.get_algo_rule(**kwargs)
    test_nodes = base.get_test_nodes_by_rule_name(
        manifest=manifest, rule_name=rule.get("name").lower()
    )
    found_nodes = [node_unique_id]
    for test_node in test_nodes:
        nodes = manifest.nodes[test_node].depends_on.nodes or []
        if node_unique_id in nodes:
            found_nodes.extend(nodes)

    return list(set(found_nodes))
