from unittest import mock

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgorithm
from dbterd.core.meta import Column, Ref, Table


class TestAlgoBase:
    def setup_method(self):
        """Set up test algorithm instance."""
        self.algo = TestRelationshipAlgorithm()

    def test_get_tables_from_metadata_with_none_data(self):
        """Test that get_tables_from_metadata handles None data by initializing an empty list."""
        result = self.algo.get_tables_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    @mock.patch.object(TestRelationshipAlgorithm, "get_table_name", return_value="test_table")
    def test_get_table_from_metadata_with_none_exposures(self, mock_get_table_name):
        """Test that get_table_from_metadata handles None exposures by initializing an empty list."""
        model_metadata = {
            "node": {
                "uniqueId": "model.package.model_name",
                "description": "test description",
                "database": "test_db",
                "schema": "test_schema",
                "alias": "test_alias",
                "name": "test_name",
                "catalog": {},
            }
        }
        result = self.algo.get_table_from_metadata(
            model_metadata=model_metadata, exposures=None, entity_name_format="test"
        )
        assert isinstance(result, Table)
        assert result.exposures == []

    @mock.patch.object(TestRelationshipAlgorithm, "get_table_name", return_value="test_table")
    @mock.patch.object(TestRelationshipAlgorithm, "get_compiled_sql", return_value="SELECT * FROM test")
    def test_get_table_with_none_exposures(self, mock_get_compiled_sql, mock_get_table_name):
        """Test that get_table handles None exposures by initializing an empty list."""
        manifest_node = mock.MagicMock()
        manifest_node.database = "test_db"
        manifest_node.schema_ = "test_schema"
        manifest_node.identifier = "test_identifier"
        manifest_node.columns = {}
        manifest_node.description = "test description"
        manifest_node.meta = {}

        result = self.algo.get_table(
            node_name="model.package.model_name", manifest_node=manifest_node, exposures=None, entity_name_format="test"
        )
        assert isinstance(result, Table)
        assert result.exposures == []

    def test_get_node_exposures_from_metadata_with_none_data(self):
        """Test that get_node_exposures_from_metadata handles None data by initializing an empty list."""
        result = self.algo.get_node_exposures_from_metadata(data=None, resource_type=["model"])
        assert isinstance(result, list)
        assert result == []

    def test_get_relationships_from_metadata_with_none_data(self):
        """Test that get_relationships_from_metadata handles None data by initializing an empty list."""
        result = self.algo.get_relationships_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    def test_make_up_relationships_with_none_params(self):
        """Test that make_up_relationships handles None parameters by initializing empty lists."""
        # Test with None tables, None relationships
        result = self.algo.make_up_relationships(relationships=None, tables=None)
        assert isinstance(result, list)
        assert result == []

        # Test with None tables, list relationships
        relationships = [
            Ref(name="ref1", table_map=("model.pkg.table1", "model.pkg.table2"), column_map=("col1", "col2"), type="")
        ]
        result = self.algo.make_up_relationships(relationships=relationships, tables=None)
        assert isinstance(result, list)
        assert result == []

    def test_get_unique_refs_with_none_refs(self):
        """Test that get_unique_refs handles None refs by initializing an empty list."""
        result = self.algo.get_unique_refs(refs=None)
        assert isinstance(result, list)
        assert result == []

    def test_enrich_tables_from_relationships_adds_missing_columns(self):
        """Test that enrich_tables_from_relationships adds missing columns from relationships."""
        # Create tables with some columns
        tables = [
            Table(
                name="model.pkg.table1",
                node_name="model.pkg.table1",
                database="db",
                schema="schema",
                columns=[Column(name="existing_col", data_type="string")],
                raw_sql="",
            ),
            Table(
                name="model.pkg.table2",
                node_name="model.pkg.table2",
                database="db",
                schema="schema",
                columns=[Column(name="EXISTING_COL2", data_type="string")],  # Uppercase to test case-insensitive check
                raw_sql="",
            ),
        ]

        # Create relationships that reference columns not in tables
        relationships = [
            Ref(
                name="ref1",
                table_map=("model.pkg.table1", "model.pkg.table2"),
                column_map=("new_col1", "new_col2"),  # These columns don't exist
                type="",
            )
        ]

        result = self.algo.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        # Verify the new columns were added
        assert len(result[0].columns) == 2  # existing_col + new_col1
        assert any(col.name == "new_col1" for col in result[0].columns)
        assert len(result[1].columns) == 2  # EXISTING_COL2 + new_col2
        assert any(col.name == "new_col2" for col in result[1].columns)

        # Verify original tables are not modified (deep copy)
        assert len(tables[0].columns) == 1
        assert len(tables[1].columns) == 1
