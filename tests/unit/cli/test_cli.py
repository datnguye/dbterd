"""Tests for CLI commands and parameters."""

from dbterd.cli.main import dbterd
from tests.unit.fixtures.cli import (
    assert_commands_have_docstrings,
    assert_unhidden_params_have_help,
)


class TestCLI:
    def test_commands_have_docstrings(self):
        assert_commands_have_docstrings(dbterd.commands)

    def test_unhidden_params_have_help_texts(self):
        assert_unhidden_params_have_help(dbterd)
