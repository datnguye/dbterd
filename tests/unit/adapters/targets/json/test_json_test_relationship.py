from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
import json
from unittest import mock

import pytest

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.json import JsonAdapter, get_schema_version
from dbterd.core.models import Column, Ref, Table
from dbterd.core.schemas.erd import SCHEMA_BASE_URL
from tests.unit.fixtures.models import make_column, make_table


@dataclass
class DummyManifestMetadata:
    generated_at: str
    project_name: str


@dataclass
class DummyManifest:
    metadata: DummyManifestMetadata


def _dummy_manifest():
    return DummyManifest(metadata=DummyManifestMetadata(generated_at="2026-04-18T00:00:00Z", project_name="shop"))


class TestJsonTestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, expected",
        [
            # Single table, no relationships
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        resource_type="model",
                        columns=[
                            Column(name="name1", data_type="--name1-type--", description="column name 1"),
                        ],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                [],
                [],
                ["model"],
                {
                    "nodes": [
                        {
                            "id": "model.dbt_resto.table1",
                            "name": "model.dbt_resto.table1",
                            "label": None,
                            "description": None,
                            "resource_type": "model",
                            "schema_name": "--schema--",
                            "database": "--database--",
                            "columns": [
                                {
                                    "name": "name1",
                                    "data_type": "--name1-type--",
                                    "description": "column name 1",
                                    "is_primary_key": False,
                                    "is_foreign_key": False,
                                }
                            ],
                            "compiled_sql": "--irrelevant--",
                        }
                    ],
                    "edges": [],
                    "metadata": {
                        "generated_at": "2026-04-18T00:00:00Z",
                        "dbt_project_name": "shop",
                        "dbterd_version": get_schema_version(),
                    },
                },
            ),
            # Two tables with a foreign-key relationship
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        resource_type="model",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        resource_type="model",
                        columns=[Column(name="name2", data_type="--name2-type2--")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=(["name2"], ["name1"]),
                        type="n1",
                    )
                ],
                [],
                [],
                ["model", "source"],
                {
                    "nodes": [
                        {
                            "id": "model.dbt_resto.table1",
                            "name": "model.dbt_resto.table1",
                            "label": None,
                            "description": None,
                            "resource_type": "model",
                            "schema_name": "--schema--",
                            "database": "--database--",
                            "columns": [
                                {
                                    "name": "name1",
                                    "data_type": "--name1-type--",
                                    "description": None,
                                    "is_primary_key": False,
                                    "is_foreign_key": True,
                                }
                            ],
                            "compiled_sql": "--irrelevant--",
                        },
                        {
                            "id": "model.dbt_resto.table2",
                            "name": "model.dbt_resto.table2",
                            "label": None,
                            "description": None,
                            "resource_type": "model",
                            "schema_name": "--schema2--",
                            "database": "--database2--",
                            "columns": [
                                {
                                    "name": "name2",
                                    "data_type": "--name2-type2--",
                                    "description": None,
                                    "is_primary_key": False,
                                    "is_foreign_key": False,
                                }
                            ],
                            "compiled_sql": "--irrelevant--",
                        },
                    ],
                    "edges": [
                        {
                            "id": "test.dbt_resto.relationships_table1",
                            "from_id": "model.dbt_resto.table1",
                            "to_id": "model.dbt_resto.table2",
                            "from_columns": ["name1"],
                            "to_columns": ["name2"],
                            "relationship_type": "fk",
                            "name": "test.dbt_resto.relationships_table1",
                            "label": None,
                            "cardinality": "n1",
                        }
                    ],
                    "metadata": {
                        "generated_at": "2026-04-18T00:00:00Z",
                        "dbt_project_name": "shop",
                        "dbterd_version": get_schema_version(),
                    },
                },
            ),
        ],
    )
    def test_build_erd(self, tables, relationships, select, exclude, resource_type, expected):
        algo = TestRelationshipAlgo()
        adapter = JsonAdapter()
        filtered_tables = algo.filter_tables_based_on_selection(
            tables=tables,
            select=select,
            exclude=exclude,
            resource_type=resource_type,
        )
        enriched_tables = algo.enrich_tables_from_relationships(
            tables=filtered_tables,
            relationships=relationships,
        )
        table_names = {table.name for table in enriched_tables}
        filtered_relationships = [
            rel for rel in relationships if all(table_name in table_names for table_name in rel.table_map)
        ]
        result = json.loads(
            adapter.build_erd(
                tables=enriched_tables,
                relationships=filtered_relationships,
                manifest=_dummy_manifest(),
            )
        )
        result.pop("$schema")
        assert result == expected

    def test_schema_url_is_pinned_to_version(self):
        adapter = JsonAdapter()
        result = json.loads(adapter.build_erd(tables=[], relationships=[]))
        assert result["$schema"] == f"{SCHEMA_BASE_URL}/{get_schema_version()}/erd.json"

    def test_composite_foreign_key(self):
        """Composite FK maps every from/to column into the column lists."""
        adapter = JsonAdapter()
        ref = Ref(
            name="fk_composite",
            table_map=["model.pkg.departments", "model.pkg.orders"],
            column_map=(["org_id", "dept_id"], ["org_id", "dept_id"]),
            type="1n",
        )
        edge = adapter.format_edge(ref)
        assert edge == {
            "id": "fk_composite",
            "from_id": "model.pkg.orders",
            "to_id": "model.pkg.departments",
            "from_columns": ["org_id", "dept_id"],
            "to_columns": ["org_id", "dept_id"],
            "relationship_type": "fk",
            "name": "fk_composite",
            "label": None,
            "cardinality": "1n",
        }

    def test_relationship_label_propagates(self):
        adapter = JsonAdapter()
        ref = Ref(
            name="fk_labeled",
            table_map=["model.pkg.a", "model.pkg.b"],
            column_map=(["id"], ["a_id"]),
            relationship_label="belongs to",
        )
        assert adapter.format_edge(ref)["label"] == "belongs to"

    def test_node_id_falls_back_to_name(self):
        adapter = JsonAdapter()
        table = Table(
            name="orders",
            node_name=None,
            database="db",
            schema="sch",
            columns=[Column(name="id", data_type="int")],
        )
        node = adapter.format_node(table, foreign_keys={})
        assert node["id"] == "orders"

    def test_node_description_and_label_propagate(self):
        adapter = JsonAdapter()
        table = Table(
            name="model.pkg.orders",
            node_name="model.pkg.orders",
            database="db",
            schema="sch",
            description="The orders mart.",
            label="Orders",
            columns=[Column(name="id", data_type="int")],
        )
        node = adapter.format_node(table, foreign_keys={})
        assert node["description"] == "The orders mart."
        assert node["label"] == "Orders"

    def test_node_handles_no_columns(self):
        adapter = JsonAdapter()
        table = Table(name="model.pkg.x", node_name="model.pkg.x", database="db", schema="sch", columns=None)
        node = adapter.format_node(table, foreign_keys={})
        assert node["columns"] == []

    def test_metadata_empty_without_manifest(self):
        adapter = JsonAdapter()
        result = json.loads(adapter.build_erd(tables=[], relationships=[]))
        assert result["metadata"] == {
            "generated_at": "",
            "dbt_project_name": "",
            "dbterd_version": get_schema_version(),
        }

    def test_format_table_returns_json_string(self):
        adapter = JsonAdapter()
        table = Table(
            name="model.pkg.t",
            node_name="model.pkg.t",
            database="db",
            schema="sch",
            columns=[Column(name="c", data_type="int")],
        )
        parsed = json.loads(adapter.format_table(table, foreign_keys={"model.pkg.t": {"c"}}))
        assert parsed["id"] == "model.pkg.t"
        assert parsed["columns"][0]["is_foreign_key"] is True

    def test_format_relationship_returns_json_string(self):
        adapter = JsonAdapter()
        ref = Ref(
            name="fk",
            table_map=["model.pkg.a", "model.pkg.b"],
            column_map=(["id"], ["a_id"]),
        )
        parsed = json.loads(adapter.format_relationship(ref))
        assert parsed["from_id"] == "model.pkg.b"
        assert parsed["to_id"] == "model.pkg.a"

    def test_run(self):
        adapter = JsonAdapter()
        with mock.patch.object(JsonAdapter, "build_erd", return_value="dummy") as mock_build_erd:
            assert adapter.run(tables=[], relationships=[], output_file_name="xyz") == ("xyz", "dummy")
            assert adapter.run(tables=[], relationships=[]) == ("output.json", "dummy")
            assert mock_build_erd.call_count == 2

    def test_get_schema_version_fallback(self):
        with mock.patch("dbterd.adapters.targets.json.version", side_effect=PackageNotFoundError):
            assert get_schema_version() == "latest"


