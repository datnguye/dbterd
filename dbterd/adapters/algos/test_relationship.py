from dbterd.adapters.algos import base
from dbterd.adapters.filter import is_selected_table
from dbterd.adapters.meta import Ref
from dbterd.helpers.log import logger


def parse_metadata(data, **kwargs):
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
    node_names = [x.node_name for x in tables]
    relationships = [
        x
        for x in relationships
        if x.table_map[0] in node_names and x.table_map[1] in node_names
    ]

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (tables, relationships)


def parse(manifest, catalog, **kwargs):
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
