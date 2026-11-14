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
from dbterd.types import Catalog, InfoSchema, Manifest


def _resolve_ref_to_node_id(to_str: str, manifest_nodes: dict) -> Optional[str]:
    """Resolve an unrendered ``ref(...)`` constraint.to to a manifest node unique ID.

    dbt does not always render the contract foreign-key ``to`` down to a relation
    name — a manifest produced by ``dbt parse``/``compile`` (rather than a full
    ``build`` against a live target) keeps it as the literal ``ref('...')``
    expression. This resolves those by matching the referenced model name.

    Supports:
        - ``ref('model_name')`` / ``ref("model_name")``
        - ``ref('package', 'model_name')`` / ``ref("package", "model_name")``

    Args:
        to_str: The constraint.to string (a ``ref(...)`` expression)
        manifest_nodes: Dict of manifest node IDs to node objects

    Returns:
        Matching node unique ID, or None if it is not a ref or no model matches.

    """
    if not to_str:
        return None

    match = re.match(r"""ref\(\s*['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"]\s*)?\)""", to_str)
    if not match:
        return None

    first_arg, second_arg = match.group(1), match.group(2)
    model_name = second_arg if second_arg else first_arg

    for node_id in manifest_nodes:
        if node_id.startswith("model.") and node_id.split(".")[-1] == model_name:
            return node_id

    return None


def _resolve_to_node_id(to_str: str, manifest_nodes: dict) -> Optional[str]:
    """Resolve constraint.to to a manifest node unique ID.

    Handles both shapes dbt may emit for a contract foreign-key ``to``:

    - A fully qualified relation name (``<database>.<schema>.<table_name>``, e.g.
      ``"shaman.dummy.locations"``), matched against each node's ``relation_name``.
      This is what a built/rendered manifest carries.
    - An unrendered ``ref(...)`` expression (e.g. ``"ref('locations')"``), which a
      parsed/compiled manifest carries — resolved via _resolve_ref_to_node_id.

    Only the model resource type is currently supported.

    Args:
        to_str: The constraint.to string (relation name or ``ref(...)`` expression)
        manifest_nodes: Dict of manifest node IDs to node objects

    Returns:
        Matching node unique ID, or None if not found.

    """
    if not to_str:
        return None

    # model resource type takes priority over other resource types
    sorted_nodes = sorted(manifest_nodes.items(), key=lambda x: 0 if x[0].startswith("model.") else 1)
    for node_id, node in sorted_nodes:
        if getattr(node, "relation_name", None) == to_str:
            return node_id

    # Fall back to resolving an unrendered ref('...') expression by model name
    return _resolve_ref_to_node_id(to_str=to_str, manifest_nodes=manifest_nodes)


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


def _info_schema_nodes(info: InfoSchema) -> dict:
    """Map each info schema model, seed, snapshot and source unique ID to its row."""
    return {node.unique_id: node for node in BaseAlgoAdapter.get_info_schema_nodes(info)}


def _info_schema_pk_map(info: InfoSchema) -> dict[str, set[str]]:
    """Map each info schema node unique ID to its lowercase primary key column names.

    Reads model-level constraints from the node rows and column-level ones from `node_columns`,
    mirroring _extract_pk_column_names for a manifest node.
    """
    pk_map: dict[str, set[str]] = {}
    for node in BaseAlgoAdapter.get_info_schema_nodes(info):
        for constraint in _constraints_of_type(node.constraints, "primary_key"):
            columns = _constraint_value(constraint, "columns") or []
            pk_map.setdefault(node.unique_id, set()).update(c.lower() for c in columns)
    for column in info.dbt_node_columns:
        if _constraints_of_type(column.constraints, "primary_key"):
            pk_map.setdefault(column.node_unique_id, set()).add(column.column_name.lower())
    return pk_map


def _constraint_value(constraint, key: str):
    """Read a constraint field from a manifest constraint object or an info schema dict."""
    if isinstance(constraint, dict):
        return constraint.get(key)
    value = getattr(constraint, key, None)
    return getattr(value, "value", value)


def _constraints_of_type(constraints: Optional[list], constraint_type: str) -> list:
    """Filter constraints (manifest objects or info schema dicts) by their type."""
    return [c for c in constraints or [] if _constraint_value(c, "type") == constraint_type]


def _column_fk_refs(
    node_name: str, node_meta: Optional[dict], column_name: str, column_meta: Optional[dict], constraints, nodes: dict
) -> list[Ref]:
    """Build the relationships of a column's foreign_key constraints.

    Args:
        node_name: The node unique ID (e.g. model.pkg.orders)
        node_meta: The node meta
        column_name: The constrained column
        column_meta: The column meta
        constraints: The column constraints (manifest objects or info schema dicts)
        nodes: Dict of node unique IDs to nodes, to resolve `to`

    Returns:
        List of Ref objects, one per referenced column

    """
    relationship_type = _get_relationship_type((column_meta or {}).get(TEST_META_RELATIONSHIP_TYPE, ""))
    refs = []
    for constraint in _constraints_of_type(constraints, "foreign_key"):
        to_node_id = _resolve_to_node_id(_constraint_value(constraint, "to"), nodes)
        if not to_node_id:
            continue
        constraint_name = _constraint_value(constraint, "name") or None
        for to_column in _constraint_value(constraint, "to_columns") or [column_name]:
            refs.append(
                Ref(
                    name=constraint_name or node_name,
                    table_map=[to_node_id, node_name],
                    column_map=([to_column], [column_name]),
                    type=relationship_type,
                    relationship_label=(node_meta or {}).get("relationship_labels", {}).get(constraint_name),
                )
            )
    return refs


