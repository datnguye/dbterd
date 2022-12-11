import click
from dbterd.helpers import jsonify
from dbterd.cli import params
from dbterd.adapters.worker import Worker


# dbterd
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.version_option()
@click.pass_context
def dbterd(ctx, **kwargs):
    """Tools for producing diagram-as-code"""


# dbterd debug
@dbterd.command(name="debug")
@click.pass_context
@params.common_params
def debug(ctx, **kwargs):
    """Inspect the hidden magics"""
    print(f"Arguments used: {kwargs}")
    print(f"Context used: {jsonify.to_json(ctx.obj)}")



# dbterd run
@dbterd.command(name="run")
@click.pass_context
@params.common_params
def run(ctx, **kwargs):
    """Run the convert"""
    Worker(ctx).run(**kwargs)
