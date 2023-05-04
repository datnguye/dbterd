from dataclasses import dataclass
from unittest import mock
from unittest.mock import MagicMock

import pytest

from dbterd.adapters.algos import base as base_algo
from dbterd.adapters.algos import test_relationship as algo
from dbterd.adapters.algos.meta import Column, Ref, Table


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
class ManifestNode:
    test_metadata: ManifestNodeTestMetaData
    meta: dict
    columns: dict
    raw_sql: str = ""
    database: str = ""
    schema_: str = ""


@dataclass
class ManifestNodeColumn:
    name: str
    data_type: str = "unknown"
    description: str = ""


@dataclass
class DummyManifestRel:
    parent_map = dict(
        {
            "test.dbt_resto.relationships_table1": ["table2", "table1"],
            "test.dbt_resto.relationships_table2": ["table2", "table1"],
            "test.dbt_resto.relationships_table3": ["tabley", "tablex"],
            "test.dbt_resto.relationships_tablex": ["y", "x"],
            "test.dbt_resto.foreign_key_table1": ["table2", "table1"],
        }
    )
    nodes = {
        "test.dbt_resto.relationships_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2"}
            ),
            meta={},
            columns={},
        ),
        "test.dbt_resto.relationships_table2": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2"}
            ),
            meta={},
            columns={},
        ),
        "test.dbt_resto.relationships_table3": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2"}
            ),
            meta={},
            columns={},
        ),
        "test.dbt_resto.relationships_tablex": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "x", "field": "y"}
            ),
            meta={"ignore_in_erd": 1},
            columns={},
        ),
        "test.dbt_resto.foreign_key_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "pk_column_name": "f2"}
            ),
            meta={},
            columns={},
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
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table_dummy_columns",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column()],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
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
            assert base_algo.get_tables(manifest, catalog) == expected
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
                        table_map=["table2", "table1"],
                        column_map=["f2", "f1"],
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table3",
                        table_map=["tabley", "tablex"],
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
                        table_map=["table2", "table1"],
                        column_map=["f2", "f1"],
                    ),
                ],
            ),
            (MagicMock(return_value={"parent_map": [], "nodes": {}}), None, []),
        ],
    )
    def test_get_relationships(self, manifest, algorithm, expected):
        assert algo.get_relationships(manifest=manifest, algo=algorithm) == expected
