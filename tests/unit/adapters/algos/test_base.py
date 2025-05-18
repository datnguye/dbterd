from unittest import mock

from dbterd.adapters.algos import base
from dbterd.adapters.meta import Ref, Table


class TestAlgoBase:
    def test_get_tables_from_metadata_with_none_data(self):
        """Test that get_tables_from_metadata handles None data by initializing an empty list"""
        result = base.get_tables_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    @mock.patch("dbterd.adapters.algos.base.get_table_name", return_value="test_table")
    def test_get_table_from_metadata_with_none_exposures(self, mock_get_table_name):
        """Test that get_table_from_metadata handles None exposures by initializing an empty list"""
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
        result = base.get_table_from_metadata(model_metadata=model_metadata, exposures=None, entity_name_format="test")
        assert isinstance(result, Table)
        assert result.exposures == []

    @mock.patch("dbterd.adapters.algos.base.get_table_name", return_value="test_table")
    @mock.patch("dbterd.adapters.algos.base.get_compiled_sql", return_value="SELECT * FROM test")
    def test_get_table_with_none_exposures(self, mock_get_compiled_sql, mock_get_table_name):
        """Test that get_table handles None exposures by initializing an empty list"""
        manifest_node = mock.MagicMock()
        manifest_node.database = "test_db"
        manifest_node.schema_ = "test_schema"
        manifest_node.identifier = "test_identifier"
        manifest_node.columns = {}
        manifest_node.description = "test description"

        result = base.get_table(
            node_name="model.package.model_name", manifest_node=manifest_node, exposures=None, entity_name_format="test"
        )
        assert isinstance(result, Table)
        assert result.exposures == []

    def test_get_node_exposures_from_metadata_with_none_data(self):
        """Test that get_node_exposures_from_metadata handles None data by initializing an empty list"""
        result = base.get_node_exposures_from_metadata(data=None, resource_type=["model"])
        assert isinstance(result, list)
        assert result == []

    def test_get_relationships_from_metadata_with_none_data(self):
        """Test that get_relationships_from_metadata handles None data by initializing an empty list"""
        result = base.get_relationships_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    def test_make_up_relationships_with_none_params(self):
        """Test that make_up_relationships handles None parameters by initializing empty lists"""
        # Test with None tables, None relationships
        result = base.make_up_relationships(relationships=None, tables=None)
        assert isinstance(result, list)
        assert result == []

        # Test with None tables, list relationships
        relationships = [
            Ref(name="ref1", table_map=("model.pkg.table1", "model.pkg.table2"), column_map=("col1", "col2"), type="")
        ]
        result = base.make_up_relationships(relationships=relationships, tables=None)
        assert isinstance(result, list)
        assert result == []

    def test_get_unique_refs_with_none_refs(self):
        """Test that get_unique_refs handles None refs by initializing an empty list"""
        result = base.get_unique_refs(refs=None)
        assert isinstance(result, list)
        assert result == []
