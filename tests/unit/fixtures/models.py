"""Model fixtures for Table, Column, and Ref objects."""

from __future__ import annotations

import pytest

from dbterd.core.models import Column, Ref, Table


# Common test data constants to reduce magic strings
class TestDefaults:
    """Default values used across tests for consistency."""

    DATABASE = "--database--"
    DATABASE2 = "--database2--"
    DATABASE3 = "--database3--"
    SCHEMA = "--schema--"
    SCHEMA2 = "--schema2--"
    SCHEMA3 = "--schema3--"
    RAW_SQL = "--irrelevant--"
    UNKNOWN_TYPE = "unknown"


# Helper functions for creating test objects (can be used in parametrized tests)
def make_column(
    name: str = "column1",
    data_type: str = "varchar",
    description: str = "",
) -> Column:
    """Create a Column object with sensible defaults."""
    return Column(name=name, data_type=data_type, description=description)


def make_table(
    name: str = "model.dbt_resto.table1",
    node_name: str | None = None,
    database: str = TestDefaults.DATABASE,
    schema: str = TestDefaults.SCHEMA,
    columns: list[Column] | None = None,
    raw_sql: str = TestDefaults.RAW_SQL,
    description: str = "",
    exposures: list[str] | None = None,
    label: str | None = None,
) -> Table:
    """Create a Table object with sensible defaults."""
    return Table(
        name=name,
        node_name=node_name or name,
        database=database,
        schema=schema,
        columns=columns or [make_column(name="name1", data_type="name1-type")],
        raw_sql=raw_sql,
        description=description,
        exposures=exposures or [],
        label=label,
    )


def make_ref(
    name: str = "test.dbt_resto.relationships_table1",
    table_map: list[str] | None = None,
    column_map: list[str] | None = None,
    ref_type: str = "n1",
    relationship_label: str | None = None,
) -> Ref:
    """Create a Ref object with sensible defaults."""
    return Ref(
        name=name,
        table_map=table_map or ["model.dbt_resto.table2", "model.dbt_resto.table1"],
        column_map=column_map or ["name2", "name1"],
        type=ref_type,
        relationship_label=relationship_label,
    )


# Pre-built common test objects for parametrized tests
def get_table1(columns: list[Column] | None = None) -> Table:
    """Get standard table1 for tests."""
    return make_table(
        name="model.dbt_resto.table1",
        columns=columns or [make_column(name="name1", data_type="name1-type")],
    )


def get_table2(columns: list[Column] | None = None) -> Table:
    """Get standard table2 for tests."""
    return make_table(
        name="model.dbt_resto.table2",
        database=TestDefaults.DATABASE2,
        schema=TestDefaults.SCHEMA2,
        columns=columns or [make_column(name="name2", data_type="name2-type2")],
    )


def get_table3_source(columns: list[Column] | None = None) -> Table:
    """Get standard source table3 for tests."""
    return make_table(
        name="source.dbt_resto.table3",
        database=TestDefaults.DATABASE3,
        schema=TestDefaults.SCHEMA3,
        columns=columns or [make_column(name="name3", data_type="name3-type3")],
    )


def get_basic_ref() -> Ref:
    """Get basic relationship between table1 and table2."""
    return make_ref()


def get_ref_with_missing_columns() -> Ref:
    """Get relationship referencing columns that don't exist initially."""
    return make_ref(column_map=["name-notexist2", "name-notexist1"])


@pytest.fixture
def column_factory():
    """Factory fixture to create Column objects with sensible defaults.

    Usage:
        def test_something(column_factory):
            col = column_factory(name="id", data_type="integer")
    """

    def _make_column(
        name: str = "column1",
        data_type: str = "varchar",
        description: str = "",
    ) -> Column:
        return Column(name=name, data_type=data_type, description=description)

    return _make_column


@pytest.fixture
def table_factory(column_factory):
    """Factory fixture to create Table objects with sensible defaults.

    Usage:
        def test_something(table_factory):
            table = table_factory(name="model.project.users")
    """

    def _make_table(
        name: str = "model.dbt_resto.table1",
        node_name: str | None = None,
        database: str = "--database--",
        schema: str = "--schema--",
        columns: list[Column] | None = None,
        raw_sql: str = "--irrelevant--",
        description: str = "",
        exposures: list[str] | None = None,
        label: str | None = None,
    ) -> Table:
        return Table(
            name=name,
            node_name=node_name or name,
            database=database,
            schema=schema,
            columns=columns or [column_factory(name="name1", data_type="name1-type")],
            raw_sql=raw_sql,
            description=description,
            exposures=exposures or [],
            label=label,
        )

    return _make_table


@pytest.fixture
def ref_factory():
    """Factory fixture to create Ref objects with sensible defaults.

    Usage:
        def test_something(ref_factory):
            ref = ref_factory(
                table_map=["model.project.orders", "model.project.users"],
                column_map=["user_id", "id"]
            )
    """

    def _make_ref(
        name: str = "test.dbt_resto.relationships_table1",
        table_map: list[str] | None = None,
        column_map: list[str] | None = None,
        ref_type: str = "n1",
        relationship_label: str | None = None,
    ) -> Ref:
        return Ref(
            name=name,
            table_map=table_map or ["model.dbt_resto.table2", "model.dbt_resto.table1"],
            column_map=column_map or ["name2", "name1"],
            type=ref_type,
            relationship_label=relationship_label,
        )

    return _make_ref


@pytest.fixture
def single_table(table_factory):
    """A single basic table for simple test cases."""
    return table_factory()


@pytest.fixture
def table1(table_factory, column_factory):
    """Standard table1 used in relationship tests."""
    return table_factory(
        name="model.dbt_resto.table1",
        columns=[column_factory(name="name1", data_type="name1-type")],
    )


@pytest.fixture
def table2(table_factory, column_factory):
    """Standard table2 used in relationship tests."""
    return table_factory(
        name="model.dbt_resto.table2",
        database="--database2--",
        schema="--schema2--",
        columns=[column_factory(name="name2", data_type="name2-type2")],
    )


@pytest.fixture
def table3_source(table_factory, column_factory):
    """Standard source table3 used in relationship tests."""
    return table_factory(
        name="source.dbt_resto.table3",
        database="--database3--",
        schema="--schema3--",
        columns=[column_factory(name="name3", data_type="name3-type3")],
    )


@pytest.fixture
def table1_with_enriched_columns(table_factory, column_factory):
    """Table1 with extra columns from relationship enrichment."""
    return table_factory(
        name="model.dbt_resto.table1",
        columns=[
            column_factory(name="name1", data_type="name1-type"),
            column_factory(name="name-notexist1", data_type="unknown"),
        ],
    )


@pytest.fixture
def table2_with_enriched_columns(table_factory, column_factory):
    """Table2 with extra columns from relationship enrichment."""
    return table_factory(
        name="model.dbt_resto.table2",
        database="--database2--",
        schema="--schema2--",
        columns=[
            column_factory(name="name2", data_type="name2-type2"),
            column_factory(name="name-notexist2", data_type="unknown"),
        ],
    )


@pytest.fixture
def basic_ref(ref_factory):
    """Basic relationship between table1 and table2."""
    return ref_factory()


@pytest.fixture
def ref_with_missing_columns(ref_factory):
    """Relationship referencing columns that don't exist initially."""
    return ref_factory(column_map=["name-notexist2", "name-notexist1"])
