"""Tests for plugin registry."""

import pytest

from dbterd.core.registry.plugin_registry import PluginRegistry


class DummyTargetAdapter:
    """Dummy target adapter for testing."""

    file_extension = ".dummy"
    default_filename = "output.dummy"


class DummyAlgoAdapter:
    """Dummy algo adapter for testing."""

    pass


class TestPluginRegistry:
    def test_has_target_returns_true_for_registered(self):
        """Test has_target returns True for registered targets."""
        assert PluginRegistry.has_target("dbml") is True
        assert PluginRegistry.has_target("mermaid") is True

    def test_has_target_returns_false_for_unregistered(self):
        """Test has_target returns False for unregistered targets."""
        assert PluginRegistry.has_target("nonexistent_target") is False

    def test_has_algo_returns_true_for_registered(self):
        """Test has_algo returns True for registered algorithms."""
        assert PluginRegistry.has_algo("test_relationship") is True
        assert PluginRegistry.has_algo("semantic") is True

    def test_has_algo_returns_false_for_unregistered(self):
        """Test has_algo returns False for unregistered algorithms."""
        assert PluginRegistry.has_algo("nonexistent_algo") is False

    def test_list_targets_returns_registered_targets(self):
        """Test list_targets returns list of registered target names."""
        targets = PluginRegistry.list_targets()
        assert isinstance(targets, list)
        assert "dbml" in targets
        assert "mermaid" in targets

    def test_list_algos_returns_registered_algos(self):
        """Test list_algos returns list of registered algorithm names."""
        algos = PluginRegistry.list_algos()
        assert isinstance(algos, list)
        assert "test_relationship" in algos
        assert "semantic" in algos

    def test_get_target_info_returns_plugin_info(self):
        """Test get_target_info returns PluginInfo for registered target."""
        info = PluginRegistry.get_target_info("dbml")
        assert info.name == "dbml"
        assert info.adapter_class is not None

    def test_get_target_info_raises_for_unregistered(self):
        """Test get_target_info raises KeyError for unregistered target."""
        with pytest.raises(KeyError) as exc_info:
            PluginRegistry.get_target_info("nonexistent_target")
        assert "Target 'nonexistent_target' not registered" in str(exc_info.value)

    def test_get_algo_info_returns_plugin_info(self):
        """Test get_algo_info returns PluginInfo for registered algorithm."""
        info = PluginRegistry.get_algo_info("test_relationship")
        assert info.name == "test_relationship"
        assert info.adapter_class is not None

    def test_get_algo_info_raises_for_unregistered(self):
        """Test get_algo_info raises KeyError for unregistered algorithm."""
        with pytest.raises(KeyError) as exc_info:
            PluginRegistry.get_algo_info("nonexistent_algo")
        assert "Algo 'nonexistent_algo' not registered" in str(exc_info.value)

    def test_register_and_clear(self):
        """Test register methods and clear functionality."""
        # Store original state
        original_targets = PluginRegistry._targets.copy()
        original_algos = PluginRegistry._algos.copy()

        try:
            # Register new adapters
            PluginRegistry.register_target("test_target", DummyTargetAdapter, "Test target")
            PluginRegistry.register_algo("test_algo", DummyAlgoAdapter, "Test algo")

            # Verify they're registered
            assert PluginRegistry.has_target("test_target")
            assert PluginRegistry.has_algo("test_algo")

            # Clear registry
            PluginRegistry.clear()

            # Verify registry is empty
            assert len(PluginRegistry._targets) == 0
            assert len(PluginRegistry._algos) == 0

        finally:
            # Restore original state
            PluginRegistry._targets = original_targets
            PluginRegistry._algos = original_algos
