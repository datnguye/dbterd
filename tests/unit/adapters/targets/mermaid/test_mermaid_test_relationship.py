import pytest

from dbterd.adapters.targets.mermaid import MermaidAdapter
from dbterd.core.models import Column, Ref, Table


class TestMermaidTestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, omit_columns, expected",
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
                False,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1" {
                      name1-type name1
                  }
                """,
            ),
            # Test with multiple tables and relationships (enriched columns from algo adapter)
            (
                [
                    Table(
                        name="model.dbt_resto.table1",
                        node_name="model.dbt_resto.table1",
                        database="--database--",
                        schema="--schema--",
                        columns=[
                            Column(name="name1", data_type="name1-type"),
                            Column(name="name-notexist1", data_type="unknown"),
                        ],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[
                            Column(name="name2", data_type="name2-type2"),
                            Column(name="name-notexist2", data_type="unknown"),
                        ],
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
                False,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1" {
                      name1-type name1
                      unknown name-notexist1
                  }
                  "MODEL.DBT_RESTO.TABLE2" {
                    name2-type2 name2
                    unknown name-notexist2
                  }
                  "SOURCE.DBT_RESTO.TABLE3" {
                    name3-type3 name3
                  }
                  "MODEL.DBT_RESTO.TABLE1" }|--|| "MODEL.DBT_RESTO.TABLE2": name2--name1
                  "MODEL.DBT_RESTO.TABLE1" }|--|| "MODEL.DBT_RESTO.TABLE2": name-notexist2--name-notexist1
                """,
            ),
            # Test with single table (simulates filtering to only table1)
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
                [],
                [],
                ["model"],
                False,
                """erDiagram
                    "MODEL.DBT_RESTO.TABLE1" {
                        name1-type name1
                    }
                """,
            ),
            # Test with empty tables (simulates all tables excluded)
            (
                [],
                [],
                [],
                [],
                ["model"],
                False,
                """erDiagram
                """,
            ),
            # Test with single table (simulates select/exclude filtering)
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
                [],
                [],
                ["model"],
                False,
                """erDiagram
                    "MODEL.DBT_RESTO.TABLE1" {
                        name1-type name1
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
                False,
                """erDiagram
                    "MODEL.DBT_RESTO.TABLE1" {
                        name1-type name1
                    }
                """,
            ),
            # Test with single table (simulates wildcard filtering)
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
                [],
                [],
                ["model"],
                False,
                """erDiagram
                    "MODEL.DBT_RESTO.TABLE1" {
                        name1-type name1
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
                [],
                ["model"],
                True,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1" {
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
                        columns=[Column(name="name1.first_name", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[
                            Column(name="name2.first_name", data_type="name2-type2"),
                            Column(
                                name="complex_struct",
                                data_type="Struct<field1 string, field2 string>",
                            ),
                        ],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["name2.first_name", "name1.first_name"],
                    ),
                ],
                [],
                [],
                ["model", "source"],
                False,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1" {
                      name1-type name1__first_name
                  }
                  "MODEL.DBT_RESTO.TABLE2" {
                    name2-type2 name2__first_name
                    Struct[OMITTED] complex_struct
                  }
                  "MODEL.DBT_RESTO.TABLE1" }|--|| "MODEL.DBT_RESTO.TABLE2": name2__first_name--name1__first_name
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
                        label="table1",
                    )
                ],
                [],
                [],
                [],
                ["model"],
                False,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1"["TABLE1"] {
                      name1-type name1
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
                        columns=[Column(name="name1.first_name", data_type="name1-type")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="model.dbt_resto.table2",
                        node_name="model.dbt_resto.table2",
                        database="--database2--",
                        schema="--schema2--",
                        columns=[
                            Column(name="name2.first_name", data_type="name2-type2"),
                            Column(
                                name="complex_struct",
                                data_type="Struct<field1 string, field2 string>",
                            ),
                        ],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=["name2.first_name", "name1.first_name"],
                        relationship_label="Preferred_Relationship_Name",
                    ),
                ],
                [],
                [],
                ["model", "source"],
                False,
                """erDiagram
                  "MODEL.DBT_RESTO.TABLE1" {
                      name1-type name1__first_name
                  }
                  "MODEL.DBT_RESTO.TABLE2" {
                    name2-type2 name2__first_name
                    Struct[OMITTED] complex_struct
                  }
                  "MODEL.DBT_RESTO.TABLE1" }|--|| "MODEL.DBT_RESTO.TABLE2": Preferred_Relationship_Name
                """,
            ),
        ],
    )
    def test_build_erd(
        self,
        tables,
        relationships,
        select,
        exclude,
        resource_type,
        omit_columns,
        expected,
    ):
        adapter = MermaidAdapter()
        mermaid = adapter.build_erd(
            tables=tables,
            relationships=relationships,
            omit_columns=omit_columns,
        )
        print("mermaid ", mermaid.replace(" ", "").replace("\n", ""))
        print("expected", expected.replace(" ", "").replace("\n", ""))
        assert mermaid.replace(" ", "").replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")

    @pytest.mark.parametrize(
        "relationship_type, symbol",
        [
            ("0n", "}o--|{"),
            ("1n", "||--|{"),
            ("01", "}o--||"),
            ("11", "||--||"),
            ("nn", "}|--|{"),
            ("n1", "}|--||"),
            ("--irrelevant--", "}|--||"),
        ],
    )
    def test_get_rel_symbol(self, relationship_type, symbol):
        adapter = MermaidAdapter()
        assert adapter.get_rel_symbol(relationship_type=relationship_type) == symbol
