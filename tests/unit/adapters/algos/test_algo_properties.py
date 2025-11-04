"""Test algorithm properties (name and description)."""

from dbterd.adapters.algos.semantic import SemanticAlgorithm
from dbterd.adapters.algos.test_relationship import TestRelationshipAlgorithm


class TestAlgoProperties:
    """Test all algorithm implementations have correct properties."""

    def test_test_relationship_properties(self):
        """Test TestRelationship algorithm properties."""
        algo = TestRelationshipAlgorithm()
        assert algo.name == "test_relationship"
        assert algo.description == "Detect relationships based on dbt test configurations"

    def test_semantic_properties(self):
        """Test Semantic algorithm properties."""
        algo = SemanticAlgorithm()
        assert algo.name == "semantic"
        assert algo.description == "Detect relationships based on dbt semantic entities"
