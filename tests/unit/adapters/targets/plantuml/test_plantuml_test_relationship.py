import pytest

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.plantuml import PlantumlAdapter
from dbterd.core.models import Column, Ref, Table


class TestPlantUMLTestRelationship:
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                    }
                @enduml
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                        name-notexist1 : unknown
                    }
                    entity "model.dbt_resto.table2" {
                        name2 : name2-type2
                        name-notexist2: unknown
                    }
                    entity "source.dbt_resto.table3" {
                        name3 : name3-type3
                    }
                    "model.dbt_resto.table1" }|--|| "model.dbt_resto.table2"
                @enduml
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                    }
                @enduml
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
                """@startuml
                @enduml
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                    }
                @enduml
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                    }
                @enduml
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
                """@startuml
                    entity "model.dbt_resto.table1" {
                        name1 : name1-type
                    }
                @enduml
                """,
            ),
        ],
    )
    def test_parse(self, tables, relationships, select, exclude, resource_type, expected):
        algo = TestRelationshipAlgo()
        # Apply filtering and enrichment as done in the algorithm
        filtered_tables = algo.filter_tables_based_on_selection(
            tables=tables,
            select=select,
            exclude=exclude,
            resource_type=resource_type,
        )
        enriched_relationships = algo.make_up_relationships(
            relationships=relationships,
            tables=filtered_tables,
        )
        enriched_tables = algo.enrich_tables_from_relationships(
            tables=filtered_tables,
            relationships=enriched_relationships,
        )

        # Build ERD using the adapter
        adapter = PlantumlAdapter()
        plantuml = adapter.build_erd(
            tables=enriched_tables,
            relationships=enriched_relationships,
        )
        print("plantuml ", plantuml.replace(" ", "").replace("\n", ""))
        print("expected", expected.replace(" ", "").replace("\n", ""))
        assert plantuml.replace(" ", "").replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")
