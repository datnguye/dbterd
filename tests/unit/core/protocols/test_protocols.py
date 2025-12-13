"""Tests for protocol interface definitions."""

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.dbml import DbmlAdapter
from dbterd.core.protocols.algo_adapter import AlgoAdapter
from dbterd.core.protocols.target_adapter import TargetAdapter


class TestProtocols:
    def test_algo_adapter_protocol_compliance(self):
        """Test that TestRelationshipAlgo implements AlgoAdapter protocol."""
        algo = TestRelationshipAlgo()
        # Verify the algo has all required protocol methods
        assert hasattr(algo, "parse")
        assert hasattr(algo, "parse_metadata")
        assert hasattr(algo, "find_related_nodes_by_id")
        assert callable(algo.parse)
        assert callable(algo.parse_metadata)
        assert callable(algo.find_related_nodes_by_id)

    def test_target_adapter_protocol_compliance(self):
        """Test that DbmlAdapter implements key TargetAdapter protocol methods."""
        adapter = DbmlAdapter()
        # Verify the adapter has required protocol methods
        assert hasattr(adapter, "run")
        assert hasattr(adapter, "get_rel_symbol")
        assert hasattr(adapter, "build_erd")
        assert callable(adapter.run)
        assert callable(adapter.get_rel_symbol)
        assert callable(adapter.build_erd)

    def test_algo_adapter_protocol_defines_interface(self):
        """Test that AlgoAdapter protocol defines required interface methods."""
        assert hasattr(AlgoAdapter, "parse")
        assert hasattr(AlgoAdapter, "parse_metadata")
        assert hasattr(AlgoAdapter, "find_related_nodes_by_id")
        # Verify it's runtime checkable
        assert hasattr(AlgoAdapter, "__protocol_attrs__") or hasattr(AlgoAdapter, "_is_protocol")

    def test_target_adapter_protocol_defines_interface(self):
        """Test that TargetAdapter protocol defines required interface methods."""
        assert hasattr(TargetAdapter, "run")
        assert hasattr(TargetAdapter, "parse")
        assert hasattr(TargetAdapter, "get_rel_symbol")
        assert hasattr(TargetAdapter, "build_erd")
        # Verify it's runtime checkable
        assert hasattr(TargetAdapter, "__protocol_attrs__") or hasattr(TargetAdapter, "_is_protocol")

    def test_target_adapter_has_required_attributes(self):
        """Test that concrete adapters define required class attributes."""
        adapter = DbmlAdapter()
        assert hasattr(adapter, "file_extension")
        assert hasattr(adapter, "default_filename")
        assert adapter.file_extension == ".dbml"
        assert adapter.default_filename == "output.dbml"

    def test_algo_adapter_isinstance_check(self):
        """Test isinstance check with AlgoAdapter protocol."""
        algo = TestRelationshipAlgo()
        # Protocol isinstance checks method presence
        assert isinstance(algo, AlgoAdapter)
