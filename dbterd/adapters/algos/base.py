import copy

from dbterd.adapters.meta import Column, Ref, Table
from dbterd.constants import (
    DEFAULT_ALGO_RULE,
    TEST_META_IGNORE_IN_ERD,
    TEST_META_RELATIONSHIP_TYPE,
)


def get_tables(manifest, catalog, **kwargs):
    """Extract tables from dbt artifacts

    Args:
        manifest (dict): dbt manifest json
        catalog (dict): dbt catalog json

    Returns:
        List[Table]: All tables parsed from dbt artifacts
    """
    tables = []

    table_exposures = get_node_exposures(manifest=manifest)

    if hasattr(manifest, "nodes"):
        for node_name, node in manifest.nodes.items():
            if (
                node_name.startswith("model.")
                or node_name.startswith("seed.")
                or node_name.startswith("snapshot.")
            ):
                catalog_node = catalog.nodes.get(node_name)
                table = get_table(
                    node_name=node_name,
                    manifest_node=node,
                    catalog_node=catalog_node,
                    exposures=table_exposures,
                    **kwargs,
                )
                tables.append(table)

    if hasattr(manifest, "sources"):
        for node_name, source in manifest.sources.items():
            if node_name.startswith("source"):
                catalog_source = catalog.sources.get(node_name)
                table = get_table(
                    node_name=node_name,
                    manifest_node=source,
                    catalog_node=catalog_source,
                    exposures=table_exposures,
                    **kwargs,
                )
                tables.append(table)

    return tables


def enrich_tables_from_relationships(tables, relationships):
    """Fullfill columns in Table due to `select *`

    Args:
        tables (List[Table]): List of Tables
        relationships (List[Ref]): List of Relationships between Tables

    Returns:
        List[Table]: Enriched tables
    """
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


def get_table(node_name, manifest_node, catalog_node=None, exposures=[], **kwargs):
    """Construct a single Table object

    Args:
        node_name (str): Node name
        manifest_node (dict): Manifest node
        catalog_node (dict, optional): Catalog node. Defaults to None.
        exposures (List, optional): List of table-exposure mapping. Defaults to [].

    Returns:
        Table: Parsed table
    """
    node_name_parts = node_name.split(".")
    table = Table(
        name=get_table_name(
            format=kwargs.get("entity_name_format"),
            **dict(
                resource=node_name_parts[0],
                package=node_name_parts[1],
                model=node_name_parts[2],
                database=manifest_node.database.lower(),
                schema=manifest_node.schema_.lower(),
                table=(
                    manifest_node.identifier.lower()
                    if hasattr(manifest_node, "identifier")
                    else manifest_node.alias.lower()
                    if hasattr(manifest_node, "alias")
                    else node_name
                ),
            ),
        ),
        node_name=node_name,
        raw_sql=get_compiled_sql(manifest_node),
        database=manifest_node.database.lower(),
        schema=manifest_node.schema_.lower(),
        columns=[],
        resource_type=node_name.split(".")[0],
        exposures=[
            x.get("exposure_name") for x in exposures if x.get("node_name") == node_name
        ],
        description=manifest_node.description,
    )

    if catalog_node:
        for column, metadata in catalog_node.columns.items():
            table.columns.append(
                Column(
                    name=str(column).lower(),
                    data_type=str(metadata.type).lower(),
                    description=metadata.comment or "",
                )
            )

    for column_name, column_metadata in manifest_node.columns.items():
        column_name = column_name.strip('"')
        find_columns = [
            c for c in table.columns if c.name.lower() == column_name.lower()
        ]
        if not find_columns:
            table.columns.append(
                Column(
                    name=column_name.lower(),
                    data_type=str(column_metadata.data_type or "unknown").lower(),
                    description=column_metadata.description or "",
                )
            )
        else:
            find_columns[0].description = (
                find_columns[0].description or column_metadata.description or ""
            )

    if not table.columns:
        table.columns.append(Column())

    return table


def get_compiled_sql(manifest_node):
    """Retrieve compiled SQL from manifest node

    Args:
        manifest_node (dict): Manifest node

    Returns:
        str: Compiled SQL
    """
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


def get_node_exposures(manifest):
    """Get the mapping of table name and exposure name

    Args:
        manifest (dict): dbt manifest json

    Returns:
        dict: Maping dict {table_name:..., exposure_name=...}
    """
    exposures = []

    if hasattr(manifest, "exposures"):
        for exposure_name, node in manifest.exposures.items():
            for node_name in node.depends_on.nodes:
                exposures.append(
                    dict(
                        node_name=node_name,
                        exposure_name=exposure_name.split(".")[-1],
                    )
                )

    return exposures


def get_table_name(format: str, **kwargs) -> str:
    """Get table name from the input format

    Args:
        table_format (str): Table format string e.g. resource.package.model

    Returns:
        str: Qualified table name
    """
    return ".".join([kwargs.get(x.lower()) or "KEYNOTFOUND" for x in format.split(".")])


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
