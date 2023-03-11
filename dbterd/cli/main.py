import importlib.metadata

import click

from dbterd.adapters.worker import DbtWorker
from dbterd.cli import params
from dbterd.helpers import jsonify
from dbterd.helpers.log import logger

__version__ = importlib.metadata.version("dbterd")


# dbterd
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.version_option(__version__)
@click.pass_context
def dbterd(ctx, **kwargs):
    """Tools for producing diagram-as-code"""
    logger.info(f"Run with dbterd=={__version__}")


# dbterd debug
@dbterd.command(name="debug")
@click.pass_context
@params.common_params
def debug(ctx, **kwargs):
    """Inspect the hidden magics"""
    logger.info("**Arguments used**")
    logger.debug(jsonify.to_json(kwargs))
    logger.info("**Context used**")
    logger.debug(jsonify.to_json(ctx.obj))


# dbterd run
@dbterd.command(name="run")
@click.pass_context
@params.common_params
def run(ctx, **kwargs):
    """Run the convert"""
    DbtWorker(ctx).run(**kwargs)
