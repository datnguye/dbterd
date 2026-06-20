import json

import jsonschema

from dbterd.adapters.targets.json import JsonAdapter, get_schema_version
from dbterd.core.models import Column, Ref, Table
from dbterd.core.schemas.erd import SCHEMA_BASE_URL, build_erd_json_schema
from tests.unit.fixtures.models import make_column, make_table


class TestBuildErdJsonSchema:
    def test_id_is_pinned_to_version(self):
        schema = build_erd_json_schema("1.2.3")
        assert schema["$id"] == f"{SCHEMA_BASE_URL}/1.2.3/erd.json"

    def test_top_level_shape(self):
        schema = build_erd_json_schema("latest")
        assert schema["type"] == "object"
        assert set(schema["required"]) == {"nodes", "edges", "metadata"}
        assert set(schema["$defs"]) >= {"node", "edge", "column", "metadata", "cardinality", "resourceType"}

    def test_guaranteed_fields_are_required_and_non_null(self):
        """Fields the producer always emits are required with non-null types."""
        defs = build_erd_json_schema("latest")["$defs"]

        assert {"schema_name", "database"} <= set(defs["node"]["required"])
        assert "data_type" in defs["column"]["required"]
        assert "name" in defs["edge"]["required"]

        assert defs["node"]["properties"]["schema_name"]["type"] == "string"
        assert defs["node"]["properties"]["database"]["type"] == "string"
        assert defs["column"]["properties"]["data_type"]["type"] == "string"
        assert defs["edge"]["properties"]["name"]["type"] == "string"

    def test_resource_type_enum_matches_collected_node_types(self):
        """Only node types dbterd actually collects are valid resource_type values."""
        schema = build_erd_json_schema("latest")
        assert set(schema["$defs"]["resourceType"]["enum"]) == {"model", "source", "seed", "snapshot"}

    def test_validates_real_adapter_output(self):
        """The published schema must accept what the json target actually emits."""
        tables = [
            Table(
                name="model.pkg.orders",
                node_name="model.pkg.orders",
                database="db",
                schema="sch",
                resource_type="model",
                columns=[
                    Column(name="id", data_type="int", is_primary_key=True),
                    Column(name="customer_id", data_type="int"),
                ],
            ),
            Table(
                name="model.pkg.customers",
                node_name="model.pkg.customers",
                database="db",
                schema="sch",
                resource_type="model",
                columns=[Column(name="id", data_type="int", is_primary_key=True)],
            ),
        ]
        relationships = [
            Ref(
                name="fk_orders_customers",
                table_map=["model.pkg.customers", "model.pkg.orders"],
                column_map=(["id"], ["customer_id"]),
                type="n1",
            )
        ]
        payload = json.loads(JsonAdapter().build_erd(tables, relationships))
        jsonschema.validate(instance=payload, schema=build_erd_json_schema(get_schema_version()))

    def test_validates_grouped_adapter_output(self):
        """The schema must accept the optional `groups` block emitted with `--entity-group`."""
        tables = [
            make_table(
                name="model.pkg.orders",
                database="db",
                schema="sch",
                columns=[make_column(name="id", data_type="int")],
            )
        ]
        payload = json.loads(JsonAdapter().build_erd(tables, [], entity_group="database.schema"))
        assert payload["groups"] == [{"name": "db.sch", "node_ids": ["model.pkg.orders"]}]
        jsonschema.validate(instance=payload, schema=build_erd_json_schema(get_schema_version()))
