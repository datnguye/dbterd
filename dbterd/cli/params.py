import functools
import click
from dbterd import default


def common_params(func):
    @click.option(
        "--manifest-path",
        "-mp",
        help="Specified the full path to dbt manifest.json file",
        default=default.default_manifest_path(),
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
        "--target",
        "-t",
        help="Target to the diagram-as-code platform",
        default=default.default_target(),
        type=click.STRING,
    )
    @click.option(
        "--output",
        "-o",
        help="Output the result file. Default to the same target dir",
        default=default.default_output_path(),
        type=click.STRING,
    )
    @click.option(
        "--algo",
        "-a",
        help="Specified algorithm in the way to detect diagram connectors",
        default=default.deafult_algo(),
        type=click.STRING,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
