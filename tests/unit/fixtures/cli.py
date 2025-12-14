"""CLI test helper fixtures and utilities."""

from typing import Union

import click
import pytest


def assert_commands_have_docstrings(commands: dict) -> None:
    """Helper to verify all commands have docstrings."""
    for command in commands.values():
        if isinstance(command, click.Command):
            assert command.__doc__ is not None


def assert_unhidden_params_have_help(command: Union[click.Command, click.Group]) -> None:
    """Helper to verify unhidden params have help text, recursively."""
    for param in command.params:
        # arguments can't have help text
        if not isinstance(param, click.Argument) and not param.hidden:
            assert param.help is not None
    if isinstance(command, click.Group):
        for subcommand in command.commands.values():
            assert_unhidden_params_have_help(subcommand)


@pytest.fixture
def cli_docstring_checker():
    """Fixture that returns the docstring checker function."""
    return assert_commands_have_docstrings


@pytest.fixture
def cli_help_text_checker():
    """Fixture that returns the help text checker function."""
    return assert_unhidden_params_have_help
