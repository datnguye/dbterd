"""Base class for algorithm adapters.

This module provides the abstract base class that all algorithm adapters
must inherit from. It implements common functionality like metadata dispatch
and defines the interface that subclasses must implement.
"""

from abc import ABC, abstractmethod
import copy
from typing import Optional, Union

import click

from dbterd.core.filter import is_selected_table
from dbterd.core.models import Column, Ref, Table
from dbterd.helpers.log import logger
from dbterd.types import Catalog, InfoSchema, Manifest


class BaseAlgoAdapter(ABC):
    """Base class for all algorithm adapters.

    Algorithm adapters are responsible for parsing dbt artifacts (manifest/catalog)
    and extracting tables and relationships. They support both file-based artifacts
    and dbt Cloud metadata API.

    Subclasses must implement:
        - parse_artifacts: Parse from file-based manifest/catalog
        - parse_metadata: Parse from dbt Cloud metadata API

    The parse() method automatically dispatches to parse_metadata() when
    catalog == "metadata", to parse_info_schema() when catalog == "info_schema",
    otherwise it calls parse_artifacts().

    """

    def parse(self, manifest: Manifest, catalog: Union[str, Catalog], **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse dbt artifacts to extract tables and relationships.

        This is the main entry point. It automatically dispatches to
        parse_metadata() when catalog == "metadata" and to parse_info_schema()
        when catalog == "info_schema".

        Args:
            manifest: Manifest json, metadata dict (when catalog == "metadata")
                or the dbt info schema (when catalog == "info_schema")
            catalog: Catalog json, "metadata" or "info_schema" string
            **kwargs: Additional options including:
                resource_type: Types of resources to include
                entity_name_format: Format string for entity names
                select: Selection rules to include tables
                exclude: Rules to exclude tables
                algo: Algorithm name with optional rules

        Returns:
            Tuple of (tables, relationships)

        """
        if catalog == "metadata":
            return self.parse_metadata(data=manifest, **kwargs)
        if catalog == "info_schema":
            return self.parse_info_schema(info=manifest, **kwargs)
        return self.parse_artifacts(manifest=manifest, catalog=catalog, **kwargs)

    @abstractmethod
    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse from file-based manifest/catalog artifacts.

        Args:
            manifest: Manifest json
            catalog: Catalog json
            **kwargs: Additional options

        Returns:
            Tuple of (tables, relationships)

        """
        pass

    @abstractmethod
    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse from dbt Cloud metadata API response.

        Args:
            data: Metadata API response dict
            **kwargs: Additional options

        Returns:
            Tuple of (tables, relationships)

        """
        pass

    def parse_info_schema(self, info: InfoSchema, **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse from the dbt 2.0 parquet info schema (`target/info_schema/v1`).

        Algorithms opt in by overriding this hook; the default refuses rather
        than silently drawing an ERD without relationships.

        Args:
            info: Parsed dbt info schema
            **kwargs: Additional options

        Raises:
            click.UsageError: The algorithm does not support the info schema

        Returns:
            Tuple of (tables, relationships)

        """
        raise click.UsageError(f"Algorithm `{kwargs.get('algo')}` does not support the dbt info schema input")

    def collect(self, tables: list[Table], relationships: list[Ref]) -> tuple[list[Table], list[Ref]]:
        """
        Finalize parsed tables and node-level relationships into the ERD result.

        Keeps the relationships whose both ends are among the tables, renames
        their ends to entity names, adds the related columns missing from the
        tables (due to `select *`), and sorts both lists.

        Args:
            tables: Selected tables
            relationships: Relationships keyed by node unique IDs

        Returns:
            Tuple of (tables, relationships)

        """
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)
        tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """
        Find FK/PK models related to a given model.

        This is used for generating single-model ERDs that include
        related tables. Override in subclasses to provide algorithm-specific
        relationship discovery.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type ("metadata" or None for file-based)
            **kwargs: Additional options

        Returns:
            List of related manifest node unique IDs

        """
        return [node_unique_id]

    def find_related_nodes_from_refs(self, relationships: list[Ref], node_unique_id: str) -> list[str]:
        """
        Find the nodes sharing a relationship with the given node.

        Args:
            relationships: Relationships keyed by node unique IDs
            node_unique_id: Node unique ID

        Returns:
            The input node and its related node unique IDs

        """
        found_nodes = {node_unique_id}
        for relationship in relationships:
            if node_unique_id in relationship.table_map:
                found_nodes.update(relationship.table_map)
        return list(found_nodes)

    # -------------------------------------------------------------------------
    # Common table extraction methods
    # -------------------------------------------------------------------------

    def get_tables_from_metadata(self, data=None, **kwargs) -> list[Table]:
        """
        Extract tables from dbt metadata.

        Args:
            data (dict): dbt metadata query result
            **kwargs: Additional options including:
                resource_type (list): Types of resources to include (model, source, etc.)
                entity_name_format (str): Format string for entity names
                omit_columns (bool): Whether to exclude columns from tables

        Returns:
            List[Table]: All parsed tables

        """
        if data is None:
            data = []
        tables = []
        table_exposures = self.get_node_exposures_from_metadata(data=data, **kwargs)
        # Model
        if "model" in kwargs.get("resource_type", []):
            for data_item in data:
                for model in data_item.get("models", {}).get("edges", []):
                    table = self.get_table_from_metadata(
                        model_metadata=model,
                        exposures=table_exposures,
                        **kwargs,
                    )
                    tables.append(table)

        # Source
        if "source" in kwargs.get("resource_type", []):
            for data_item in data:
                for model in data_item.get("sources", {}).get("edges", []):
                    table = self.get_table_from_metadata(
                        model_metadata=model,
                        exposures=table_exposures,
                        **kwargs,
                    )
                    tables.append(table)

        return tables

    def get_tables(self, manifest: Manifest, catalog: Catalog, **kwargs) -> list[Table]:
        """
        Extract tables from dbt artifacts.

        Args:
            manifest (dict): dbt manifest json
            catalog (dict): dbt catalog json
            **kwargs: Additional options including:
                entity_name_format (str): Format string for entity names
                omit_columns (bool): Whether to exclude columns from tables

        Returns:
            List[Table]: All tables parsed from dbt artifacts

        """
        tables = []

        table_exposures = self.get_node_exposures(manifest=manifest)

        if hasattr(manifest, "nodes"):
            for node_name, node in manifest.nodes.items():
                if node_name.startswith("model.") or node_name.startswith("seed.") or node_name.startswith("snapshot."):
                    catalog_node = catalog.nodes.get(node_name)
                    table = self.get_table(
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
                    table = self.get_table(
                        node_name=node_name,
                        manifest_node=source,
                        catalog_node=catalog_source,
                        exposures=table_exposures,
                        **kwargs,
                    )
                    tables.append(table)

        return tables

    def get_tables_from_info_schema(self, info: InfoSchema, **kwargs) -> list[Table]:
        """
        Extract tables from the dbt info schema.

        Args:
            info: Parsed dbt info schema
            **kwargs: Additional options including:
                entity_name_format (str): Format string for entity names

        Returns:
            List[Table]: Tables of the enabled models, seeds, snapshots and sources

        """
        columns_of: dict[str, list] = {}
        for column in sorted(info.dbt_node_columns, key=lambda c: c.column_index or 0):
            columns_of.setdefault(column.node_unique_id, []).append(column)

        parents_of: dict[str, list[str]] = {}
        exposures_of: dict[str, list[str]] = {}
        for edge in info.dbt_edges:
            parents_of.setdefault(edge.child_unique_id, []).append(edge.parent_unique_id)
            if edge.child_unique_id.startswith("exposure."):
                exposures_of.setdefault(edge.parent_unique_id, []).append(edge.child_unique_id.split(".")[-1])

        return [
            self.get_table_from_info_schema(
                node=node,
                columns=columns_of.get(node.unique_id, []),
                parents=parents_of.get(node.unique_id, []),
                exposures=exposures_of.get(node.unique_id, []),
                **kwargs,
            )
            for node in [*info.dbt_models, *info.dbt_seeds, *info.dbt_snapshots, *info.dbt_sources]
            if node.enabled is not False
        ]

    def filter_tables_based_on_selection(self, tables: list[Table], **kwargs) -> list[Table]:
        """
        Filter list of tables based on the Selection Rules.

        Args:
            tables (List[Table]): Parsed tables
            **kwargs: Additional options including:
                select (list): Selection rules to include tables
                exclude (list): Rules to exclude tables
                resource_type (list): Types of resources to include

        Returns:
            List[Table]: Filtered tables

        """
        return [
            table
            for table in tables
            if is_selected_table(
                table=table,
                select_rules=kwargs.get("select") or [],
                resource_types=kwargs.get("resource_type", []),
                exclude_rules=kwargs.get("exclude") or [],
            )
        ]

    def select_tables(self, tables: list[Table], **kwargs) -> list[Table]:
        """Apply the selection rules, then resolve dependencies when `with_dependencies` is set.

        Dependency resolution needs the pre-selection set so it can collapse
        through intermediate nodes the selection dropped.
        """
        selected = self.filter_tables_based_on_selection(tables=tables, **kwargs)
        if kwargs.get("with_dependencies"):
            return self.resolve_dependencies(selected_tables=selected, all_tables=tables)
        return selected

    def enrich_tables_from_relationships(self, tables: list[Table], relationships: list[Ref]) -> list[Table]:
        """
        Fulfill columns in Table due to `select *`.

        Args:
            tables (List[Table]): List of Tables
            relationships (List[Ref]): List of Relationships between Tables

        Returns:
            List[Table]: Enriched tables

        """
        copied_tables = copy.deepcopy(tables)
        for relationship in relationships:
            for table in copied_tables:
                if table.name == relationship.table_map[0]:
                    table_columns = [x.name.lower() for x in table.columns]
                    for col_name in relationship.column_map[0]:
                        if col_name.lower() not in table_columns:
                            table.columns.append(Column(name=col_name))
                            table_columns.append(col_name.lower())
                if table.name == relationship.table_map[1]:
                    table_columns = [x.name.lower() for x in table.columns]
                    for col_name in relationship.column_map[1]:
                        if col_name.lower() not in table_columns:
                            table.columns.append(Column(name=col_name))
                            table_columns.append(col_name.lower())
        return copied_tables

    def get_table_from_metadata(self, model_metadata, exposures=None, **kwargs) -> Table:
        """
        Construct a single Table object (for Metadata).

        Args:
            model_metadata (dict): Metadata model node
            exposures (list, optional): List of parsed exposures. Defaults to [].
            **kwargs: Additional options including:
                entity_name_format (str): Format string for entity names
                omit_columns (bool): Whether to exclude columns from tables

        Returns:
            Table: Parsed table

        """
        if exposures is None:
            exposures = []
        node_name = model_metadata.get("node", {}).get("uniqueId")
        node_description = model_metadata.get("node", {}).get("description")
        node_database = model_metadata.get("node", {}).get("database").lower()
        node_schema = model_metadata.get("node", {}).get("schema").lower()
        node_label = model_metadata.get("node", {}).get("meta", {}).get("label")
        node_name_parts = node_name.split(".")
        table = Table(
            name=self.get_table_name(
                format=kwargs.get("entity_name_format"),
                **{
                    "resource": node_name_parts[0],
                    "package": node_name_parts[1],
                    "model": node_name_parts[2],
                    "database": node_database,
                    "schema": model_metadata.get("node", {}).get("schema").lower(),
                    "table": (
                        model_metadata.get("node", {}).get("alias") or model_metadata.get("node", {}).get("name")
                    ).lower(),
                },
            ),
            node_name=node_name,
            raw_sql=None,
            database=node_database,
            schema=node_schema,
            columns=[],
            resource_type=node_name.split(".", maxsplit=1)[0],
            exposures=[x.get("exposure_name") for x in exposures if x.get("node_name") == node_name],
            description=node_description,
            label=node_label,
            raw_depends_on=[
                parent.get("uniqueId")
                for parent in (model_metadata.get("node", {}).get("parents") or [])
                if parent.get("uniqueId")
            ],
        )

        # columns
        table_catalog = model_metadata.get("node", {}).get("catalog", {})
        if table_catalog:
            for column in table_catalog.get("columns", []):
                table.columns.append(
                    Column(
                        name=column.get("name", "").lower(),
                        data_type=column.get("type", "").lower(),
                        description=column.get("description", ""),
                    )
                )

        if not table.columns:
            table.columns.append(Column())

        return table

    def get_table(self, node_name: str, manifest_node, catalog_node=None, exposures=None, **kwargs) -> Table:
        """
        Construct a single Table object.

        Args:
            node_name (str): Node name
            manifest_node (dict): Manifest node
            catalog_node (dict, optional): Catalog node. Defaults to None.
            exposures (List, optional): List of table-exposure mapping. Defaults to [].
            **kwargs: Additional options including:
                entity_name_format (str): Format string for entity names
                omit_columns (bool): Whether to exclude columns from tables

        Returns:
            Table: Parsed table

        """
        if exposures is None:
            exposures = []
        node_name_parts = node_name.split(".")
        table = Table(
            name=self.get_table_name(
                format=kwargs.get("entity_name_format"),
                **{
                    "resource": node_name_parts[0],
                    "package": node_name_parts[1],
                    "model": node_name_parts[2],
                    "database": manifest_node.database.lower(),
                    "schema": manifest_node.schema_.lower(),
                    "table": (
                        manifest_node.identifier.lower()
                        if hasattr(manifest_node, "identifier")
                        else (manifest_node.alias.lower() if hasattr(manifest_node, "alias") else node_name)
                    ),
                },
            ),
            node_name=node_name,
            raw_sql=self.get_compiled_sql(manifest_node),
            database=manifest_node.database.lower(),
            schema=manifest_node.schema_.lower(),
            columns=[],
            resource_type=node_name.split(".", maxsplit=1)[0],
            exposures=[x.get("exposure_name") for x in exposures if x.get("node_name") == node_name],
            description=manifest_node.description,
            label=manifest_node.meta.get("label"),
            # Sources have no `depends_on`; seeds have one without `nodes`.
            raw_depends_on=list(getattr(getattr(manifest_node, "depends_on", None), "nodes", None) or []),
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

        for original_column_name, column_metadata in manifest_node.columns.items():
            column_name = original_column_name.strip('"')
            find_columns = [c for c in table.columns if c.name.lower() == column_name.lower()]
            if not find_columns:
                table.columns.append(
                    Column(
                        name=column_name.lower(),
                        data_type=str(column_metadata.data_type or "unknown").lower(),
                        description=column_metadata.description or "",
                    )
                )
            else:
                find_columns[0].description = find_columns[0].description or column_metadata.description or ""

        if not table.columns:
            table.columns.append(Column())

        return table

    def get_table_from_info_schema(
        self, node, columns: list, parents: list[str], exposures: list[str], **kwargs
    ) -> Table:
        """
        Construct a single Table object (for the dbt info schema).

        Column types prefer the warehouse type, then the declared one, then the inferred one.

        Args:
            node: Info schema model, seed, snapshot or source row
            columns: Info schema `node_columns` rows of the node, in column order
            parents: Parent node unique IDs
            exposures: Names of the exposures depending on the node
            **kwargs: Additional options including:
                entity_name_format (str): Format string for entity names

        Returns:
            Table: Parsed table

        """
        node_name_parts = node.unique_id.split(".")
        database = (node.database_name or "").lower()
        schema = (node.schema_name or "").lower()
        return Table(
            name=self.get_table_name(
                format=kwargs.get("entity_name_format"),
                resource=node_name_parts[0],
                package=node_name_parts[1],
                model=node_name_parts[2],
                database=database,
                schema=schema,
                table=(node.identifier or node.alias or node.name).lower(),
            ),
            node_name=node.unique_id,
            raw_sql=node.compiled_code or node.raw_code,
            database=database,
            schema=schema,
            columns=[
                Column(
                    name=column.column_name.strip('"').lower(),
                    data_type=str(
                        column.data_type_actual or column.data_type_declared or column.data_type_inferred or "unknown"
                    ).lower(),
                    description=column.description or "",
                )
                for column in columns
            ]
            or [Column()],
            resource_type=node_name_parts[0],
            exposures=exposures,
            description=node.description or "",
            label=(node.meta or {}).get("label"),
            raw_depends_on=parents,
        )

    def get_compiled_sql(self, manifest_node):
        """
        Retrieve compiled SQL from manifest node.

        Args:
            manifest_node (dict): Manifest node

        Returns:
            str: Compiled SQL

        """
        if hasattr(manifest_node, "compiled_sql"):  # up to v6
            return manifest_node.compiled_sql

        if hasattr(manifest_node, "compiled_code"):  # from v7
            return manifest_node.compiled_code

        if hasattr(manifest_node, "columns"):  # nodes having no compiled but just list of columns
            columns = ",\n            ".join([str(x) for x in manifest_node.columns])
            table = f"{manifest_node.database}.{manifest_node.schema_}.undefined"
            return f"""select
            {columns}
        from {table}"""

        return manifest_node.raw_sql  # fallback to raw dbt code

    def get_node_exposures_from_metadata(self, data=None, **kwargs):
        """
        Get the mapping of table name and exposure name (for Metadata).

        Args:
            data (list, optional): Metadata result list. Defaults to [].
            **kwargs: Additional options that might be passed from parent functions

        Returns:
            list: List of mapping dict {table_name:..., exposure_name=...}

        """
        if data is None:
            data = []
        exposures = []
        for data_item in data:
            for exposure in data_item.get("exposures", {}).get("edges", []):
                name = exposure.get("node", {}).get("name")
                parent_nodes = exposure.get("node", {}).get("parents")
                for node in parent_nodes:
                    node_name = node.get("uniqueId", "")
                    if node_name.split(".", maxsplit=1)[0] in kwargs.get("resource_type", []):
                        exposures.append(
                            {
                                "node_name": node_name,
                                "exposure_name": name,
                            }
                        )

        return exposures

    def get_node_exposures(self, manifest: Manifest) -> list[dict[str, str]]:
        """
        Get the mapping of table name and exposure name.

        Args:
            manifest (dict): dbt manifest json

        Returns:
            list: List of mapping dict {table_name:..., exposure_name=...}

        """
        exposures = []

        if hasattr(manifest, "exposures"):
            for exposure_name, node in manifest.exposures.items():
                for node_name in node.depends_on.nodes:
                    exposures.append(
                        {
                            "node_name": node_name,
                            "exposure_name": exposure_name.split(".")[-1],
                        }
                    )

        return exposures

    def resolve_dependencies(self, selected_tables: list[Table], all_tables: list[Table]) -> list[Table]:
        """Fill in each selected table's `depends_on` with upstream entity names.

        The dbt DAG usually routes a mart to its sources through intermediate
        nodes (staging, intermediate models) that the selection leaves out. The
        walk passes straight through those, so each table ends up pointing at
        its nearest *selected* ancestors and the graph stays connected however
        the selection cuts through it.

        Because the walk can only ever terminate on a selected node, every name
        it produces belongs to a table that is actually emitted. Targets that
        render dependencies (DBML `Dep`) therefore cannot emit a dangling
        endpoint, which those formats reject outright.

        Args:
            selected_tables: Tables surviving selection; mutated in place.
            all_tables: Every parsed table, pre-selection, needed to walk
                through nodes the selection dropped.

        Returns:
            The same `selected_tables` list, with `depends_on` populated.

        """
        parents_of = {t.node_name: t.raw_depends_on for t in all_tables if t.node_name}
        name_of = {t.node_name: t.name for t in all_tables if t.node_name}
        selected_ids = {t.node_name for t in selected_tables if t.node_name}

        def nearest_selected_ancestors(node_id: str) -> list[str]:
            """Nearest selected ancestor ids, walking up through unselected nodes."""
            found: list[str] = []
            seen: set[str] = {node_id}
            queue = list(parents_of.get(node_id, []))
            while queue:
                current = queue.pop()
                if current in seen:
                    continue  # already handled, or a cycle in a malformed manifest
                seen.add(current)
                if current in selected_ids:
                    found.append(current)
                else:
                    queue.extend(parents_of.get(current, []))
            return found

        for table in selected_tables:
            if not table.node_name:
                continue

            # Several dbt nodes can share one entity name (every table of a source
            # collapses onto `source.<package>.<source_name>` by default), so dedupe
            # by name and drop the self-edge that collapse would otherwise create.
            upstream_ids = nearest_selected_ancestors(table.node_name)
            table.depends_on = sorted({name_of[i] for i in upstream_ids if i in name_of} - {table.name})

        return selected_tables

    def get_table_name(self, format: str, **kwargs) -> str:
        """
        Get table name from the input format.

        Args:
            format (str): Table format string e.g. resource.package.model
            **kwargs: Dictionary containing values for each format part

        Returns:
            str: Qualified table name

        """
        return ".".join([kwargs.get(x.lower()) or "KEYNOTFOUND" for x in format.split(".")])

    # -------------------------------------------------------------------------
    # Common relationship methods
    # -------------------------------------------------------------------------

    def make_up_relationships(
        self, relationships: Optional[list[Ref]] = None, tables: Optional[list[Table]] = None
    ) -> list[Ref]:
        """
        Filter Refs given by the parsed Tables & applied the entity name format.

        Args:
            relationships (List[Ref], optional): Parsed relationships. Defaults to [].
            tables (List[Table], optional): Parsed tables. Defaults to [].

        Returns:
            List[Ref]: Cooked relationships

        """
        if tables is None:
            tables = []
        if relationships is None:
            relationships = []
        node_names = [x.node_name for x in tables]
        relationships = [
            Ref(
                name=x.name,
                table_map=[
                    next(t for t in tables if t.node_name == x.table_map[0]).name,
                    next(t for t in tables if t.node_name == x.table_map[1]).name,
                ],
                column_map=x.column_map,
                type=x.type,
                relationship_label=x.relationship_label,
            )
            for x in relationships
            if x.table_map[0] in node_names and x.table_map[1] in node_names
        ]

        return relationships

    def get_unique_refs(self, refs: Optional[list[Ref]] = None) -> list[Ref]:
        """
        Remove duplicates in the Relationship list.

        Args:
            refs (list[Ref], optional): List of parsed relationship. Defaults to [].

        Returns:
            list[Ref]: Distinct parsed relationship

        """
        if refs is None:
            refs = []
        if not refs:
            return []

        distinct_list = [refs[0]]
        for ref in refs:
            distinct_maps = [str((x.table_map, x.column_map)) for x in distinct_list]
            if str((ref.table_map, ref.column_map)) not in distinct_maps:
                distinct_list.append(ref)

        return distinct_list
