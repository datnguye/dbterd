import os
import functools

import click

from dbterd import default


def common_params(func):
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
        "--resource-type",
        "-rt",
        help="Specified dbt resource type(seed, model, source, snapshot),default:model, use examples, -rt model -rt source",
        default=default.default_resource_types(),
        multiple=True,
        type=click.STRING,
    )
    @click.option(
        "--algo",
        "-a",
        help="Specified algorithm in the way to detect diagram connectors",
        default=default.default_algo(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--entity-name-format",
        "-enf",
        help="Specified the format of the entity node's name",
        default=default.default_entity_name_format(),
        show_default=True,
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
        "--omit-columns",
        help="Flag to omit columns in diagram. Currently only mermaid is supported",
        is_flag=True,
        default=False,
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def run_params(func):
    @common_params
    @click.option(
        "--artifacts-dir",
        "-ad",
        help="Specified the path to dbt artifact directory which known as /target directory",
        default="",
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
        "--dbt-cloud",
        help=(
            "Flag to download dbt artifact files using dbt Cloud API. "
            "This requires the additional parameters to be able to connection to dbt Cloud API"
        ),
        is_flag=True,
        default=False,
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-host-url",
        help=(
            "Configure dbt Cloud's Host URL. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_HOST_URL) if not specified. "
            "Sample dbt Cloud Run URL: "
            "https://<HOST_URL>/deploy/<ACCOUNT_ID>/projects/irrelevant/runs/<RUN_ID>"
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_HOST_URL", "cloud.getdbt.com"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-account-id",
        help=(
            "Configure dbt Cloud's Account ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ACCOUNT_ID) if not specified"
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_ACCOUNT_ID"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-run-id",
        help=(
            "Configure dbt Cloud's completed Run ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_RUN_ID) if not specified"
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_RUN_ID"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-job-id",
        help=(
            "Configure dbt Cloud's Job ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_JOB_ID) if not specified"
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_JOB_ID"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-service-token",
        help=(
            "Configure dbt Service Token (Permissions: Job Admin). "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_SERVICE_TOKEN) if not specified. "
            "Visit https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens to see how to generate it. "
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_SERVICE_TOKEN"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-api-version",
        help=(
            "Configure dbt Cloud Administrative API version. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_API_VERSION) if not specified."
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_API_VERSION", "v2"),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def run_metadata_params(func):
    @common_params
    @click.option(
        "--dbt-cloud-host-url",
        help=(
            "Configure dbt Cloud's Host URL. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_HOST_URL) if not specified. "
            "Sample dbt Cloud Run URL: "
            "https://<HOST_URL>/deploy/<ACCOUNT_ID>/projects/irrelevant/runs/<RUN_ID>"
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_HOST_URL", "cloud.getdbt.com"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-service-token",
        help=(
            "Configure dbt Service Token (Permissions: Job Admin). "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_SERVICE_TOKEN) if not specified. "
            "Visit https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens to see how to generate it. "
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_SERVICE_TOKEN"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-environment-id",
        help=(
            "Configure dbt Cloud Environment ID - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ENVIRONMENT_ID) if not specified."
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_ENVIRONMENT_ID"),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-query-file-path",
        help=(
            "Configure dbt Cloud GraphQL query file path - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_QUERY_FILE_PATH) if not specified."
        ),
        default=os.environ.get("DBTERD_DBT_CLOUD_QUERY_FILE_PATH"),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper
