from unittest import mock

from dbterd.adapters.algos import semantic
from dbterd.adapters.meta import SemanticEntity


class TestSemanticExtended:
    def test_get_relationships_from_metadata_with_none_data(self):
        """Test _get_relationships_from_metadata with None data parameter"""
        # Test with None data
        result = semantic._get_relationships_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    def test_get_linked_semantic_entities_from_metadata_with_none_data(self):
        """Test _get_linked_semantic_entities_from_metadata with None data"""
        result = semantic._get_linked_semantic_entities_from_metadata(data=None)
        assert isinstance(result, list)
        assert result == []

    def test_get_semantic_entities_from_metadata_with_none_data(self):
        """Test _get_semantic_entities_from_metadata with None data"""
        result = semantic._get_semantic_entities_from_metadata(data=None)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == []  # FK list should be empty
        assert result[1] == []  # PK list should be empty

    def test_find_related_nodes_by_id_with_metadata_type(self):
        """Test find_related_nodes_by_id with metadata type parameter"""
        # When type is "metadata", should just return the input node_unique_id in a list
        node_id = "model.pkg.test_model"
        result = semantic.find_related_nodes_by_id(manifest={}, node_unique_id=node_id, type="metadata")
        assert result == [node_id]

    @mock.patch("dbterd.adapters.algos.semantic._get_linked_semantic_entities")
    def test_find_related_nodes_by_id_with_linked_entities(self, mock_get_linked_entities):
        """Test find_related_nodes_by_id with linked entities"""
        # Mock the _get_linked_semantic_entities function to return some entities
        mock_get_linked_entities.return_value = [
            (
                SemanticEntity(
                    semantic_model="sm1",
                    model="model.pkg.test_model_fk",
                    entity_name="entity1",
                    entity_type="foreign",
                    column_name="id",
                    relationship_type="",
                ),
                SemanticEntity(
                    semantic_model="sm1",
                    model="model.pkg.test_model_pk",
                    entity_name="entity1",
                    entity_type="primary",
                    column_name="id",
                    relationship_type="",
                ),
            )
        ]

        # Check when the node_unique_id matches the primary model
        result = semantic.find_related_nodes_by_id(manifest={}, node_unique_id="model.pkg.test_model_pk")
        assert sorted(result) == sorted(["model.pkg.test_model_pk", "model.pkg.test_model_fk"])

        # Check when the node_unique_id matches the foreign model
        result = semantic.find_related_nodes_by_id(manifest={}, node_unique_id="model.pkg.test_model_fk")
        assert sorted(result) == sorted(["model.pkg.test_model_fk", "model.pkg.test_model_pk"])

        # Check when the node_unique_id doesn't match either model
        result = semantic.find_related_nodes_by_id(manifest={}, node_unique_id="model.pkg.other_model")
        assert result == ["model.pkg.other_model"]
