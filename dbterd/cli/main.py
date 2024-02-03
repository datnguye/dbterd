import importlib.metadata
from typing import List

import click

from dbterd.adapters.base import Executor
from dbterd.cli import params
from dbterd.helpers import jsonify
from dbterd.helpers.log import logger

__version__ = importlib.metadata.version("dbterd")


# Programmatic invocation
class dbterdRunner:
    """Support runner for the programatic call"""

    def __init__(self) -> None:
        pass

    def invoke(self, args: List[str]):
        """Invoke a command of dbterd programatically

        Args:
            args (List[str]): dbterd arguments

        Raises:
            Exception: Unhandled exception
            Exception: Not Supported command exception
        """
        try:
            dbt_ctx = dbterd.make_context(dbterd.name, args)
            return dbterd.invoke(dbt_ctx)
        except click.exceptions.Exit as e:
            # 0 exit code, expected for --version early exit
            if str(e) == "0":
                return [], True
            raise Exception(f"unhandled exit code {str(e)}")
        except (click.NoSuchOption, click.UsageError) as e:
            raise Exception(e.message)


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


# dbterd run
@dbterd.command(name="run")
@click.pass_context
@params.run_params
def run(ctx, **kwargs):
    """
    Generate ERD file from reading dbt artifact files,
    optionally downloading from Administrative API (dbt Cloud) befor hands
    """
    Executor(ctx).run(**kwargs)


# dbterd run_metadata
@dbterd.command(name="run-metadata")
@click.pass_context
@params.run_metadata_params
def run_metadata(ctx, **kwargs):
    """Generate ERD file from reading Discovery API (dbt Cloud)"""
    Executor(ctx).run_metadata(**kwargs)


# dbterd debug
@dbterd.command(name="debug")
@click.pass_context
@params.run_params
@params.run_metadata_params
def debugx(ctx, **kwargs):
    """Inspect the hidden magics"""
    logger.info("**Arguments used**")
    logger.debug(jsonify.to_json(kwargs))
    logger.info("**Arguments evaluated**")
    logger.debug(jsonify.to_json(Executor(ctx).evaluate_kwargs(**kwargs)))
