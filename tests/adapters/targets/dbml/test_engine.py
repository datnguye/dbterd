from dbterd.adapters.targets.dbml.engine import engine


class DummyManifestV6:
    compiled_sql: str = "compiled_sql"


class DummyManifestV7:
    compiled_code: str = "compiled_code"


class DummyManifestError:
    raw_sql: str = "raw_sql"


class DummyManifestHasColumns:
    columns = dict(
        {
            "col1": dict({"data_type": "col1dt"}),
            "col2": dict({"data_type": "col2dt"}),
        }
    )
    database = "database_dummy"
    schema = "schema_dummy"


class TestDbmlEngine:
    def test_get_compiled_sql_v6(self):
        node = DummyManifestV6()
        assert engine.get_compiled_sql(manifest_node=node) == "compiled_sql"

    def test_get_compiled_sql_v7(self):
        node = DummyManifestV7()
        assert engine.get_compiled_sql(manifest_node=node) == "compiled_code"

    def test_get_compiled_error(self):
        node = DummyManifestError()
        assert engine.get_compiled_sql(manifest_node=node) == "raw_sql"

    # def test_get_compiled_has_columns(self):
    #     node = DummyManifestHasColumns()
    #     assert engine.get_compiled_sql(manifest_node=node) != "raw_sql"