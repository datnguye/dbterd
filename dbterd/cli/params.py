import functools

import click

from dbterd import default


def common_params(func):
    @click.option(
        "--artifacts-dir",
        "-ad",
        help="Specified the path to dbt artifact directory which known as /target directory",
        default="",
        type=click.STRING,
    )
    @click.option(
        "--output",
        "-o",
        help="Output the result file. Default to the cwd/target",
        default=default.default_output_path(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--select",
        "-s",
        help="Selecttion criteria",
        default=[],
        multiple=True,
        type=click.STRING,
    )
    @click.option(
        "--exclude",
        "-ns",
        help="Exclusion criteria",
        default=[],
        multiple=True,
        type=click.STRING,
    )
    @click.option(
        "--target",
        "-t",
        help="Target to the diagram-as-code platform",
        default=default.default_target(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--algo",
        "-a",
        help="Specified algorithm in the way to detect diagram connectors",
        default=default.deafult_algo(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--manifest-version",
        "-mv",
        help="Specified dbt manifest.json version",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--catalog-version",
        "-cv",
        help="Specified dbt catalog.json version",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--resource-type",
        "-rt",
        help="Specified dbt resource type(seed, model, source, snapshot),default:model, use examples, -rt model -rt source",
        default=["model"],
        multiple=True,
        type=click.STRING,
    )
    @click.option(
        "--dbt",
        help="Flag to indicate the Selecton to follow dbt's one leveraging Programmatic Invocation",
        is_flag=True,
        default=False,
        show_default=True,
    )
    @click.option(
        "--dbt-project-dir",
        "-dpd",
        help="Specified dbt project directory path",
        default="",
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--dbt-target",
        "-dt",
        help="Specified dbt target name",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--dbt-auto-artifacts",
        help="Flag to force generating dbt artifact files leveraging Programmatic Invocation",
        is_flag=True,
        default=False,
        show_default=True,
    )
    @click.option(
        "--entity-name-format",
        "-enf",
        help="Specified the format of the entity node's name",
        default="resource.package.model",
        show_default=True,
        type=click.STRING,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper
