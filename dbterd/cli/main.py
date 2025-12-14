import importlib.metadata
from pathlib import Path

import click

from dbterd.cli import params
from dbterd.cli.config import ConfigError, get_yaml_template, load_config
from dbterd.constants import CONFIG_FILE_DBTERD_YML
from dbterd.core.executor import Executor
from dbterd.helpers import jsonify
from dbterd.helpers.log import logger


__version__ = importlib.metadata.version("dbterd")


# Programmatic invocation
class DbterdRunner:
    """Support runner for the programmatic call."""

    def __init__(self) -> None:
        pass

    def invoke(self, args: list[str]):
        """
        Invoke a command of dbterd programmatically.

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
            raise Exception(f"unhandled exit code {e!s}") from e
        except (click.NoSuchOption, click.UsageError) as e:
            raise Exception(e.message) from e


# dbterd
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.version_option(__version__)
@click.pass_context
def dbterd(ctx):
    """Tools for producing diagram-as-code."""
    logger.info(f"Run with dbterd=={__version__}")

    # Load configuration file and set as default_map
    # This allows CLI arguments to override config file values
    ctx.ensure_object(dict)
    try:
        config = load_config()
        if config:
            ctx.default_map = ctx.default_map or {}
            # Apply config to all subcommands
            for command_name in ctx.command.commands:
                if command_name not in ctx.default_map:
                    ctx.default_map[command_name] = {}
                ctx.default_map[command_name].update(config)
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        raise click.ClickException(str(e)) from e


# dbterd run
@dbterd.command(name="run")
@click.pass_context
@params.run_params
def run(ctx, **kwargs):
    """
    Generate ERD file from reading dbt artifact files,
    optionally downloading from Administrative API (dbt Cloud) before hands.
    """
    Executor(ctx).run(**kwargs)


# dbterd run_metadata
@dbterd.command(name="run-metadata")
@click.pass_context
@params.run_metadata_params
def run_metadata(ctx, **kwargs):
    """Generate ERD file from reading Discovery API (dbt Cloud)."""
    Executor(ctx).run_metadata(**kwargs)


# dbterd debug
@dbterd.command(name="debug")
@click.pass_context
@params.debug_params
def debugx(ctx, **kwargs):
    """Inspect the hidden magics."""
    logger.info("**Arguments used**")
    logger.debug(jsonify.to_json(kwargs))
    logger.info("**Arguments evaluated**")
    logger.debug(jsonify.to_json(Executor(ctx).evaluate_kwargs(**kwargs)))


# dbterd init
@dbterd.command(name="init")
@params.init_params
def init(template: str, force: bool):
    """Initialize a dbterd configuration file.

    Creates .dbterd.yml with common parameters and helpful comments.
    For pyproject.toml configuration, manually add [tool.dbterd] section.

    Use --template to choose between dbt-core and dbt-cloud configurations.
    """
    config_path = Path.cwd() / CONFIG_FILE_DBTERD_YML
    config_content = get_yaml_template(template_type=template)

    if config_path.exists() and not force:
        logger.error(f"Configuration file already exists: {config_path}. Use --force to overwrite.")
        raise click.ClickException("Configuration file already exists")

    # Write configuration file
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        logger.info(f"Created configuration file: {config_path} | Template type: {template}")
    except OSError as e:
        logger.error(f"Failed to create configuration file: {e}")
        raise click.ClickException(f"Failed to create configuration file: {e}") from e
