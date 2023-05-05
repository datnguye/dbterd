from unittest import mock

import pytest

from dbterd.adapters.algos.meta import Column, Ref, Table
from dbterd.adapters.targets.graphviz import graphviz_test_relationship as engine


class TestGraphVizTestRelationship:
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type ) name1</td></tr>
                            </table>> ];
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type) name1</td></tr>
                            <tr><td align="left">(unknown) name-notexist1</td></tr>
                            </table>> ];
                    "model.dbt_resto.table2" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table2</font></td></tr>
                            <tr><td align="left">(name2-type2) name2</td></tr>
                            <tr><td align="left">(unknown) name-notexist2</td></tr>
                            </table>> ];
                    "source.dbt_resto.table3" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">source.dbt_resto.table3</font></td></tr>
                            <tr><td align="left">(name3-type3) name3</td></tr>
                            </table>> ];
                    "model.dbt_resto.table1" -> "model.dbt_resto.table2" [
                        penwidth = 1
                        fontsize = 12
                        fontcolor = "black"
                        label = "name1 = name2"
                    ];
                    "model.dbt_resto.table1" -> "model.dbt_resto.table2" [
                        penwidth = 1
                        fontsize = 12
                        fontcolor = "black"
                        label = "name-notexist1 = name-notexist2"
                    ];
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type) name1</td></tr>
                            </table>> ];
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
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
                ["model.dbt_resto"],
                ["model.dbt_resto.table2"],
                ["model"],
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type) name1</td></tr>
                            </table>> ];
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type) name1</td></tr>
                            </table>> ];
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
                """digraph g {
                    fontname="Helvetica,Arial,sans-serif"
                    node [fontname="Helvetica,Arial,sans-serif"]
                    edge [fontname="Helvetica,Arial,sans-serif"]
                    graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
                    ratio=auto;
                    "model.dbt_resto.table1" [
                        style = "filled, bold"
                        penwidth = 1
                        fillcolor = "white"
                        fontname = "Courier New"
                        shape = "Mrecord"
                        label =<
                            <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                            <tr><td bgcolor="black" align="center" colspan="2">
                            <font color="white">model.dbt_resto.table1</font></td></tr>
                            <tr><td align="left">(name1-type) name1</td></tr>
                            </table>> ];
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
                graphviz = engine.parse(
                    manifest="--manifest--",
                    catalog="--catalog--",
                    select=select,
                    exclude=exclude,
                    resource_type=resource_type,
                )
                print("graphviz ", graphviz.replace(" ", "").replace("\n", ""))
                print("expected", expected.replace(" ", "").replace("\n", ""))
                assert graphviz.replace(" ", "").replace("\n", "") == str(
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
