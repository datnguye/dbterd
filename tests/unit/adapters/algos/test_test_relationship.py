from dataclasses import dataclass, field
from unittest import mock
from unittest.mock import MagicMock

import pytest

from dbterd.adapters.algos import base as base_algo
from dbterd.adapters.algos import test_relationship as algo
from dbterd.adapters.meta import Column, Ref, Table


@dataclass
class DummyManifestV6:
    compiled_sql: str = "compiled_sql"


@dataclass
class DummyManifestV7:
    compiled_code: str = "compiled_code"


@dataclass
class DummyManifestError:
    raw_sql: str = "raw_sql"


@dataclass
class DummyManifestHasColumns:
    columns = dict({"col1": None, "col2": None})
    database = "database_dummy"
    schema = "schema_dummy"


@dataclass
class ManifestNodeTestMetaData:
    kwargs: dict


@dataclass
class ManifestNodeDependsOn:
    nodes: list = field(default_factory=list)


@dataclass
class ManifestNode:
    test_metadata: ManifestNodeTestMetaData
    meta: dict
    columns: dict
    raw_sql: str = ""
    database: str = ""
    schema_: str = ""
    depends_on: ManifestNodeDependsOn = field(default_factory=ManifestNodeDependsOn)


@dataclass
class ManifestExposureNode:
    depends_on: ManifestNodeDependsOn


@dataclass
class ManifestNodeColumn:
    name: str
    data_type: str = "unknown"
    description: str = ""


@dataclass
class DummyManifestRel:
    nodes = {
        "test.dbt_resto.relationships_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table2": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table3": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('tabley')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.tabley", "model.dbt_resto.tablex"]
            ),
        ),
        "test.dbt_resto.relationships_tablex": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "x", "field": "y", "to": "ref('y')"}
            ),
            meta={"ignore_in_erd": 1},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.y", "model.dbt_resto.x"]
            ),
        ),
        "test.dbt_resto.foreign_key_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={
                    "column_name": "f1",
                    "pk_column_name": "f2",
                    "pk_table_name": "ref('table2')",
                }
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table4": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table-m2')"}
            ),
            meta={"relationship_type": "one-to-one"},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table-m2", "model.dbt_resto.table-m1"]
            ),
        ),
        "test.dbt_resto.relationships_table1_reverse": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table-r2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table-r1", "model.dbt_resto.table-r2"]
            ),
        ),
    }


@dataclass
class DummyManifestTable:
    nodes = {
        "model.dbt_resto.table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql--",
            database="--database--",
            schema_="--schema--",
            columns={},
        ),
        "model.dbt_resto.table_dummy_columns": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql--",
            database="--database--",
            schema_="--schema--",
            columns={},
        ),
        "model.dbt_resto.table2": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql2--",
            database="--database2--",
            schema_="--schema2--",
            columns={
                "name2": ManifestNodeColumn(name="name2"),
                "name3": ManifestNodeColumn(name="name3"),
            },
        ),
    }
    sources = {
        "source.dummy.source_table": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            database="--database--",
            schema_="--schema--",
            columns={
                "name1": ManifestNodeColumn(name="name1"),
                "name2": ManifestNodeColumn(name="name2"),
            },
        ),
    }


@dataclass
class DummyManifestWithExposure:
    exposures = {
        "exposure.dbt_resto.dummy": ManifestExposureNode(
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table1", "model.dbt_resto.table2"]
            ),
        )
    }


@dataclass
class CatalogNode:
    columns: dict


@dataclass
class CatalogNodeColumn:
    type: str
    comment: str = ""


@dataclass
class DummyCatalogTable:
    nodes = {
        "model.dbt_resto.table1": CatalogNode(
            columns={"name1": CatalogNodeColumn(type="--name1-type--")}
        ),
        "model.dbt_resto.table2": CatalogNode(
            columns={"name3": CatalogNodeColumn(type="--name3-type--")}
        ),
    }
    sources = {
        "source.dummy.source_table": CatalogNode(
            columns={"name1": CatalogNodeColumn(type="--name1-type--")}
        ),
    }


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
                    ),
                    Table(
                        name="model.dbt_resto.table_dummy_columns",
                        node_name="model.dbt_resto.table_dummy_columns",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column()],
                        raw_sql="--irrelevant--",
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
        assert algo.get_relationships(manifest=manifest, algo=algorithm) == expected

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
        assert algo.get_relationship_type(meta=meta) == type

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
