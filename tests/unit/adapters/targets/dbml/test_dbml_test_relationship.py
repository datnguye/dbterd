import pytest

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.dbml import DbmlAdapter
from dbterd.core.models import Column, Ref, Table


class TestDbmlTestRelationship:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, omit_entity_name_quotes, expected",
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
                False,
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
                        column_map=(["name2"], ["name1"]),
                    ),
                    Ref(
                        name="test.dbt_resto.relationships_table1",
                        table_map=["model.dbt_resto.table2", "model.dbt_resto.table1"],
                        column_map=(["name-notexist2"], ["name-notexist1"]),
                    ),
                ],
                [],
                [],
                ["model", "source"],
                False,
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
                        column_map=(["name2"], ["name1"]),
                    )
                ],
                ["schema:--schema--"],
                [],
                ["model", "source"],
                False,
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
                False,
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
                False,
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
                False,
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
                False,
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
                False,
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
                False,
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table23" {
                    "name23" "name23-type"
                    Note:"model.dbt_resto.table23 description"
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
                    ),
                ],
                [],
                [],
                [],
                ["model"],
                True,
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table model.dbt_resto.table23 {
                    "name23" "name23-type"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                """,
            ),
        ],
    )
    def test_parse(
        self,
        tables,
        relationships,
        select,
        exclude,
        resource_type,
        omit_entity_name_quotes,
        expected,
    ):
        algo = TestRelationshipAlgo()
        adapter = DbmlAdapter()
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
        table_names = {table.name for table in enriched_tables}
        filtered_relationships = [
            rel for rel in relationships if all(table_name in table_names for table_name in rel.table_map)
        ]
        dbml = adapter.build_erd(
            tables=enriched_tables,
            relationships=filtered_relationships,
            omit_entity_name_quotes=omit_entity_name_quotes,
        )
        assert dbml.replace(" ", "").replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")


class TestDbmlTableGroup:
    @pytest.mark.parametrize(
        "tables, relationships, select, exclude, resource_type, omit_entity_name_quotes, entity_group, expected",
        [
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
                        database="--database--",
                        schema="--schema--",
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
                [],
                [],
                [],
                ["model", "source"],
                False,
                "database.schema",
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                    Note:""
                }
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table2" {
                    "name2" "--name2-type2--"
                    Note:""
                }
                //--configured at schema: --database3--.--schema3--
                Table "source.dbt_resto.table3" {
                    "name3" "--name3-type3--"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                //TableGroups (based on database.schema)
                TableGroup "--database--.--schema--" {
                    "model.dbt_resto.table1"
                    "model.dbt_resto.table2"
                }
                TableGroup "--database3--.--schema3--" {
                    "source.dbt_resto.table3"
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
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                [],
                [],
                ["model"],
                True,
                "database.schema",
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table model.dbt_resto.table1 {
                    "name1" "--name1-type--"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                //TableGroups (based on database.schema)
                TableGroup --database--.--schema-- {
                    model.dbt_resto.table1
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
                        columns=[Column(name="name1", data_type="--name1-type--")],
                        raw_sql="--irrelevant--",
                    ),
                    Table(
                        name="source.dbt_resto.table3",
                        node_name="source.dbt_resto.table3",
                        database="--database3--",
                        schema="--schema--",
                        columns=[Column(name="name3", data_type="--name3-type3--")],
                        raw_sql="--irrelevant--",
                    ),
                ],
                [],
                [],
                [],
                ["model", "source"],
                False,
                "schema",
                """//Tables (based on the selection criteria)
                //--configured at schema: --database--.--schema--
                Table "model.dbt_resto.table1" {
                    "name1" "--name1-type--"
                    Note:""
                }
                //--configured at schema: --database3--.--schema--
                Table "source.dbt_resto.table3" {
                    "name3" "--name3-type3--"
                    Note:""
                }
                //Refs (based on the DBT Relationship Tests)
                //TableGroups (based on schema)
                TableGroup "--schema--" {
                    "model.dbt_resto.table1"
                    "source.dbt_resto.table3"
                }
                """,
            ),
        ],
    )
    def test_parse_with_table_group(
        self,
        tables,
        relationships,
        select,
        exclude,
        resource_type,
        omit_entity_name_quotes,
        entity_group,
        expected,
    ):
        algo = TestRelationshipAlgo()
        adapter = DbmlAdapter()
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
        table_names = {table.name for table in enriched_tables}
        filtered_relationships = [
            rel for rel in relationships if all(table_name in table_names for table_name in rel.table_map)
        ]
        dbml = adapter.build_erd(
            tables=enriched_tables,
            relationships=filtered_relationships,
            omit_entity_name_quotes=omit_entity_name_quotes,
            entity_group=entity_group,
        )
        assert dbml.replace(" ", "").replace("\n", "") == str(expected).replace(" ", "").replace("\n", "")

    @pytest.mark.parametrize("entity_group", [None, ""])
    def test_no_table_group_when_unset(self, entity_group):
        """No TableGroup section is emitted when entity_group is unset/empty (default off)."""
        adapter = DbmlAdapter()
        tables = [
            Table(
                name="model.dbt_resto.table1",
                node_name="model.dbt_resto.table1",
                database="db",
                schema="public",
                columns=[Column(name="name1", data_type="int")],
            ),
        ]
        dbml = adapter.build_erd(tables=tables, relationships=[], entity_group=entity_group)
        assert "TableGroup" not in dbml


class TestFormatColumnRef:
    def setup_method(self):
        self.adapter = DbmlAdapter()

    def test_single_column(self):
        assert self.adapter._format_column_ref("orders", ["id"], '"') == '"orders"."id"'

    def test_composite_columns(self):
        assert self.adapter._format_column_ref("orders", ["org_id", "dept_id"], '"') == '"orders".("org_id", "dept_id")'

    def test_no_quote(self):
        assert self.adapter._format_column_ref("orders", ["id"], "") == 'orders."id"'


class TestFormatIndexesBlock:
    def setup_method(self):
        self.adapter = DbmlAdapter()

    def test_single_pk(self):
        result = self.adapter._format_indexes_block(["id"])
        assert result == "  indexes {\n    (id) [pk]\n  }\n"

    def test_composite_pk(self):
        result = self.adapter._format_indexes_block(["org_id", "dept_id"])
        assert result == "  indexes {\n    (org_id, dept_id) [pk]\n  }\n"


class TestDbmlCompositeFK:
    def test_composite_fk_rendered(self):
        """Composite FK column_map renders as table.(col1, col2) syntax."""
        adapter = DbmlAdapter()
        ref = Ref(
            name="test",
            table_map=["model.pkg.departments", "model.pkg.orders"],
            column_map=(["org_id", "dept_id"], ["org_id", "dept_id"]),
        )
        result = adapter.format_relationship(ref)
        assert result == 'Ref: "model.pkg.orders".("org_id", "dept_id") > "model.pkg.departments".("org_id", "dept_id")'

    def test_pk_indexes_block_rendered(self):
        """Table with is_primary_key columns emits an indexes block."""
        adapter = DbmlAdapter()
        table = Table(
            name="model.pkg.orders",
            node_name="model.pkg.orders",
            database="db",
            schema="public",
            columns=[
                Column(name="id", data_type="int", is_primary_key=True),
                Column(name="name", data_type="varchar"),
            ],
        )
        result = adapter.format_table(table)
        assert "indexes {" in result
        assert "(id) [pk]" in result
        assert "name" in result  # non-PK column still present

    def test_composite_pk_indexes_block(self):
        """Table with composite PK emits correct indexes block."""
        adapter = DbmlAdapter()
        table = Table(
            name="model.pkg.segments",
            node_name="model.pkg.segments",
            database="db",
            schema="public",
            columns=[
                Column(name="customer_id", data_type="int", is_primary_key=True),
                Column(name="segment_code", data_type="varchar", is_primary_key=True),
            ],
        )
        result = adapter.format_table(table)
        assert "(customer_id, segment_code) [pk]" in result

    def test_no_pk_no_indexes_block(self):
        """Table without PK columns emits no indexes block."""
        adapter = DbmlAdapter()
        table = Table(
            name="model.pkg.t1",
            node_name="model.pkg.t1",
            database="db",
            schema="public",
            columns=[Column(name="name", data_type="varchar")],
        )
        result = adapter.format_table(table)
        assert "indexes" not in result
