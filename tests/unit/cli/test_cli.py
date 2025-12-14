import click

from dbterd.cli.main import dbterd


def _assert_commands_have_docstrings(commands: dict) -> None:
    """Helper to verify all commands have docstrings."""
    for command in commands.values():
        if isinstance(command, click.Command):
            assert command.__doc__ is not None


def _assert_unhidden_params_have_help(command: click.Command | click.Group) -> None:
    """Helper to verify unhidden params have help text, recursively."""
    for param in command.params:
        # arguments can't have help text
        if not isinstance(param, click.Argument) and not param.hidden:
            assert param.help is not None
    if isinstance(command, click.Group):
        for subcommand in command.commands.values():
            _assert_unhidden_params_have_help(subcommand)


class TestCLI:
    def test_commands_have_docstrings(self):
        _assert_commands_have_docstrings(dbterd.commands)

    def test_unhidden_params_have_help_texts(self):
        _assert_unhidden_params_have_help(dbterd)
