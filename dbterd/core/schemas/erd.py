"""JSON Schema definition for the dbterd ERD payload.

This is the single source of truth for the ``json`` target's output contract.
It is published to the docs site so that downstream consumers — the dbterd VS Code
extension, dbt-docs, and friends — can validate dbterd output instead of guessing
field names.
"""

import os
from typing import Any


# Absolute base URL for the published ERD JSON Schema. It is baked into every
# emitted payload's ``$schema`` (validators must be able to dereference it) and
# into the schema's own ``$id``. The default tracks the docs ``site_url``; set
# ``DBTERD_SCHEMA_BASE_URL`` to point payloads at a different host (e.g. a fork
# or a vanity domain) without touching code.
SCHEMA_BASE_URL = os.environ.get(
    "DBTERD_SCHEMA_BASE_URL",
    "https://dbterd.datnguye.me/latest/schemas/erd",
)


def build_erd_json_schema(schema_version: str) -> dict[str, Any]:
    """Return the dbterd ERD JSON Schema, pinned to ``schema_version``.

    Args:
        schema_version: Version segment for ``$id`` (typically the dbterd version,
            or ``latest`` for the rolling alias).

    Returns:
        A JSON Schema (draft 2020-12) describing the ERD payload.

    """
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URL}/{schema_version}/erd.json",
        "title": "dbterd ERD Payload",
        "description": "Entity Relationship Diagram payload produced by the dbterd `json` target.",
        "type": "object",
        "required": ["nodes", "edges", "metadata"],
        "additionalProperties": True,
        "properties": {
            "$schema": {"type": "string", "format": "uri"},
            "nodes": {
                "type": "array",
                "description": "Tables/models in the diagram.",
                "items": {"$ref": "#/$defs/node"},
            },
            "edges": {
                "type": "array",
                "description": "Relationships (foreign keys) between nodes.",
                "items": {"$ref": "#/$defs/edge"},
            },
            "metadata": {"$ref": "#/$defs/metadata"},
            "groups": {
                "type": "array",
                "description": "Node groupings, emitted only when the `--entity-group` option is set.",
                "items": {"$ref": "#/$defs/group"},
            },
        },
        "$defs": {
            "resourceType": {
                "type": "string",
                "description": "dbt node types dbterd collects (manifest: model/seed/snapshot nodes + sources).",
                "enum": ["model", "source", "seed", "snapshot"],
            },
            "cardinality": {
                "type": "string",
                "description": "dbterd relationship type code.",
                "enum": ["01", "11", "0n", "1n", "nn", "n1"],
            },
            "column": {
                "type": "object",
                "required": ["name", "data_type"],
                "additionalProperties": True,
                "properties": {
                    "name": {"type": "string"},
                    "data_type": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "is_primary_key": {"type": "boolean", "default": False},
                    "is_foreign_key": {"type": "boolean", "default": False},
                },
            },
            "node": {
                "type": "object",
                "required": ["id", "name", "resource_type", "schema_name", "database", "columns"],
                "additionalProperties": True,
                "properties": {
                    "id": {"type": "string", "description": "dbt unique id, e.g. model.pkg.orders."},
                    "name": {"type": "string", "description": "Friendly table name."},
                    "label": {"type": ["string", "null"], "description": "Display label, when set."},
                    "description": {"type": ["string", "null"], "description": "Table/model documentation."},
                    "resource_type": {"$ref": "#/$defs/resourceType"},
                    "schema_name": {"type": "string"},
                    "database": {"type": "string"},
                    "columns": {"type": "array", "items": {"$ref": "#/$defs/column"}},
                    "compiled_sql": {"type": ["string", "null"], "description": "Compiled SQL of the node."},
                },
            },
            "edge": {
                "type": "object",
                "required": ["id", "from_id", "to_id", "name"],
                "additionalProperties": True,
                "properties": {
                    "id": {"type": "string"},
                    "from_id": {"type": "string", "description": "Node id of the FK (child) side."},
                    "to_id": {"type": "string", "description": "Node id of the referenced (parent) side."},
                    "from_columns": {"type": "array", "items": {"type": "string"}},
                    "to_columns": {"type": "array", "items": {"type": "string"}},
                    "relationship_type": {"type": "string", "enum": ["fk"], "default": "fk"},
                    "name": {"type": "string"},
                    "label": {"type": ["string", "null"]},
                    "cardinality": {"$ref": "#/$defs/cardinality"},
                },
            },
            "group": {
                "type": "object",
                "required": ["name", "node_ids"],
                "additionalProperties": True,
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Group key, the dot-joined `--entity-group` attribute values.",
                    },
                    "node_ids": {
                        "type": "array",
                        "description": "Node ids belonging to this group.",
                        "items": {"type": "string"},
                    },
                },
            },
            "metadata": {
                "type": "object",
                "required": ["generated_at", "dbt_project_name", "dbterd_version"],
                "additionalProperties": True,
                "properties": {
                    "generated_at": {"type": "string"},
                    "dbt_project_name": {"type": "string"},
                    "dbterd_version": {"type": "string", "description": "dbterd version that produced this payload."},
                },
            },
        },
    }
