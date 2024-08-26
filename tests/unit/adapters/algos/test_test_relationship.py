from unittest import mock
from unittest.mock import MagicMock

import click
import pytest

from dbterd.adapters.algos import base as base_algo
from dbterd.adapters.algos import test_relationship
from dbterd.adapters.meta import Column, Ref, Table
from tests.unit.adapters.algos import (
    DummyCatalogTable,
    DummyManifestError,
    DummyManifestHasColumns,
    DummyManifestRel,
    DummyManifestTable,
    DummyManifestV6,
    DummyManifestV7,
    DummyManifestWithExposure,
)


class TestAlgoTestRelationship:
    @pytest.mark.parametrize(
        "manifest, catalog, expected",
        [
            (
                DummyManifestTable(),
                DummyCatalogTable(),
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                        description="",
                    ),
                    Table(
                        name="model.dbt_resto.table_dummy_columns",
                        node_name="model.dbt_resto.table_dummy_columns",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column()],
                        raw_sql="--irrelevant--",
                        description="",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[
                            Column(name="name3", data_type="--name3-type--"),
                            Column(name="name2"),
                        ],
                        raw_sql="--irrelevant--",
                        description="",
                    ),
                    Table(
                        name="source.dummy.source_table",
                        node_name="source.dummy.source_table",
                        database="--database--",
                        schema="--schema--",
                        columns=[
                            Column(name="name1", data_type="--name1-type--"),
                            Column(name="name2"),
                        ],
                        raw_sql="--irrelevant--",
                        resource_type="source",
                        description="",
                    ),
                ],
            ),
        ],
    )
    def test_get_tables(self, manifest, catalog, expected):
        with mock.patch(
            "dbterd.adapters.algos.base.get_compiled_sql",
            return_value="--irrelevant--",
        ) as mock_get_compiled_sql:
            assert (
                base_algo.get_tables(
                    manifest,
                    catalog,
                    **dict(entity_name_format="resource.package.model")
                )
                == expected
            )
            mock_get_compiled_sql.assert_called()

    @pytest.mark.parametrize(
        "manifest, expected",
        [
            (DummyManifestV6(), "compiled_sql"),
            (DummyManifestV7(), "compiled_code"),
            (DummyManifestError(), "raw_sql"),
            (
                DummyManifestHasColumns(),
                """select
                col1,
                col2
                from database_dummy.schema_dummy.undefined
                """,
            ),
        ],
    )
    def test_get_compiled(self, manifest, expected):
        assert base_algo.get_compiled_sql(manifest_node=manifest).replace(
            " ", ""
        ).replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")

    @pytest.mark.parametrize(
        "manifest, algorithm, expected",
        [
            (
                DummyManifestRel(),
                None,
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["f2", "f1"],
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table3",
                        table_map=["model.dbt_resto.tabley", "model.dbt_resto.tablex"],
                        column_map=["f2", "f1"],
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table4",
                        table_map=[
                            "model.dbt_resto.table-m2",
                            "model.dbt_resto.table-m1",
                        ],
                        column_map=["f2", "f1"],
                        type="11",
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table1_reverse",
                        table_map=[
                            "model.dbt_resto.table-r2",
                            "model.dbt_resto.table-r1",
                        ],
                        column_map=["f2", "f1"],
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table1_recursive",
                        table_map=["model.dbt_resto.table1", "model.dbt_resto.table1"],
                        column_map=["f2", "f1"],
                    ),
                ],
            ),
            (
                DummyManifestRel(),
                "test_relationship:(name:foreign_key|c_from:column_name|c_to:pk_column_name)",
                [
                    Ref(
                        name="test.dbt_resto.foreign_key_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["f2", "f1"],
                    ),
                ],
            ),
            (MagicMock(return_value={"depends_on": {}, "nodes": {}}), None, []),
        ],
    )
    def test_get_relationships(self, manifest, algorithm, expected):
        assert (
            base_algo.get_relationships(manifest=manifest, algo=algorithm) == expected
        )

    @pytest.mark.parametrize(
        "meta, type",
        [
            ("zero-to-many", "0n"),
            ("one-to-many", "1n"),
            ("zero-to-one", "01"),
            ("one-to-one", "11"),
            ("many-to-many", "nn"),
            ("many-to-one", "n1"),
            ("--irrelevant--", "n1"),
        ],
    )
    def test_get_relationship_type(self, meta, type):
        assert base_algo.get_relationship_type(meta=meta) == type

    @pytest.mark.parametrize(
        "manifest, expected",
        [
            (
                DummyManifestWithExposure(),
                [
                    dict(node_name="model.dbt_resto.table1", exposure_name="dummy"),
                    dict(node_name="model.dbt_resto.table2", exposure_name="dummy"),
                ],
            ),
            (
                DummyManifestTable(),
                [],
            ),
        ],
    )
    def test_get_node_exposures(self, manifest, expected):
        assert expected == base_algo.get_node_exposures(manifest=manifest)

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([], []),
            ([{}], []),
            ([{}, {}], []),
            ([{"models": {"edges": []}, "sources": {"edges": []}}], []),
        ],
    )
    @mock.patch("dbterd.adapters.algos.base.get_table_from_metadata")
    @mock.patch("dbterd.adapters.algos.base.get_node_exposures_from_metadata")
    def test_get_tables_from_metadata_w_empty_data(
        self,
        mock_get_node_exposures_from_metadata,
        mock_get_table_from_metadata,
        data,
        expected,
    ):
        assert expected == base_algo.get_tables_from_metadata(
            data=data, resource_type=["model", "source"]
        )
        mock_get_node_exposures_from_metadata.assert_called_once()
        assert mock_get_table_from_metadata.call_count == 0

    @pytest.mark.parametrize(
        "resource_type, data, get_table_from_metadata_call_count",
        [
            (
                ["model"],
                [{"models": {"edges": ["item1", "item2"]}, "sources": {"edges": []}}],
                2,
            ),
            (
                ["model"],
                [
                    {
                        "models": {"edges": ["item1", "item2"]},
                        "sources": {"edges": ["source1"]},
                    }
                ],
                2,
            ),
            (
                ["model", "source"],
                [
                    {
                        "models": {"edges": ["item1", "item2"]},
                        "sources": {"edges": ["source1"]},
                    }
                ],
                3,
            ),
            (
                [],
                [
                    {
                        "models": {"edges": ["item1", "item2"]},
                        "sources": {"edges": ["source1"]},
                    }
                ],
                0,
            ),
        ],
    )
    @mock.patch("dbterd.adapters.algos.base.get_table_from_metadata")
    @mock.patch("dbterd.adapters.algos.base.get_node_exposures_from_metadata")
    def test_get_tables_from_metadata_w_1_data(
        self,
        mock_get_node_exposures_from_metadata,
        mock_get_table_from_metadata,
        resource_type,
        data,
        get_table_from_metadata_call_count,
    ):
        base_algo.get_tables_from_metadata(data=data, resource_type=resource_type)
        mock_get_node_exposures_from_metadata.assert_called_once()
        assert (
            mock_get_table_from_metadata.call_count
            == get_table_from_metadata_call_count
        )

    @pytest.mark.parametrize(
        "data, kwargs, expected",
        [
            (
                [
                    {
                        "models": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "model.package.name1",
                                        "database": "db1",
                                        "schema": "sc1",
                                        "name": "name1",
                                        "catalog": {},
                                    }
                                },
                            ]
                        }
                    }
                ],
                dict(
                    entity_name_format="resource.package.model", resource_type=["model"]
                ),
                [
                    Table(
                        name="model.package.name1",
                        database="db1",
                        schema="sc1",
                        columns=[
                            Column(name="unknown", data_type="unknown", description="")
                        ],
                        raw_sql=None,
                        resource_type="model",
                        exposures=[],
                        node_name="model.package.name1",
                        description=None,
                    ),
                ],
            ),
            (
                [
                    {
                        "models": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "model.package.name1",
                                        "database": "db1",
                                        "schema": "sc1",
                                        "name": "name1",
                                        "catalog": {},
                                    }
                                },
                            ]
                        },
                        "exposures": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "exposure.package.e1",
                                        "name": "e1",
                                        "parents": [
                                            {"uniqueId": "model.package.name1"}
                                        ],
                                    }
                                },
                            ]
                        },
                    }
                ],
                dict(
                    entity_name_format="resource.package.model",
                    resource_type=["model"],
                    select=["exposure:e1"],
                ),
                [
                    Table(
                        name="model.package.name1",
                        database="db1",
                        schema="sc1",
                        columns=[
                            Column(name="unknown", data_type="unknown", description="")
                        ],
                        raw_sql=None,
                        resource_type="model",
                        exposures=["e1"],
                        node_name="model.package.name1",
                        description=None,
                    ),
                ],
            ),
        ],
    )
    def test_get_tables_from_metadata(self, data, kwargs, expected):
        assert expected == base_algo.get_tables_from_metadata(data=data, **kwargs)

    @pytest.mark.parametrize(
        "model_metadata, exposures, kwargs, expected",
        [
            (
                {
                    "node": {
                        "uniqueId": "model.package.name1",
                        "database": "db1",
                        "schema": "sc1",
                        "name": "name1",
                        "catalog": {},
                    }
                },
                [],
                dict(entity_name_format="resource.package.model"),
                Table(
                    name="model.package.name1",
                    node_name="model.package.name1",
                    database="db1",
                    schema="sc1",
                    columns=[
                        Column(name="unknown", data_type="unknown", description="")
                    ],
                    raw_sql=None,
                    description=None,
                ),
            ),
            (
                {
                    "node": {
                        "uniqueId": "model.package.name1",
                        "database": "db1",
                        "schema": "sc1",
                        "name": "name1",
                        "catalog": {"columns": [{"name": "col1"}]},
                    }
                },
                [],
                dict(entity_name_format="resource.package.model"),
                Table(
                    name="model.package.name1",
                    node_name="model.package.name1",
                    database="db1",
                    schema="sc1",
                    columns=[Column(name="col1", data_type="", description="")],
                    raw_sql=None,
                    description=None,
                ),
            ),
            (
                {
                    "node": {
                        "uniqueId": "model.package.name1",
                        "database": "db1",
                        "schema": "sc1",
                        "name": "name1",
                        "catalog": {
                            "columns": [
                                {"name": "col1", "type": "type1"},
                                {"name": "col2", "type": "type2"},
                            ]
                        },
                    }
                },
                [],
                dict(entity_name_format="resource.package.model"),
                Table(
                    name="model.package.name1",
                    node_name="model.package.name1",
                    database="db1",
                    schema="sc1",
                    columns=[
                        Column(name="col1", data_type="type1", description=""),
                        Column(name="col2", data_type="type2", description=""),
                    ],
                    raw_sql=None,
                    description=None,
                ),
            ),
            (
                {
                    "node": {
                        "uniqueId": "model.package.name1",
                        "database": "db1",
                        "schema": "sc1",
                        "name": "name1",
                        "catalog": None,
                    }
                },
                [],
                dict(entity_name_format="resource.package.model"),
                Table(
                    name="model.package.name1",
                    node_name="model.package.name1",
                    database="db1",
                    schema="sc1",
                    columns=[
                        Column(name="unknown", data_type="unknown", description=""),
                    ],
                    raw_sql=None,
                    description=None,
                ),
            ),
        ],
    )
    def test_get_table_from_metadata(self, model_metadata, exposures, kwargs, expected):
        assert expected == base_algo.get_table_from_metadata(
            model_metadata=model_metadata, exposures=exposures, **kwargs
        )

    @pytest.mark.parametrize(
        "data, kwargs, expected",
        [
            ([], dict(resource_type=["model", "source"]), []),
            (
                [{"exposures": {"edges": []}}],
                dict(resource_type=["model", "source"]),
                [],
            ),
            (
                [
                    {
                        "exposures": {
                            "edges": [
                                {
                                    "node": {
                                        "name": "ex1",
                                        "parents": [{"uniqueId": "model.x"}],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(resource_type=["model", "source"]),
                [dict(node_name="model.x", exposure_name="ex1")],
            ),
            (
                [
                    {
                        "exposures": {
                            "edges": [
                                {
                                    "node": {
                                        "name": "ex1",
                                        "parents": [
                                            {"uniqueId": "model.x"},
                                            {"uniqueId": "model.y"},
                                            {"uniqueId": "source.z"},
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(resource_type=["model"]),
                [
                    dict(node_name="model.x", exposure_name="ex1"),
                    dict(node_name="model.y", exposure_name="ex1"),
                ],
            ),
        ],
    )
    def test_get_node_exposures_from_metadata(self, data, kwargs, expected):
        assert expected == base_algo.get_node_exposures_from_metadata(
            data=data, **kwargs
        )

    @pytest.mark.parametrize(
        "data, kwargs, expected",
        [
            ([], dict(algo="test_relationship"), []),
            (
                [{"tests": {"edges": []}}],
                dict(algo="test_relationship", resource_type=["model", "source"]),
                [],
            ),
            (
                [
                    {
                        "tests": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "test.relationship_1",
                                        "testMetadata": {
                                            "kwargs": {
                                                "columnName": "coly",
                                                "to": 'ref("x")',
                                                "field": "colx",
                                            }
                                        },
                                        "parents": [],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(algo="test_relationship", resource_type=["model", "source"]),
                [
                    Ref(
                        name="test.relationship_1",
                        table_map=["", ""],
                        column_map=["colx", "coly"],
                        type="n1",
                    )
                ],
            ),
            (
                [
                    {
                        "tests": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "test.relationship_1",
                                        "meta": {},
                                        "testMetadata": {
                                            "kwargs": {
                                                "columnName": "coly",
                                                "to": 'ref("x")',
                                                "field": "colx",
                                            }
                                        },
                                        "parents": [
                                            {"uniqueId": "model.p.x"},
                                            {"uniqueId": "model.p.y"},
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(algo="test_relationship", resource_type=["model", "source"]),
                [
                    Ref(
                        name="test.relationship_1",
                        table_map=["model.p.x", "model.p.y"],
                        column_map=["colx", "coly"],
                        type="n1",
                    )
                ],
            ),
            (
                [
                    {
                        "tests": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "test.relationship_1",
                                        "meta": {},
                                        "testMetadata": {
                                            "kwargs": {
                                                "columnName": "coly",
                                                "to": 'ref("x")',
                                                "field": "colx",
                                            }
                                        },
                                        "parents": [
                                            {"uniqueId": "model.p.y"},
                                            {"uniqueId": "model.p.x"},
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(algo="test_relationship", resource_type=["model", "source"]),
                [
                    Ref(
                        name="test.relationship_1",
                        table_map=["model.p.x", "model.p.y"],
                        column_map=["colx", "coly"],
                        type="n1",
                    )
                ],
            ),
            (
                [
                    {
                        "tests": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "test.relationship_1",
                                        "meta": {},
                                        "testMetadata": {
                                            "kwargs": {
                                                "columnName": "coly",
                                                "to": 'ref("x")',
                                                "field": "colx",
                                            }
                                        },
                                        "parents": [
                                            {"uniqueId": "model.p.x"},
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(algo="test_relationship", resource_type=["model"]),
                [
                    Ref(
                        name="test.relationship_1",
                        table_map=["model.p.x", "model.p.x"],
                        column_map=["colx", "coly"],
                        type="n1",
                    )
                ],
            ),
        ],
    )
    def test_get_relationships_from_metadata(self, data, kwargs, expected):
        assert expected == base_algo.get_relationships_from_metadata(
            data=data, **kwargs
        )

    @pytest.mark.parametrize(
        "data, kwargs",
        [
            (
                [
                    {
                        "tests": {
                            "edges": [
                                {
                                    "node": {
                                        "uniqueId": "test.relationship_1",
                                        "meta": {},
                                        "testMetadata": {
                                            "kwargs": {
                                                "columnName": "coly",
                                                "to": 'ref("x")',
                                                "field": "colx",
                                            }
                                        },
                                        "parents": [
                                            {"uniqueId": "model.p.x"},
                                            {"uniqueId": "model.p.y"},
                                            {"uniqueId": "model.p.z"},
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ],
                dict(algo="test_relationship", resource_type=["model", "source"]),
            ),
        ],
    )
    def test_get_relationships_from_metadata_error(self, data, kwargs):
        with pytest.raises(click.BadParameter):
            base_algo.get_relationships_from_metadata(data=data, **kwargs)

    def test_find_related_nodes_by_id_not_supported_type(self):
        assert ["model.p.abc"] == test_relationship.find_related_nodes_by_id(
            manifest="irrelevant", type="metadata", node_unique_id="model.p.abc"
        )

    def test_find_related_nodes_by_id(self):
        assert sorted(["model.dbt_resto.table1", "model.dbt_resto.table2"]) == sorted(
            test_relationship.find_related_nodes_by_id(
                manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.table2"
            )
        )
        assert [
            "model.dbt_resto.not-exists"
        ] == test_relationship.find_related_nodes_by_id(
            manifest=DummyManifestRel(), node_unique_id="model.dbt_resto.not-exists"
        )
