from types import SimpleNamespace

import pytest

from dbterd.adapters.algos.semantic import SemanticAlgo


@pytest.mark.parametrize(
    "meta,expected",
    [
        ({}, "n1"),
        ({"relationship_type": "many-to-one"}, "n1"),
        ({"relationship_type": "one-to-one"}, "11"),
        ({"relationship_type": "zero-to-one"}, "01"),
        ({"relationship_type": "zero-to-many"}, "0n"),
        ({"relationship_type": "one-to-many"}, "1n"),
        ({"relationship_type": "many-to-many"}, "nn"),
        *[({"relationship_type": code}, code) for code in ("0n", "01", "11", "nn", "1n", "n1")],
    ],
)
def test_semantic_relationship_cardinality(meta, expected):
    models = {}
    metadata = []
    for name, kind, column in [("customers", "primary", "id"), ("orders", "foreign", "customer_id")]:
        models[name] = SimpleNamespace(
            depends_on=SimpleNamespace(nodes=[f"model.tiny.{name}"]),
            entities=[SimpleNamespace(name="customer", type=SimpleNamespace(value=kind), expr=column)],
            primary_entity=None,
            config=SimpleNamespace(meta=meta),
        )
        metadata.append(
            {
                "node": {
                    "uniqueId": name,
                    "parents": [{"uniqueId": f"model.tiny.{name}"}],
                    "entities": [{"name": "customer", "type": kind, "expr": column}],
                    "meta": meta,
                }
            }
        )

    algo = SemanticAlgo()
    assert algo.get_relationships(SimpleNamespace(semantic_models=models))[0].type == expected
    data = [{"semanticModels": {"edges": metadata}}]
    assert algo.get_relationships_from_metadata(data)[0].type == expected
