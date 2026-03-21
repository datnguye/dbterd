"""Model contract algorithm adapter for dbterd.

This module extracts tables and relationships from dbt artifacts
using dbt model contract constraints (foreign_key) to determine connections.
Requires manifest v12+ (dbt 1.9+) for the `to` and `to_columns` fields.
"""

from typing import Optional, Union

from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def _resolve_to_node_id(to_str: str, manifest_nodes: dict) -> Optional[str]:
    """Resolve constraint.to to a manifest node unique ID.

    The constraint.to value is a fully qualified relation name in the format:
        <database>.<schema>.<table_name>  (e.g. "shaman.dummy.locations")

    This is matched against each node's relation_name field.
    Only model resource type is currently supported.

    Args:
        to_str: The constraint.to string (<database>.<schema>.<table_name>)
        manifest_nodes: Dict of manifest node IDs to node objects

    Returns:
        Matching node unique ID, or None if not found.

    """
    if not to_str:
        return None

    # model resource type takes priority over other resource types
    sorted_nodes = sorted(manifest_nodes.items(), key=lambda x: (0 if x[0].startswith("model.") else 1))
    for node_id, node in sorted_nodes:
        if getattr(node, "relation_name", None) == to_str:
            return node_id

    return None


def _get_relationship_type(meta_value: str) -> str:
    """Get short form of the relationship type from meta.

    Args:
        meta_value: Meta relationship_type value

    Returns:
        Short relationship type code.

    """
    mapping = {
        "zero-to-many": "0n",
        "zero-to-one": "01",
        "one-to-one": "11",
        "many-to-many": "nn",
        "one-to-many": "1n",
    }
    return mapping.get(meta_value.lower(), "n1")


def _extract_pk_column_names(node) -> list[str]:
    """Extract primary key column names from a manifest node's constraints.

    Checks both model-level constraints (constraint.columns where type=primary_key)
    and column-level constraints (column.constraints where type=primary_key).

    Args:
        node: The manifest node object

    Returns:
        List of column names that are part of the primary key.

    """
    pk_columns = []

    if hasattr(node, "constraints") and node.constraints:
        for constraint in node.constraints:
            if constraint.type.value == "primary_key" and getattr(constraint, "columns", None):
                pk_columns.extend(constraint.columns)

    if hasattr(node, "columns") and node.columns:
        for col_name, col in node.columns.items():
            if not hasattr(col, "constraints") or not col.constraints:
                continue
            for constraint in col.constraints:
                if constraint.type.value == "primary_key":
                    pk_columns.append(col_name)

    return pk_columns