def _model_fk_refs(node_name: str, node_meta: Optional[dict], constraints, nodes: dict) -> list[Ref]:
    """Build the relationships of a model's model-level foreign_key constraints.

    Args:
        node_name: The node unique ID (e.g. model.pkg.orders)
        node_meta: The node meta
        constraints: The model constraints (manifest objects or info schema dicts)
        nodes: Dict of node unique IDs to nodes, to resolve `to`

    Returns:
        List of Ref objects, one per constraint

    """
    node_meta = node_meta or {}
    refs = []
    for constraint in _constraints_of_type(constraints, "foreign_key"):
        columns = _constraint_value(constraint, "columns")
        to_node_id = _resolve_to_node_id(_constraint_value(constraint, "to"), nodes)
        if not to_node_id or not columns:
            continue
        constraint_name = _constraint_value(constraint, "name") or None
        refs.append(
            Ref(
                name=constraint_name or node_name,
                table_map=[to_node_id, node_name],
                column_map=(list(_constraint_value(constraint, "to_columns") or columns), list(columns)),
                type=_get_relationship_type(node_meta.get("relationship_types", {}).get(constraint_name) or ""),
                relationship_label=node_meta.get("relationship_labels", {}).get(constraint_name)
                or node_meta.get("relationship_label"),
            )
        )
    return refs


@register_algo("model_contract", description="Detect relationships via dbt model contract constraints")
class ModelContractAlgo(BaseAlgoAdapter):
    """Algorithm adapter using dbt model contract constraints.

    Extracts relationships from dbt's model contract foreign_key constraints
    (available in manifest v12+ / dbt 1.9+) to determine table connections.
    """

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        tables = self.select_tables(self.get_tables(manifest=manifest, catalog=catalog, **kwargs), **kwargs)
        tables = self._enrich_tables_with_pk_info(tables=tables, manifest=manifest)
        return self.collect(tables=tables, relationships=self.get_relationships(manifest=manifest, **kwargs))

    def parse_info_schema(self, info: InfoSchema, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from the dbt info schema."""
        tables = self.select_tables(self.get_tables_from_info_schema(info=info, **kwargs), **kwargs)
        tables = self._mark_primary_keys(tables=tables, pk_map=_info_schema_pk_map(info))
        return self.collect(tables=tables, relationships=self.get_relationships_from_info_schema(info=info))

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

        return self._mark_primary_keys(tables=tables, pk_map=pk_map)

    @staticmethod
    def _mark_primary_keys(tables: list[Table], pk_map: dict[str, set[str]]) -> list[Table]:
        """Set is_primary_key on the columns listed per node unique ID in `pk_map`."""
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
        if type == "info_schema":
            return self.find_related_nodes_from_refs(
                self.get_relationships_from_info_schema(info=manifest), node_unique_id
            )

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

    def get_relationships_from_info_schema(self, info: InfoSchema) -> list[Ref]:
        """Extract relationships from the foreign_key constraints of the dbt info schema models.

        Column-level constraints come from `node_columns`, model-level ones from `models`.

        Args:
            info: Parsed dbt info schema

        Returns:
            List of parsed relationships

        """
        nodes = _info_schema_nodes(info)
        refs = []
        for column in info.dbt_node_columns:
            node = nodes.get(column.node_unique_id)
            if column.node_unique_id.startswith("model.") and node is not None:
                refs.extend(
                    _column_fk_refs(
                        column.node_unique_id, node.meta, column.column_name, column.meta, column.constraints, nodes
                    )
                )
        for model in info.dbt_models:
            refs.extend(_model_fk_refs(model.unique_id, model.meta, model.constraints, nodes))
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
        return [
            ref
            for col_name, col in (getattr(node, "columns", None) or {}).items()
            for ref in _column_fk_refs(
                node_name,
                getattr(node, "meta", None),
                col_name,
                getattr(col, "meta", None),
                getattr(col, "constraints", None),
                manifest_nodes,
            )
        ]

    def _extract_model_level_refs(self, node_name: str, node, manifest_nodes: dict) -> list[Ref]:
        """Extract Ref objects from model-level FK constraints.

        Args:
            node_name: The node unique ID (e.g. model.pkg.orders)
            node: The manifest node object
            manifest_nodes: Dict of all manifest nodes

        Returns:
            List of Ref objects

        """
        return _model_fk_refs(
            node_name, getattr(node, "meta", None), getattr(node, "constraints", None), manifest_nodes
        )
