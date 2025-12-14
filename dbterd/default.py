import json
import os
from pathlib import Path
from typing import Optional

from dbterd.helpers.file import extract_artifact_version_from_file


def default_artifact_path() -> str:
    return os.environ.get("DBTERD_ARTIFACT_PATH", str(Path.cwd() / "target"))


def default_output_path() -> str:
    return os.environ.get("DBTERD_OUTPUT_PATH", str(Path.cwd() / "target"))


def default_target() -> str:
    return os.environ.get("DBTERD_TARGET", "dbml")


def default_algo() -> str:
    return os.environ.get("DBTERD_ALGO", "test_relationship")


def default_resource_types() -> list[str]:
    default_value = os.environ.get("DBTERD_RESOURCE_TYPES", "model")
    if isinstance(default_value, str):
        return [default_value]
    return default_value


def default_entity_name_format() -> str:
    return os.environ.get("DBTERD_ENTITY_NAME_FORMAT", "resource.package.model")


def default_omit_entity_name_quotes() -> bool:
    return os.environ.get("DBTERD_OMIT_ENTITY_NAME_QUOTES", "false").lower() in ["true", "yes", "1"]


def default_omit_columns() -> bool:
    return os.environ.get("DBTERD_OMIT_COLUMNS", "false").lower() in ["true", "yes", "1"]


def default_dbt_project_dir() -> str:
    return os.environ.get("DBTERD_DBT_PROJECT_DIR", ".")


def default_dbt() -> bool:
    return os.environ.get("DBTERD_DBT", "false").lower() in ["true", "yes", "1"]


def default_dbt_auto_artifacts() -> bool:
    return os.environ.get("DBTERD_DBT_AUTO_ARTIFACTS", "false").lower() in ["true", "yes", "1"]


def default_dbt_cloud() -> bool:
    return os.environ.get("DBTERD_DBT_CLOUD", "false").lower() in ["true", "yes", "1"]


def default_dbt_cloud_host_url() -> str:
    return os.environ.get("DBTERD_DBT_CLOUD_HOST_URL", "cloud.getdbt.com")


def default_dbt_cloud_api_version() -> str:
    return os.environ.get("DBTERD_DBT_CLOUD_API_VERSION", "v2")


def default_dbt_cloud_account_id() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_ACCOUNT_ID")


def default_dbt_cloud_run_id() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_RUN_ID")


def default_dbt_cloud_job_id() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_JOB_ID")


def default_dbt_cloud_service_token() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_SERVICE_TOKEN")


def default_dbt_cloud_environment_id() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_ENVIRONMENT_ID")


def default_dbt_cloud_query_file_path() -> Optional[str]:
    return os.environ.get("DBTERD_DBT_CLOUD_QUERY_FILE_PATH")


def default_artifacts_dir() -> str:
    return os.environ.get("DBTERD_ARTIFACTS_DIR", "")


def default_bypass_validation() -> bool:
    return os.environ.get("DBTERD_BYPASS_VALIDATION", "true").lower() in ["true", "yes", "1"]


def default_init_template() -> str:
    return os.environ.get("DBTERD_INIT_TEMPLATE", "dbt-core")


def default_init_force() -> bool:
    return os.environ.get("DBTERD_INIT_FORCE", "false").lower() in ["true", "yes", "1"]


def default_manifest_version(artifacts_dir: Optional[str] = None) -> Optional[str]:
    """Auto-detect manifest.json version from metadata.

    Args:
        artifacts_dir: Optional artifacts directory path. If not provided, uses default.

    Returns:
        Version string if manifest.json exists and has metadata, None otherwise
    """
    if env_version := os.environ.get("DBTERD_MANIFEST_VERSION"):
        return env_version

    # Try to read version from manifest.json
    if not artifacts_dir:
        artifacts_dir = default_artifacts_dir() or default_artifact_path()

    manifest_path = Path(artifacts_dir) / "manifest.json"

    if manifest_path.exists():
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)
                if "metadata" in manifest_data and "dbt_schema_version" in manifest_data["metadata"]:
                    schema_version = manifest_data["metadata"]["dbt_schema_version"]
                    return extract_artifact_version_from_file(schema_version)
        except (json.JSONDecodeError, KeyError, OSError):
            pass

    return None


def default_catalog_version(artifacts_dir: Optional[str] = None) -> Optional[str]:
    """Auto-detect catalog.json version from metadata.

    Args:
        artifacts_dir: Optional artifacts directory path. If not provided, uses default.

    Returns:
        Version string if catalog.json exists and has metadata, None otherwise
    """
    if env_version := os.environ.get("DBTERD_CATALOG_VERSION"):
        return env_version

    # Try to read version from catalog.json
    if not artifacts_dir:
        artifacts_dir = default_artifacts_dir() or default_artifact_path()

    catalog_path = Path(artifacts_dir) / "catalog.json"

    if catalog_path.exists():
        try:
            with open(catalog_path, encoding="utf-8") as f:
                catalog_data = json.load(f)
                if "metadata" in catalog_data and "dbt_schema_version" in catalog_data["metadata"]:
                    schema_version = catalog_data["metadata"]["dbt_schema_version"]
                    return extract_artifact_version_from_file(schema_version)
        except (json.JSONDecodeError, KeyError, OSError):
            pass

    return None


def default_output_file_name() -> Optional[str]:
    """Default output file name.

    Returns:
        None to use target-specific default
    """
    return os.environ.get("DBTERD_OUTPUT_FILE_NAME")


def default_dbt_target() -> Optional[str]:
    """Default dbt target name.

    Returns:
        None to use dbt's default target
    """
    return os.environ.get("DBTERD_DBT_TARGET")
