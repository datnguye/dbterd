from dataclasses import dataclass
from unittest import mock

import pytest

from dbterd.adapters.algos.meta import Column, Ref, Table
from dbterd.adapters.targets.dbml import dbml_test_relationship as engine


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


@dataclass
class DummyManifestRel:
    parent_map = dict(
        {
            "test.dbt_resto.relationships_table1": ["table2", "table1"],
            "test.dbt_resto.relationships_table2": ["table2", "table1"],
            "test.dbt_resto.relationships_table3": ["tabley", "tablex"],
            "test.dbt_resto.relationships_tablex": ["y", "x"],
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


class TestDbmlTestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, expected",
        [
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    )
                ],
                [],
                "",
                None,
                ["model"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="--name2-type2--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="source.dbt_resto.table3",
                        database="--database3--",
                        schema="--schema3--",
                        columns=[Column(name="name3", data_type="--name3-type3--")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["name2", "name1"],
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["name-notexist2", "name-notexist1"],
                    ),
                ],
                "",
                None,
                ["model", "source"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                    "name-notexist1" "unknown"
                }
                //--configured at schema: --database2--.--schema2--
                Table "model.dbt_resto.table2" {
                    "name2" "--name2-type2--"
                    "name-notexist2" "unknown"
                }
                //--configured at schema: --database3--.--schema3--
                Table "source.dbt_resto.table3" {
                    "name3" "--name3-type3--"
                }
                //Refs (based on the DBT Relationship Tests)
                Ref: "model.dbt_resto.table1"."name1" > "model.dbt_resto.table2"."name2"
                Ref: "model.dbt_resto.table1"."name-notexist1" > "model.dbt_resto.table2"."name-notexist2"
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="--name2-type2--")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["name2", "name1"],
                    )
                ],
                "schema:--schema--",
                None,
                ["model", "source"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    )
                ],
                [],
                "",
                "model.dbt_resto.table1",
                ["model"],
                """//Tables (based on the selection criteria)
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
        ],
    )
    def test_parse(
        self, tables, relationships, select, exclude, resource_type, expected
    ):
        with mock.patch(
            "dbterd.adapters.algos.test_relationship.get_tables",
            return_value=tables,
        ) as mock_get_tables:
            with mock.patch(
                "dbterd.adapters.algos.test_relationship.get_relationships",
                return_value=relationships,
            ) as mock_get_relationships:
                dbml = engine.parse(
                    manifest="--manifest--",
                    catalog="--catalog--",
                    select=select,
                    exclude=exclude,
                    resource_type=resource_type,
                )
                print("dbml    ", dbml.replace(" ", "").replace("\n", ""))
                print("expected", expected.replace(" ", "").replace("\n", ""))
                assert dbml.replace(" ", "").replace("\n", "") == str(expected).replace(
                    " ", ""
                ).replace("\n", "")
                mock_get_tables.assert_called_once()
                mock_get_relationships.assert_called_once()
