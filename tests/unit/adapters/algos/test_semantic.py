from unittest import mock
from unittest.mock import MagicMock

import pytest

from dbterd.adapters.algos import semantic
from dbterd.adapters.meta import Ref
from dbterd.adapters.targets import dbml as engine
from tests.unit.adapters.algos import DummyManifestRel, DummyManifestTable


class TestAlgoSemantic:
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                [
                    dict(
                        semanticModels=dict(edges=[]),
                    ),
                ],
                [],
            ),
            (
                [
                    dict(
                        semanticModels=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        entities=[dict(name="one", type="primary")],
                                        uniqueId="semantic_model.a.model1",
                                        meta=None,
                                        parents=[dict(uniqueId="model.a.model1")],
                                    )
                                ),
                                dict(
                                    node=dict(
                                        entities=[dict(name="one", type="foreign")],
                                        uniqueId="semantic_model.a.model2",
                                        meta=None,
                                        parents=[dict(uniqueId="model.a.model2")],
                                    )
                                ),
                            ]
                        ),
                    ),
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
                    dict(
                        semanticModels=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        entities=[dict(name="one", type="primary")],
                                        uniqueId="semantic_model.a.model1",
                                        meta=None,
                                        parents=[dict(uniqueId="model.a.model1")],
                                    )
                                ),
                                dict(
                                    node=dict(
                                        entities=[
                                            dict(name="one", type="foreign", expr="two")
                                        ],
                                        uniqueId="semantic_model.a.model2",
                                        meta=None,
                                        parents=[dict(uniqueId="model.a.model2")],
                                    )
                                ),
                            ]
                        ),
                    ),
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
        assert semantic._get_relationships_from_metadata(data=data) == expected

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
        assert semantic._get_relationships(manifest=manifest) == expected

    def test_find_related_nodes_by_id(self):
        assert sorted(["model.dbt_resto.table1", "model.dbt_resto.table2"]) == sorted(
            semantic.find_related_nodes_by_id(
                manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.table2"
            )
        )
        assert sorted(
            [
                "model.dbt_resto.table1",
                "model.dbt_resto.table2",
                "model.dbt_resto.tablex",
            ]
        ) == sorted(
            semantic.find_related_nodes_by_id(
                manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.table1"
            )
        )
        assert ["model.dbt_resto.not-exists"] == semantic.find_related_nodes_by_id(
            manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.not-exists"
        )

    def test_parse(self):
        with mock.patch(
            "dbterd.adapters.algos.base.get_tables",
        ) as mock_get_tables:
            with mock.patch(
                "dbterd.adapters.algos.semantic._get_relationships",
            ) as mock_get_relationships:
                engine.parse(
                    manifest="--manifest--",
                    catalog="--catalog--",
                    select=[],
                    exclude=[],
                    resource_type=["model"],
                    algo="semantic",
                    omit_entity_name_quotes=False,
                )
                mock_get_tables.assert_called_once()
                mock_get_relationships.assert_called_once()

    def test_parse_metadata(self):
        with mock.patch(
            "dbterd.adapters.algos.base.get_tables_from_metadata",
        ) as mock_get_tables:
            with mock.patch(
                "dbterd.adapters.algos.semantic._get_relationships_from_metadata",
            ) as mock_get_relationships:
                engine.parse(
                    manifest=[],
                    catalog="metadata",
                    select=[],
                    exclude=[],
                    resource_type=["model"],
                    algo="semantic",
                    omit_entity_name_quotes=False,
                )
                mock_get_tables.assert_called_once()
                mock_get_relationships.assert_called_once()
