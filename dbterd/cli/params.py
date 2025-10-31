import functools

import click

from dbterd import default


def common_params(func):
    @click.option(
        "--select",
        "-s",
        help="Selection criteria",
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
        help=("Specified dbt resource type(model, source), default:model, use examples, -rt model -rt source"),
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
        "--omit-entity-name-quotes",
        help="Flag to omit double quotes in the entity name. Currently only dbml is supported",
        is_flag=True,
        default=default.default_omit_entity_name_quotes(),
        show_default=True,
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
        "--output-file-name",
        "-ofn",
        help="Output the result file name. Default is defined in the target module",
        default=default.default_output_file_name(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--omit-columns",
        help="Flag to omit columns in diagram. Currently only mermaid is supported",
        is_flag=True,
        default=default.default_omit_columns(),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def dbt_cloud_common_params(func):
    @click.option(
        "--dbt-cloud-host-url",
        help=(
            "Configure dbt Cloud's Host URL. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_HOST_URL) if not specified. "
            "Sample dbt Cloud Run URL: "
            "https://<HOST_URL>/deploy/<ACCOUNT_ID>/projects/irrelevant/runs/<RUN_ID>"
        ),
        default=default.default_dbt_cloud_host_url(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-service-token",
        help=(
            "Configure dbt Service Token (Permissions: Job Admin). "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_SERVICE_TOKEN) if not specified. "
            "Visit https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens to see how to generate it. "
        ),
        default=default.default_dbt_cloud_service_token(),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def run_params(func):
    @common_params
    @dbt_cloud_common_params
    @click.option(
        "--artifacts-dir",
        "-ad",
        help="Specified the path to dbt artifact directory which known as /target directory",
        default=default.default_artifacts_dir(),
        type=click.STRING,
    )
    @click.option(
        "--manifest-version",
        "-mv",
        help="Specified dbt manifest.json version",
        type=click.STRING,
    )
    @click.option(
        "--bypass-validation",
        help="Flag to bypass the Pydantic Validation Error by patching extra to ignored fields",
        is_flag=True,
        default=default.default_bypass_validation(),
        show_default=True,
    )
    @click.option(
        "--catalog-version",
        "-cv",
        help="Specified dbt catalog.json version",
        type=click.STRING,
    )
    @click.option(
        "--dbt",
        help="Flag to indicate the Selection to follow dbt's one leveraging Programmatic Invocation",
        is_flag=True,
        default=default.default_dbt(),
        show_default=True,
    )
    @click.option(
        "--dbt-project-dir",
        "-dpd",
        help="Specified dbt project directory path",
        default=default.default_dbt_project_dir(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--dbt-target",
        "-dt",
        help="Specified dbt target name",
        default=default.default_dbt_target(),
        type=click.STRING,
    )
    @click.option(
        "--dbt-auto-artifacts",
        help="Flag to force generating dbt artifact files leveraging Programmatic Invocation",
        is_flag=True,
        default=default.default_dbt_auto_artifacts(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud",
        help=(
            "Flag to download dbt artifact files using dbt Cloud API. "
            "This requires the additional parameters to be able to connection to dbt Cloud API"
        ),
        is_flag=True,
        default=default.default_dbt_cloud(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-account-id",
        help=(
            "Configure dbt Cloud's Account ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ACCOUNT_ID) if not specified"
        ),
        default=default.default_dbt_cloud_account_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-run-id",
        help=(
            "Configure dbt Cloud's completed Run ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_RUN_ID) if not specified"
        ),
        default=default.default_dbt_cloud_run_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-job-id",
        help=(
            "Configure dbt Cloud's Job ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_JOB_ID) if not specified"
        ),
        default=default.default_dbt_cloud_job_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-api-version",
        help=(
            "Configure dbt Cloud Administrative API version. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_API_VERSION) if not specified."
        ),
        default=default.default_dbt_cloud_api_version(),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def run_metadata_params(func):
    @common_params
    @dbt_cloud_common_params
    @click.option(
        "--dbt-cloud-environment-id",
        help=(
            "Configure dbt Cloud Environment ID - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ENVIRONMENT_ID) if not specified."
        ),
        default=default.default_dbt_cloud_environment_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-query-file-path",
        help=(
            "Configure dbt Cloud GraphQL query file path - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_QUERY_FILE_PATH) if not specified."
        ),
        default=default.default_dbt_cloud_query_file_path(),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def debug_params(func):
    @common_params
    @dbt_cloud_common_params
    @click.option(
        "--artifacts-dir",
        "-ad",
        help="Specified the path to dbt artifact directory which known as /target directory",
        default=default.default_artifacts_dir(),
        type=click.STRING,
    )
    @click.option(
        "--manifest-version",
        "-mv",
        help="Specified dbt manifest.json version",
        type=click.STRING,
    )
    @click.option(
        "--bypass-validation",
        help="Flag to bypass the Pydantic Validation Error by patching extra to ignored fields",
        is_flag=True,
        default=default.default_bypass_validation(),
        show_default=True,
    )
    @click.option(
        "--catalog-version",
        "-cv",
        help="Specified dbt catalog.json version",
        type=click.STRING,
    )
    @click.option(
        "--dbt",
        help="Flag to indicate the Selection to follow dbt's one leveraging Programmatic Invocation",
        is_flag=True,
        default=default.default_dbt(),
        show_default=True,
    )
    @click.option(
        "--dbt-project-dir",
        "-dpd",
        help="Specified dbt project directory path",
        default=default.default_dbt_project_dir(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--dbt-target",
        "-dt",
        help="Specified dbt target name",
        default=default.default_dbt_target(),
        type=click.STRING,
    )
    @click.option(
        "--dbt-auto-artifacts",
        help="Flag to force generating dbt artifact files leveraging Programmatic Invocation",
        is_flag=True,
        default=default.default_dbt_auto_artifacts(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud",
        help=(
            "Flag to download dbt artifact files using dbt Cloud API. "
            "This requires the additional parameters to be able to connection to dbt Cloud API"
        ),
        is_flag=True,
        default=default.default_dbt_cloud(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-account-id",
        help=(
            "Configure dbt Cloud's Account ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ACCOUNT_ID) if not specified"
        ),
        default=default.default_dbt_cloud_account_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-run-id",
        help=(
            "Configure dbt Cloud's completed Run ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_RUN_ID) if not specified"
        ),
        default=default.default_dbt_cloud_run_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-job-id",
        help=(
            "Configure dbt Cloud's Job ID. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_JOB_ID) if not specified"
        ),
        default=default.default_dbt_cloud_job_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-api-version",
        help=(
            "Configure dbt Cloud Administrative API version. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_API_VERSION) if not specified."
        ),
        default=default.default_dbt_cloud_api_version(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-environment-id",
        help=(
            "Configure dbt Cloud Environment ID - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_ENVIRONMENT_ID) if not specified."
        ),
        default=default.default_dbt_cloud_environment_id(),
        show_default=True,
    )
    @click.option(
        "--dbt-cloud-query-file-path",
        help=(
            "Configure dbt Cloud GraphQL query file path - Used for Metadata (Discovery) API. "
            "Try to get OS environment variable (DBTERD_DBT_CLOUD_QUERY_FILE_PATH) if not specified."
        ),
        default=default.default_dbt_cloud_query_file_path(),
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper


def init_params(func):
    @click.option(
        "--template",
        "-tmpl",
        type=click.Choice(["dbt-core", "dbt-cloud"], case_sensitive=False),
        default=default.default_init_template(),
        show_default=True,
        help="Configuration template type (dbt-core or dbt-cloud)",
    )
    @click.option(
        "--force",
        is_flag=True,
        default=default.default_init_force(),
        help="Overwrite existing configuration file if present",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper
