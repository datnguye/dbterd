"""JSON target adapter for dbterd.

This module converts parsed dbt artifacts into the canonical dbterd ERD JSON
payload (``nodes`` / ``edges`` / ``metadata``). The shape is published as a
JSON Schema on the docs site (https://dbterd.datnguye.me/latest/schemas/erd/)
so downstream tools — like the dbterd VS Code extension and dbt-docs — can
consume it with confidence rather than reverse-engineering field names.
"""

from importlib.metadata import PackageNotFoundError, version
import json

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.builder.json_builder import JsonERDBuilder
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target
from dbterd.core.schemas.erd import SCHEMA_BASE_URL


def get_schema_version() -> str:
    """Return the dbterd version used to pin the published JSON Schema.

    Falls back to ``latest`` when the package metadata is unavailable (for
    example, when running from a source checkout that was never installed).
    """
    try:
        return version("dbterd")
    except PackageNotFoundError:
        return "latest"


@register_target("json", description="dbterd ERD JSON payload (nodes/edges/metadata)")
class JsonAdapter(BaseTargetAdapter):
    """Canonical JSON format target adapter.

    Emits the dbterd ERD payload consumed by the VS Code extension and other
    integrations. The structure is intentionally stable and schema-validated;
    if you need a different shape, you probably want a different target.
    """

    file_extension = ".json"
    default_filename = "output.json"

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build the dbterd ERD JSON payload from tables and relationships."""
        foreign_keys = self._collect_foreign_keys(relationships)
        schema_version = get_schema_version()

        builder = JsonERDBuilder()
        builder.add_tables(tables, lambda t: self.format_node(t, foreign_keys))
        builder.add_relationships(relationships, self.format_edge)

        # Keys are emitted in this order; `metadata` is a plain static value
        # (the builder only treats `$tables`/`$relationships` as placeholders).
        schema = {
            "$schema": f"{SCHEMA_BASE_URL}/{schema_version}/erd.json",
            "nodes": "$tables",
            "edges": "$relationships",
            "metadata": self._build_metadata(schema_version, **kwargs),
        }

        entity_group = kwargs.get("entity_group")
        if entity_group and tables:
            schema["groups"] = self.format_entity_groups(tables, entity_group)

        return builder.build(schema=schema)

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table as a JSON string.

        Exists only to satisfy the ``BaseTargetAdapter`` ABC; ``build_erd`` uses
        ``format_node`` directly and never calls this. Kept for parity with the
        other targets and for any caller that wants a single-node JSON string.
        """
        foreign_keys = kwargs.get("foreign_keys", {})
        return json.dumps(self.format_node(table, foreign_keys))

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship as a JSON string.

        ABC-contract counterpart to ``format_edge`` (see ``format_table``);
        ``build_erd`` uses ``format_edge`` directly.
        """
        return json.dumps(self.format_edge(relationship))

    def format_node(self, table: Table, foreign_keys: dict[str, set[str]]) -> dict:
        """Format a single table as a dbterd ERD node dict."""
        node_id = table.node_name or table.name
        fk_columns = foreign_keys.get(node_id, set())
        return {
            "id": node_id,
            "name": table.name,
            "label": table.label,
            "description": table.description or None,
            "resource_type": table.resource_type,
            "schema_name": table.schema,
            "database": table.database,
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "description": col.description or None,
                    "is_primary_key": col.is_primary_key,
                    "is_foreign_key": col.name in fk_columns,
                }
                for col in (table.columns or [])
            ],
            # `Table.raw_sql` holds compiled SQL: the parser fills it via
            # `get_compiled_sql` (compiled_code/compiled_sql, raw dbt code only as a
            # last resort), hence `compiled_sql` as the public field name.
            "compiled_sql": table.raw_sql,
        }

    def format_edge(self, relationship: Ref) -> dict:
        """Format a single relationship as a dbterd ERD edge dict.

        ``table_map`` / ``column_map`` are ordered ``(to, from)`` by dbterd's
        algorithms, so the FK side (``from``) is index 1 and the referenced
        side (``to``) is index 0.
        """
        to_table, from_table = relationship.table_map[0], relationship.table_map[1]
        to_columns, from_columns = list(relationship.column_map[0]), list(relationship.column_map[1])
        return {
            "id": relationship.name,
            "from_id": from_table,
            "to_id": to_table,
            "from_columns": from_columns,
            "to_columns": to_columns,
            "relationship_type": "fk",
            "name": relationship.name,
            "label": relationship.relationship_label,
            "cardinality": relationship.type,
        }

    def format_entity_groups(self, tables: list[Table], entity_group: str) -> list[dict]:
        """Group nodes by ``Table`` attributes, mirroring the DBML ``TableGroup`` feature.

        ``entity_group`` is a dot-separated list of ``Table`` attribute names
        (e.g. ``"database.schema"`` or ``"schema"``). Each table's group key is built
        by joining those attribute values with ``.``, preserving first-seen order.

        Returns a list of ``{"name": <key>, "node_ids": [...]}`` dicts, where each
        ``node_id`` matches the corresponding node's ``id`` field.
        """
        attributes = [attr.lower() for attr in entity_group.split(".")]

        groups: dict[str, list[str]] = {}
        for table in tables:
            key = ".".join(str(getattr(table, attr)) for attr in attributes)
            node_id = table.node_name or table.name
            groups.setdefault(key, []).append(node_id)

        return [{"name": key, "node_ids": node_ids} for key, node_ids in groups.items()]

    def _collect_foreign_keys(self, relationships: list[Ref]) -> dict[str, set[str]]:
        """Map each node id to the set of its columns participating in a FK.

        Used to flag ``is_foreign_key`` on columns, since dbterd's Column model
        only tracks primary keys natively.
        """
        foreign_keys: dict[str, set[str]] = {}
        for rel in relationships:
            from_table = rel.table_map[1]
            from_columns = rel.column_map[1]
            foreign_keys.setdefault(from_table, set()).update(from_columns)
        return foreign_keys

    def _build_metadata(self, schema_version: str, **kwargs) -> dict:
        """Build the ``metadata`` block from the manifest, when available."""
        generated_at = ""
        dbt_project_name = ""
        manifest = kwargs.get("manifest")
        if manifest is not None and hasattr(manifest, "metadata"):
            generated_at = str(getattr(manifest.metadata, "generated_at", "") or "")
            dbt_project_name = getattr(manifest.metadata, "project_name", "") or ""

        return {
            "generated_at": generated_at,
            "dbt_project_name": dbt_project_name,
            "dbterd_version": schema_version,
        }
