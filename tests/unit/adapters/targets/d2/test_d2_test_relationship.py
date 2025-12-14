import pytest

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.d2 import D2Adapter
from dbterd.core.models import Column, Ref, Table


class TestD2TestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, expected",
        [
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
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
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="name2-type2")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="source.dbt_resto.table3",
                        node_name="source.dbt_resto.table3",
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
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
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
                        node_name="model.dbt_resto.table1",
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
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
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
                        node_name="model.dbt_resto.table1",
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
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
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
    def test_parse(self, tables, relationships, select, exclude, resource_type, expected):
        algo = TestRelationshipAlgo()
        # Apply filtering and enrichment as the algorithm does
        filtered_tables = algo.filter_tables_based_on_selection(
            tables=tables,
            select=select,
            exclude=exclude,
            resource_type=resource_type,
        )
        enriched_tables = algo.enrich_tables_from_relationships(
            tables=filtered_tables,
            relationships=relationships,
        )

        # Filter relationships to only include those between filtered tables
        filtered_table_names = {table.name for table in enriched_tables}
        filtered_relationships = [
            rel for rel in relationships if all(table_name in filtered_table_names for table_name in rel.table_map)
        ]

        adapter = D2Adapter()
        d2_output = adapter.build_erd(tables=enriched_tables, relationships=filtered_relationships)
        print("d2_output ", d2_output.replace(" ", "").replace("\n", ""))
        print("expected", expected.replace(" ", "").replace("\n", ""))
        assert d2_output.replace(" ", "").replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")
