from dataclasses import dataclass

import pytest

from dbterd.adapters.targets.dbml.engine import engine


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
class DummyManifestRel:
    parent_map = dict({"test.dbt_resto.relationships_table1": ["table1", "table2"]})
    nodes = [
        {
            "test.dbt_resto.relationships_table1": dict(
                {"test_metadata": dict({"field": "f1", "column_name": "f1"})}
            )
        }
    ]


class TestDbmlEngine:
    @pytest.mark.parametrize(
        "manifest, expected",
        [
            (DummyManifestV6(), "compiled_sql"),
            (DummyManifestV7(), "compiled_code"),
            (DummyManifestError(), "raw_sql"),
            (
                DummyManifestHasColumns(),
                """select
                col1,
                col2
                from database_dummy.schema_dummy.undefined
                """,
            ),
        ],
    )
    def test_get_compiled(self, manifest, expected):
        assert engine.get_compiled_sql(manifest_node=manifest).replace(" ", "").replace(
            "\n", ""
        ) == str(expected).replace(" ", "").replace("\n", "")

    # @pytest.mark.parametrize(
    #     "manifest, expected",
    #     [
    #         (DummyManifestRel(), [])
    #     ]
    # )
    # def test_get_relationships(self, manifest, expected):
    #     assert engine.get_relationships(manifest) == expected
