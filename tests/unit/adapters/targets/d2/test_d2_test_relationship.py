from unittest import mock

import pytest

from dbterd.adapters.meta import Column, Ref, Table
from dbterd.adapters.targets.d2 import d2_test_relationship as engine


class TestD2TestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, expected",
        [
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    )
                ],
                [],
                [],
                [],
                ["model"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                    }
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="name2-type2")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="source.dbt_resto.table3",
                        database="--database3--",
                        schema="--schema3--",
                        columns=[Column(name="name3", data_type="name3-type3")],
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
                [],
                [],
                ["model", "source"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                        name-notexist1: unknown
                    }
                    "model.dbt_resto.table2": {
                        shape: sql_table
                        name2: name2-type2
                        name-notexist2: unknown
                    }
                    "source.dbt_resto.table3": {
                        shape: sql_table
                        name3: name3-type3
                    }
                    "model.dbt_resto.table1" -> "model.dbt_resto.table2": "name1 = name2"
                    "model.dbt_resto.table1" -> "model.dbt_resto.table2": "name-notexist1 = name-notexist2"
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="name2-type2")],
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
                ["schema:--schema--"],
                [],
                ["model", "source"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                    }
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    )
                ],
                [],
                [],
                ["model.dbt_resto.table1"],
                ["model"],
                """
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name2", data_type="name2-type")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                ["model.dbt_resto"],
                ["model.dbt_resto.table2"],
                ["model"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                    }
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                ["schema:", "wildcard:", ""],
                [],
                ["model"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                    }
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name2", data_type="name2-type")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                ["schema:--schema--,wildcard:*dbt_resto.table*"],
                ["wildcard:*table2"],
                ["model"],
                """
                    "model.dbt_resto.table1": {
                        shape: sql_table
                        name1: name1-type
                    }
                """,
            ),
        ],
    )
    def test_parse(
        self, tables, relationships, select, exclude, resource_type, expected
    ):
        with mock.patch(
            "dbterd.adapters.algos.base.get_tables",
            return_value=tables,
        ) as mock_get_tables:
            with mock.patch(
                "dbterd.adapters.algos.test_relationship.get_relationships",
                return_value=relationships,
            ) as mock_get_relationships:
                mermaid = engine.parse(
                    manifest="--manifest--",
                    catalog="--catalog--",
                    select=select,
                    exclude=exclude,
                    resource_type=resource_type,
                )
                print("mermaid ", mermaid.replace(" ", "").replace("\n", ""))
                print("expected", expected.replace(" ", "").replace("\n", ""))
                assert mermaid.replace(" ", "").replace("\n", "") == str(
                    expected
                ).replace(" ", "").replace("\n", "")
                mock_get_tables.assert_called_once()
                mock_get_relationships.assert_called_once()

    @pytest.mark.parametrize(
        "relationship_type, symbol",
        [
            ("0n", "->"),
            ("1n", "->"),
            ("01", "->"),
            ("11", "->"),
            ("nn", "->"),
            ("n1", "->"),
            ("--irrelevant--", "->"),
        ],
    )
    def test_get_rel_symbol(self, relationship_type, symbol):
        assert engine.get_rel_symbol(relationship_type=relationship_type) == symbol
