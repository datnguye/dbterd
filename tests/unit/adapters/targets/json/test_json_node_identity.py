import json

from dbterd.adapters.targets.json import JsonAdapter
from dbterd.core.models import Column, Ref, Table


def test_custom_entity_names_keep_node_ids_and_foreign_keys():
    tables = [
        Table(
            name="customers",
            node_name="model.tiny.customers",
            database="demo",
            schema="public",
            columns=[Column(name="id", data_type="integer")],
        ),
        Table(
            name="orders",
            node_name="model.tiny.orders",
            database="demo",
            schema="public",
            columns=[Column(name="customer_id", data_type="integer")],
        ),
    ]
    relationship = Ref(
        name="orders_customers",
        table_map=("customers", "orders"),
        column_map=(["id"], ["customer_id"]),
    )

    payload = json.loads(JsonAdapter().build_erd(tables, [relationship]))

    assert payload["edges"][0]["from_id"] == "model.tiny.orders"
    assert payload["edges"][0]["to_id"] == "model.tiny.customers"
    assert payload["nodes"][1]["columns"][0]["is_foreign_key"] is True
    assert relationship.table_map == ("customers", "orders")
