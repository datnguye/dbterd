"""Tests for the main module."""

from unittest import mock

from dbterd import main


@mock.patch("dbterd.cli.main.dbterd")
def test_main(mock_dbterd):
    """Test that main calls the CLI dbterd function."""
    main.main()
    mock_dbterd.assert_called_once()
