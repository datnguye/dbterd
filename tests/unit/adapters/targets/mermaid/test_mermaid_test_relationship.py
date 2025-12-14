import pytest

from dbterd.adapters.targets.mermaid import MermaidAdapter
from tests.unit.fixtures.models import (
    TestDefaults,
    get_basic_ref,
    get_ref_with_missing_columns,
    get_table1,
    get_table2,
    get_table3_source,
    make_column,
    make_ref,
    make_table,
)


class TestMermaidTestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, omit_columns, expected",
        [
            # Test with single table
            (
                [get_table1()],
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
                    get_table1(
                        columns=[
                            make_column(name="name1", data_type="name1-type"),
                            make_column(name="name-notexist1", data_type=TestDefaults.UNKNOWN_TYPE),
                        ]
                    ),
                    get_table2(
                        columns=[
                            make_column(name="name2", data_type="name2-type2"),
                            make_column(name="name-notexist2", data_type=TestDefaults.UNKNOWN_TYPE),
                        ]
                    ),
                    get_table3_source(),
                ],
                [get_basic_ref(), get_ref_with_missing_columns()],
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
                [get_table1()],
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
                [get_table1()],
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
            # Test with empty select filters
            (
                [get_table1()],
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
                [get_table1()],
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
            # Test with omit_columns=True
            (
                [get_table1()],
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
            # Test with nested column names and complex struct types
            (
                [
                    make_table(
                        name="model.dbt_resto.table1",
                        columns=[make_column(name="name1.first_name", data_type="name1-type")],
                    ),
                    make_table(
                        name="model.dbt_resto.table2",
                        database=TestDefaults.DATABASE2,
                        schema=TestDefaults.SCHEMA2,
                        columns=[
                            make_column(name="name2.first_name", data_type="name2-type2"),
                            make_column(name="complex_struct", data_type="Struct<field1 string, field2 string>"),
                        ],
                    ),
                ],
                [
                    make_ref(
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
            # Test with table label
            (
                [make_table(name="model.dbt_resto.table1", label="table1")],
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
            # Test with relationship label
            (
                [
                    make_table(
                        name="model.dbt_resto.table1",
                        columns=[make_column(name="name1.first_name", data_type="name1-type")],
                    ),
                    make_table(
                        name="model.dbt_resto.table2",
                        database=TestDefaults.DATABASE2,
                        schema=TestDefaults.SCHEMA2,
                        columns=[
                            make_column(name="name2.first_name", data_type="name2-type2"),
                            make_column(name="complex_struct", data_type="Struct<field1 string, field2 string>"),
                        ],
                    ),
                ],
                [
                    make_ref(
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
