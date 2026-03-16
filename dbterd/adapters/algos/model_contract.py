"""Model contract algorithm adapter for dbterd.

This module extracts tables and relationships from dbt artifacts
using dbt model contract constraints (foreign_key) to determine connections.
Requires manifest v12+ (dbt 1.9+) for the `to` and `to_columns` fields.
"""

import re
from typing import Optional, Union

from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def _resolve_ref_to_node_id(ref_str: str, manifest_nodes: dict) -> Optional[str]:
    """Resolve a ref string like ref('model_name') to a manifest node unique ID.

    Supports:
        - ref('model_name')
        - ref("model_name")
        - ref('package', 'model_name')
        - ref("package", "model_name")

    Args:
        ref_str: The ref string from constraint.to
        manifest_nodes: Dict of manifest node IDs to node objects

    Returns:
        Matching node unique ID, or None if not found.

    """
    if not ref_str:
        return None

    match = re.match(r"""ref\(\s*['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"]\s*)?\)""", ref_str)
    if not match:
        return None

    first_arg = match.group(1)
    second_arg = match.group(2)
    model_name = second_arg if second_arg else first_arg

    for node_id in manifest_nodes:
        if node_id.startswith("model.") and node_id.split(".")[-1] == model_name:
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

        relationships = self.get_relationships(manifest=manifest, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

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
                        target_id = _resolve_ref_to_node_id(constraint.to, manifest_nodes)
                        if target_id:
                            targets.append(target_id)

        if hasattr(node, "constraints") and node.constraints:
            for constraint in node.constraints:
                if constraint.type.value == "foreign_key" and getattr(constraint, "to", None):
                    target_id = _resolve_ref_to_node_id(constraint.to, manifest_nodes)
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

                to_node_id = _resolve_ref_to_node_id(constraint.to, manifest_nodes)
                if not to_node_id:
                    continue

                to_columns = getattr(constraint, "to_columns", None)
                to_column = to_columns[0] if to_columns else col_name
                from_column = col_name

                col_meta = getattr(col, "meta", None) or {}
                relationship_type = _get_relationship_type(col_meta.get(TEST_META_RELATIONSHIP_TYPE, ""))

                refs.append(
                    Ref(
                        name=node_name,
                        table_map=[to_node_id, node_name],
                        column_map=[to_column, from_column],
                        type=relationship_type,
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

            to_node_id = _resolve_ref_to_node_id(constraint.to, manifest_nodes)
            if not to_node_id:
                continue

            to_columns = getattr(constraint, "to_columns", None) or constraint.columns
            node_meta = getattr(node, "meta", None) or {}
            relationship_type = _get_relationship_type(node_meta.get(TEST_META_RELATIONSHIP_TYPE, ""))

            for from_col, to_col in zip(constraint.columns, to_columns):
                refs.append(
                    Ref(
                        name=node_name,
                        table_map=[to_node_id, node_name],
                        column_map=[to_col, from_col],
                        type=relationship_type,
                    )
                )

        return refs
