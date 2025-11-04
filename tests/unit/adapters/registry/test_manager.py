from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dbterd.core.registry.manager import RegistryManager


class MockAlgorithm:
    """Mock algorithm for testing."""

    def name(self) -> str:
        return "mock_algo"


class MockTarget:
    """Mock target for testing."""

    def name(self) -> str:
        return "mock_target"


class TestRegistryManager:
    def test_initialize_only_once(self):
        """Test that initialize only runs once."""
        manager = RegistryManager()
        manager.initialize()
        assert manager._initialized is True

        # Second call should not re-initialize
        with patch.object(manager, "_auto_discover_parsers") as mock_parsers:
            manager.initialize()
            mock_parsers.assert_not_called()

    def test_get_parser_initializes_if_needed(self):
        """Test get_parser initializes if not already initialized."""
        manager = RegistryManager()
        assert manager._initialized is False

        # This should trigger initialization
        with pytest.raises(KeyError):
            manager.get_parser("nonexistent")

        assert manager._initialized is True

    def test_get_target_initializes_if_needed(self):
        """Test get_target initializes if not already initialized."""
        manager = RegistryManager()
        assert manager._initialized is False

        # This should trigger initialization
        with pytest.raises(KeyError):
            manager.get_target("nonexistent")

        assert manager._initialized is True

    def test_list_parsers_initializes_if_needed(self):
        """Test list_parsers initializes if not already initialized."""
        manager = RegistryManager()
        assert manager._initialized is False

        parsers = manager.list_parsers()
        assert manager._initialized is True
        assert isinstance(parsers, list)

    def test_list_targets_initializes_if_needed(self):
        """Test list_targets initializes if not already initialized."""
        manager = RegistryManager()
        assert manager._initialized is False

        targets = manager.list_targets()
        assert manager._initialized is True
        assert isinstance(targets, list)

    def test_register_parser(self):
        """Test registering a parser."""
        manager = RegistryManager()

        class TestAlgo:
            @property
            def name(self) -> str:
                return "test"

            @property
            def description(self) -> str:
                return "test"

            def parse(self, *args, **kwargs):
                return []

            def parse_metadata(self, *args, **kwargs):
                return []

            def find_related_nodes_by_id(self, *args, **kwargs):
                return []

        manager.register_parser("test_algo", TestAlgo)
        # Should not raise an error

    def test_register_target(self):
        """Test registering a target."""
        manager = RegistryManager()

        class TestTarget:
            @property
            def name(self) -> str:
                return "test"

            @property
            def file_extension(self) -> str:
                return ".txt"

            def run(self, *args, **kwargs):
                return "result"

        manager.register_target("test_target", TestTarget)
        # Should not raise an error

    def test_discover_algorithms_with_no_file(self):
        """Test _discover_algorithms when package.__file__ is None."""
        manager = RegistryManager()

        with patch("dbterd.core.registry.manager.importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.__file__ = None
            mock_import.return_value = mock_module

            result = manager._discover_algorithms("test.package")
            assert result == {}

    def test_discover_algorithms_with_import_error_in_module(self):
        """Test _discover_algorithms when a specific module within the package fails to import."""
        manager = RegistryManager()

        # Mock a package with a valid file
        mock_package = Mock()
        mock_package.__file__ = str(Path(__file__).parent / "test_package" / "__init__.py")

        # Create a mock file that will be discovered
        mock_file = Mock()
        mock_file.stem = "broken_algo"

        call_count = [0]

        with (
            patch("dbterd.core.registry.manager.importlib.import_module") as mock_import,
            patch.object(Path, "glob") as mock_glob,
        ):
            mock_glob.return_value = [mock_file]

            def import_side_effect(name):
                call_count[0] += 1
                if call_count[0] == 1:  # First call is for the package
                    return mock_package
                else:  # Subsequent calls are for individual modules
                    raise ImportError(f"Cannot import {name}")

            mock_import.side_effect = import_side_effect

            result = manager._discover_algorithms("test.package")
            # Should return empty dict because all module imports failed
            assert result == {}
            # Verify import was attempted multiple times
            assert mock_import.call_count >= 2

    def test_discover_targets_with_no_file(self):
        """Test _discover_targets when package.__file__ is None."""
        manager = RegistryManager()

        with patch("dbterd.core.registry.manager.importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.__file__ = None
            mock_import.return_value = mock_module

            result = manager._discover_targets("test.package")
            assert result == {}

    def test_discover_targets_with_import_error_in_module(self):
        """Test _discover_targets when a specific module within the package fails to import."""
        manager = RegistryManager()

        # Mock a package with a valid file
        mock_package = Mock()
        mock_package.__file__ = str(Path(__file__).parent / "test_package" / "__init__.py")

        # Create a mock file that will be discovered
        mock_file = Mock()
        mock_file.stem = "broken_target"

        call_count = [0]

        with (
            patch("dbterd.core.registry.manager.importlib.import_module") as mock_import,
            patch.object(Path, "glob") as mock_glob,
        ):
            mock_glob.return_value = [mock_file]

            def import_side_effect(name):
                call_count[0] += 1
                if call_count[0] == 1:  # First call is for the package
                    return mock_package
                else:  # Subsequent calls are for individual modules
                    raise ImportError(f"Cannot import {name}")

            mock_import.side_effect = import_side_effect

            result = manager._discover_targets("test.package")
            # Should return empty dict because all module imports failed
            assert result == {}
            # Verify import was attempted multiple times
            assert mock_import.call_count >= 2

    def test_discover_algorithms_with_package_import_error(self):
        """Test _discover_algorithms when the package itself fails to import."""
        manager = RegistryManager()

        with patch("dbterd.core.registry.manager.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Package not found")

            result = manager._discover_algorithms("nonexistent.package")
            assert result == {}

    def test_discover_targets_with_package_import_error(self):
        """Test _discover_targets when the package itself fails to import."""
        manager = RegistryManager()

        with patch("dbterd.core.registry.manager.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Package not found")

            result = manager._discover_targets("nonexistent.package")
            assert result == {}
