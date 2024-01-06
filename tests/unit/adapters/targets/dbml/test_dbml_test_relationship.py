from unittest import mock

import pytest

from dbterd.adapters.meta import Column, Ref, Table
from dbterd.adapters.targets.dbml import dbml_test_relationship as engine


class TestDbmlTestRelationship:
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
                        columns=[
                            Column(
                                name="name1",
                                data_type="--name1-type--",
                                description="column name 1",
                            )
                        ],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                [],
                [],
                ["model"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--" [note: "column name 1"]
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
            (
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
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[Column(name="name2", data_type="--name2-type2--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="source.dbt_resto.table3",
                        node_name="source.dbt_resto.table3",
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
                [],
                [],
                ["model", "source"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                    "name-notexist1" "unknown"
                    Note:""
                }
                //--configured at schema: --database2--.--schema2--
                Table "model.dbt_resto.table2" {
                    "name2" "--name2-type2--"
                    "name-notexist2" "unknown"
                    Note:""
                }
                //--configured at schema: --database3--.--schema3--
                Table "source.dbt_resto.table3" {
                    "name3" "--name3-type3--"
                    Note:""
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
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
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
                ["schema:--schema--"],
                [],
                ["model", "source"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    )
                ],
                [],
                [],
                ["model.dbt_resto.table1"],
                ["model"],
                """//Tables (based on the selection criteria)
                //Refs (based on the DBT Relationship Tests)
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
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "name1-type"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
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
                        name="model.dbt_resto.view2",
                        node_name="model.dbt_resto.view2",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name2", data_type="name2-type")],
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
                [],
                ["wildcard:*.table*"],
                [],
                ["model", "source"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "name1-type"
                    Note:""
                }
                //--configured at schema: --database3--.--schema3--
                Table "source.dbt_resto.table3" {
                    "name3" "name3-type3"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
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
                        exposures=["dummy1"],
                    )
                ],
                [],
                ["exposure:dummy1", "exposure:"],
                [],
                ["model"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "name1-type"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
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
                        exposures=["dummy1"],
                    ),
                    Table(
                        name="model.dbt_resto.table23",
                        node_name="model.dbt_resto.table23",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name23", data_type="name23-type")],
                        raw_sql="--irrelevant--",
                        exposures=["dummy2", "dummy3"],
                    ),
                ],
                [],
                ["exposure:dummy2"],
                [],
                ["model"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table23" {
                    "name23" "name23-type"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
            (
                [
                    Table(
                        name="model.dbt_resto.table23",
                        node_name="model.dbt_resto.table23",
                        database="--database--",
                        schema="--schema--",
                        columns=[Column(name="name23", data_type="name23-type")],
                        raw_sql="--irrelevant--",
                        exposures=["dummy2", "dummy3"],
                        description="model.dbt_resto.table23 description",
                    ),
                ],
                [],
                ["exposure:dummy2"],
                [],
                ["model"],
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table23" {
                    "name23" "name23-type"
                    Note:"model.dbt_resto.table23 description"
                }
                //Refs (based on the DBT Relationship Tests)
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
                dbml = engine.parse(
                    manifest="--manifest--",
                    catalog="--catalog--",
                    select=select,
                    exclude=exclude,
                    resource_type=resource_type,
                )
                assert dbml.replace(" ", "").replace("\n", "") == str(expected).replace(
                    " ", ""
                ).replace("\n", "")
                mock_get_tables.assert_called_once()
                mock_get_relationships.assert_called_once()

    @pytest.mark.parametrize(
        "relationship_type, symbol",
        [
            ("0n", "<"),
            ("1n", "<"),
            ("01", "-"),
            ("11", "-"),
            ("nn", "<>"),
            ("n1", ">"),
            ("--irrelevant--", ">"),
        ],
    )
    def test_get_rel_symbol(self, relationship_type, symbol):
        assert engine.get_rel_symbol(relationship_type=relationship_type) == symbol
