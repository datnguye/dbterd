"""Tests for external adapter entry point discovery in _register_adapters."""

from unittest import mock

from dbterd.core.executor import _register_adapters


class TestRegisterAdaptersEntryPoints:
    @mock.patch("dbterd.core.executor.importlib.metadata.entry_points")
    @mock.patch("dbterd.core.executor.pkgutil.iter_modules", return_value=[])
    def test_loads_external_entry_points(self, mock_iter_modules, mock_entry_points):
        mock_ep = mock.Mock()
        mock_ep.name = "snowflake_ddl"
        mock_entry_points.return_value = [mock_ep]

        _register_adapters()

        mock_entry_points.assert_called_once_with(group="dbterd.adapters")
        mock_ep.load.assert_called_once()

    @mock.patch("dbterd.core.executor.importlib.metadata.entry_points")
    @mock.patch("dbterd.core.executor.pkgutil.iter_modules", return_value=[])
    def test_handles_entry_point_load_failure_gracefully(self, mock_iter_modules, mock_entry_points):
        mock_ep = mock.Mock()
        mock_ep.name = "broken_adapter"
        mock_ep.load.side_effect = ImportError("module not found")
        mock_entry_points.return_value = [mock_ep]

        with mock.patch("dbterd.core.executor.logger") as mock_logger:
            _register_adapters()

        mock_ep.load.assert_called_once()
        mock_logger.warning.assert_called_once_with(
            "Failed to load external adapter entry point '%s'", "broken_adapter"
        )

    @mock.patch("dbterd.core.executor.importlib.metadata.entry_points")
    @mock.patch("dbterd.core.executor.pkgutil.iter_modules", return_value=[])
    def test_no_external_entry_points(self, mock_iter_modules, mock_entry_points):
        mock_entry_points.return_value = []

        _register_adapters()

        mock_entry_points.assert_called_once_with(group="dbterd.adapters")
