from unittest import mock
from unittest.mock import MagicMock

import pytest

from dbterd.adapters.algos.semantic import SemanticAlgo
from dbterd.core.models import Ref
from tests.unit.adapters.algos import DummyManifestRel, DummyManifestTable


class TestAlgoSemantic:
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                [
                    {
                        "semanticModels": {"edges": []},
                    },
                ],
                [],
            ),
            (
                [
                    {
                        "semanticModels": {
                            "edges": [
                                {
                                    "node": {
                                        "entities": [{"name": "one", "type": "primary"}],
                                        "uniqueId": "semantic_model.a.model1",
                                        "meta": None,
                                        "parents": [{"uniqueId": "model.a.model1"}],
                                    }
                                },
                                {
                                    "node": {
                                        "entities": [{"name": "one", "type": "foreign"}],
                                        "uniqueId": "semantic_model.a.model2",
                                        "meta": None,
                                        "parents": [{"uniqueId": "model.a.model2"}],
                                    }
                                },
                            ]
                        },
                    },
                ],
                [
                    Ref(
                        name="semantic_model.a.model1",
                        table_map=("model.a.model1", "model.a.model2"),
                        column_map=("one", "one"),
                        type="",
                    )
                ],
            ),
            (
                [
                    {
                        "semanticModels": {
                            "edges": [
                                {
                                    "node": {
                                        "entities": [{"name": "one", "type": "primary"}],
                                        "uniqueId": "semantic_model.a.model1",
                                        "meta": None,
                                        "parents": [{"uniqueId": "model.a.model1"}],
                                    }
                                },
                                {
                                    "node": {
                                        "entities": [
                                            {
                                                "name": "one",
                                                "type": "foreign",
                                                "expr": "two",
                                            }
                                        ],
                                        "uniqueId": "semantic_model.a.model2",
                                        "meta": None,
                                        "parents": [{"uniqueId": "model.a.model2"}],
                                    }
                                },
                            ]
                        },
                    },
                ],
                [
                    Ref(
                        name="semantic_model.a.model1",
                        table_map=("model.a.model1", "model.a.model2"),
                        column_map=("one", "two"),
                        type="",
                    )
                ],
            ),
        ],
    )
    def test_get_relationships_from_metadata(self, data, expected):
        algo = SemanticAlgo()
        assert algo.get_relationships_from_metadata(data=data) == expected

    @pytest.mark.parametrize(
        "manifest, expected",
        [
            (
                DummyManifestRel(),
                [
                    Ref(
                        name="semantic_model.dbt_resto.sm1",
                        table_map=("model.dbt_resto.table1", "model.dbt_resto.table2"),
                        column_map=("id1", "id2"),
                        type="",
                    ),
                    Ref(
                        name="semantic_model.dbt_resto.sm1",
                        table_map=("model.dbt_resto.table1", "model.dbt_resto.tablex"),
                        column_map=("id1", "x"),
                        type="",
                    ),
                ],
            ),
            (MagicMock(return_value={"semantic_models": {}, "nodes": {}}), []),
            (DummyManifestTable(), []),
        ],
    )
    def test_get_relationships(self, manifest, expected):
        algo = SemanticAlgo()
        assert algo.get_relationships(manifest=manifest) == expected

    def test_find_related_nodes_by_id(self):
        algo = SemanticAlgo()
        assert sorted(["model.dbt_resto.table1", "model.dbt_resto.table2"]) == sorted(
            algo.find_related_nodes_by_id(manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.table2")
        )
        assert sorted(
            [
                "model.dbt_resto.table1",
                "model.dbt_resto.table2",
                "model.dbt_resto.tablex",
            ]
        ) == sorted(algo.find_related_nodes_by_id(manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.table1"))
        assert algo.find_related_nodes_by_id(
            manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.not-exists"
        ) == ["model.dbt_resto.not-exists"]

    def test_parse(self):
        with (
            mock.patch.object(
                SemanticAlgo,
                "get_tables",
            ) as mock_get_tables,
            mock.patch.object(
                SemanticAlgo,
                "get_relationships",
            ) as mock_get_relationships,
        ):
            algo = SemanticAlgo()
            algo.parse_artifacts(
                manifest="--manifest--",
                catalog="--catalog--",
                select=[],
                exclude=[],
                resource_type=["model"],
            )
            mock_get_tables.assert_called_once()
            mock_get_relationships.assert_called_once()

    def test_parse_metadata(self):
        with (
            mock.patch.object(
                SemanticAlgo,
                "get_tables_from_metadata",
            ) as mock_get_tables,
            mock.patch.object(
                SemanticAlgo,
                "get_relationships_from_metadata",
            ) as mock_get_relationships,
        ):
            algo = SemanticAlgo()
            algo.parse_metadata(
                data=[],
                select=[],
                exclude=[],
                resource_type=["model"],
            )
            mock_get_tables.assert_called_once()
            mock_get_relationships.assert_called_once()
