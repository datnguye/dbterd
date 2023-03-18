import click

from dbterd.cli.main import dbterd


class TestCLI:
    def test_commands_have_docstrings(self):
        def run_test(commands):
            for command in commands.values():
                if type(command) is click.Command:
                    assert command.__doc__ is not None

        run_test(dbterd.commands)

    def test_unhidden_params_have_help_texts(self):
        def run_test(command):
            for param in command.params:
                # arguments can't have help text
                if not isinstance(param, click.Argument) and not param.hidden:
                    assert param.help is not None
            if type(command) is click.Group:
                for command in command.commands.values():
                    run_test(command)

        run_test(dbterd)