class TestJsonEntityGroup:
    @pytest.mark.parametrize(
        "tables, entity_group, expected_groups",
        [
            (
                [
                    make_table("model.dbt_resto.table1"),
                    make_table("model.dbt_resto.table2", columns=[make_column(name="name2")]),
                    make_table("source.dbt_resto.table3", database="--database3--", schema="--schema3--"),
                ],
                "database.schema",
                [
                    {
                        "name": "--database--.--schema--",
                        "node_ids": ["model.dbt_resto.table1", "model.dbt_resto.table2"],
                    },
                    {"name": "--database3--.--schema3--", "node_ids": ["source.dbt_resto.table3"]},
                ],
            ),
            (
                [
                    make_table("model.dbt_resto.table1"),
                    make_table("source.dbt_resto.table3", database="--database3--"),
                ],
                "schema",
                [
                    {
                        "name": "--schema--",
                        "node_ids": ["model.dbt_resto.table1", "source.dbt_resto.table3"],
                    }
                ],
            ),
        ],
    )
    def test_build_erd_with_groups(self, tables, entity_group, expected_groups):
        adapter = JsonAdapter()
        result = json.loads(adapter.build_erd(tables=tables, relationships=[], entity_group=entity_group))
        assert result["groups"] == expected_groups

    @pytest.mark.parametrize("entity_group", [None, ""])
    def test_no_groups_when_unset(self, entity_group):
        """No `groups` key is emitted when entity_group is unset/empty (default off)."""
        adapter = JsonAdapter()
        result = json.loads(
            adapter.build_erd(
                tables=[make_table("model.dbt_resto.table1")], relationships=[], entity_group=entity_group
            )
        )
        assert "groups" not in result

    def test_no_groups_when_no_tables(self):
        """No `groups` key is emitted when there are no tables to group."""
        adapter = JsonAdapter()
        result = json.loads(adapter.build_erd(tables=[], relationships=[], entity_group="database.schema"))
        assert "groups" not in result

    @pytest.mark.parametrize(
        "entity_group",
        ["databse.schema", "schema.", "."],
        ids=["typo", "trailing-dot", "lone-dot"],
    )
    def test_unknown_attribute_raises_attribute_error(self, entity_group):
        """An unknown/empty attribute name surfaces as a plain AttributeError from getattr."""
        adapter = JsonAdapter()
        with pytest.raises(AttributeError):
            adapter.build_erd(
                tables=[make_table("model.dbt_resto.table1")],
                relationships=[],
                entity_group=entity_group,
            )

    def test_group_node_id_falls_back_to_name(self):
        """A node with no node_name groups under its name, matching the node `id` field."""
        adapter = JsonAdapter()
        table = make_table(name="orders", database="db", schema="sch")
        # make_table coerces node_name to name; force the falsy case this test exists for.
        table.node_name = None
        groups = adapter.format_entity_groups([table], "schema")
        assert groups == [{"name": "sch", "node_ids": ["orders"]}]