@register_algo("model_contract", description="Detect relationships via dbt model contract constraints")
class ModelContractAlgo(BaseAlgoAdapter):
    """Algorithm adapter using dbt model contract constraints.

    Extracts relationships from dbt's model contract foreign_key constraints
    (available in manifest v12+ / dbt 1.9+) to determine table connections.
    """

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)
        tables = self._enrich_tables_with_pk_info(tables=tables, manifest=manifest)

        relationships = self.get_relationships(manifest=manifest, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def _enrich_tables_with_pk_info(self, tables: list[Table], manifest: Manifest) -> list[Table]:
        """Mark columns as primary key based on manifest constraints.

        Args:
            tables: List of parsed tables
            manifest: Manifest data

        Returns:
            Tables with is_primary_key set on relevant columns.

        """
        if not hasattr(manifest, "nodes"):
            return tables

        pk_map: dict[str, set[str]] = {}
        for node_name, node in manifest.nodes.items():
            pk_cols = _extract_pk_column_names(node)
            if pk_cols:
                pk_map[node_name] = {c.lower() for c in pk_cols}

        for table in tables:
            pks = pk_map.get(table.node_name, set())
            if not pks:
                continue
            for col in table.columns:
                if col.name.lower() in pks:
                    col.is_primary_key = True

        return tables

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from dbt Cloud metadata API response.

        Not supported for model_contract algorithm.
        """
        logger.warning("model_contract algorithm does not support dbt Cloud metadata API. Returning empty results.")
        return ([], [])

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """Find FK models related to the input model ID via constraints.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type (local file or metadata)
            **kwargs: Additional options

        Returns:
            List of manifest node unique IDs

        """
        found_nodes = [node_unique_id]
        if type == "metadata":
            return found_nodes

        if not hasattr(manifest, "nodes"):
            return found_nodes

        for node_name, node in manifest.nodes.items():
            if not node_name.startswith("model."):
                continue

            fk_targets = self._collect_fk_targets(node, manifest.nodes)

            for target_id in fk_targets:
                if node_name == node_unique_id:
                    found_nodes.append(target_id)
                elif target_id == node_unique_id:
                    found_nodes.append(node_name)

        return list(set(found_nodes))

    def get_relationships(self, manifest: Manifest, **kwargs) -> list[Ref]:
        """Extract relationships from model contract constraints.

        Scans model.* nodes for column-level and model-level foreign_key
        constraints with populated `to` fields (manifest v12+).

        Args:
            manifest: Manifest data
            **kwargs: Additional options

        Returns:
            List of parsed relationships

        """
        if not hasattr(manifest, "nodes"):
            return []

        refs = []

        for node_name, node in manifest.nodes.items():
            if not node_name.startswith("model."):
                continue

            refs.extend(self._extract_column_level_refs(node_name, node, manifest.nodes))
            refs.extend(self._extract_model_level_refs(node_name, node, manifest.nodes))

        return self.get_unique_refs(refs=refs)

    def _collect_fk_targets(self, node, manifest_nodes: dict) -> list[str]:
        """Collect all FK target node IDs from a node's constraints.

        Args:
            node: Manifest node object
            manifest_nodes: Dict of all manifest nodes

        Returns:
            List of target node IDs

        """
        targets = []

        if hasattr(node, "columns") and node.columns:
            for col in node.columns.values():
                if not hasattr(col, "constraints") or not col.constraints:
                    continue
                for constraint in col.constraints:
                    if constraint.type.value == "foreign_key" and getattr(constraint, "to", None):
                        target_id = _resolve_to_node_id(constraint.to, manifest_nodes)
                        if target_id:
                            targets.append(target_id)

        if hasattr(node, "constraints") and node.constraints:
            for constraint in node.constraints:
                if constraint.type.value == "foreign_key" and getattr(constraint, "to", None):
                    target_id = _resolve_to_node_id(constraint.to, manifest_nodes)
                    if target_id:
                        targets.append(target_id)

        return targets

    def _extract_column_level_refs(self, node_name: str, node, manifest_nodes: dict) -> list[Ref]:
        """Extract Ref objects from column-level FK constraints.

        Args:
            node_name: The node unique ID (e.g. model.pkg.orders)
            node: The manifest node object
            manifest_nodes: Dict of all manifest nodes

        Returns:
            List of Ref objects

        """
        refs = []

        if not hasattr(node, "columns") or not node.columns:
            return refs

        for col_name, col in node.columns.items():
            if not hasattr(col, "constraints") or not col.constraints:
                continue

            for constraint in col.constraints:
                if constraint.type.value != "foreign_key":
                    continue
                if not getattr(constraint, "to", None):
                    continue

                to_node_id = _resolve_to_node_id(constraint.to, manifest_nodes)
                if not to_node_id:
                    continue

                to_columns = getattr(constraint, "to_columns", None) or [col_name]
                col_meta = getattr(col, "meta", None) or {}
                relationship_type = _get_relationship_type(col_meta.get(TEST_META_RELATIONSHIP_TYPE, ""))

                constraint_name = getattr(constraint, "name", None) or None
                node_meta = getattr(node, "meta", None) or {}
                relationship_label = node_meta.get("relationship_labels", {}).get(constraint_name)
                for to_column in to_columns:
                    refs.append(
                        Ref(
                            name=constraint_name or node_name,
                            table_map=[to_node_id, node_name],
                            column_map=([to_column], [col_name]),
                            type=relationship_type,
                            relationship_label=relationship_label,
                        )
                    )

        return refs

    def _extract_model_level_refs(self, node_name: str, node, manifest_nodes: dict) -> list[Ref]:
        """Extract Ref objects from model-level FK constraints.

        Args:
            node_name: The node unique ID (e.g. model.pkg.orders)
            node: The manifest node object
            manifest_nodes: Dict of all manifest nodes

        Returns:
            List of Ref objects

        """
        refs = []

        if not hasattr(node, "constraints") or not node.constraints:
            return refs

        for constraint in node.constraints:
            if constraint.type.value != "foreign_key":
                continue
            if not getattr(constraint, "to", None):
                continue
            if not getattr(constraint, "columns", None):
                continue

            to_node_id = _resolve_to_node_id(constraint.to, manifest_nodes)
            if not to_node_id:
                continue

            to_columns = list(getattr(constraint, "to_columns", None) or constraint.columns)
            node_meta = getattr(node, "meta", None) or {}
            constraint_name = getattr(constraint, "name", None) or None
            relationship_type = _get_relationship_type(
                node_meta.get("relationship_types", {}).get(constraint_name) or ""
            )
            relationship_label = node_meta.get("relationship_labels", {}).get(constraint_name) or node_meta.get(
                "relationship_label"
            )

            refs.append(
                Ref(
                    name=constraint_name or node_name,
                    table_map=[to_node_id, node_name],
                    column_map=(to_columns, list(constraint.columns)),
                    type=relationship_type,
                    relationship_label=relationship_label,
                )
            )

        return refs
