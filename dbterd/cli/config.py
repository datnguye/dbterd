from pathlib import Path
import sys
from typing import Any, Optional

from dbterd import default
from dbterd.constants import (
    CONFIG_FILE_DBTERD_YML,
    CONFIG_FILE_PYPROJECT_TOML,
    CONFIG_TEMPLATE_DBT_CLOUD,
    CONFIG_TEMPLATE_DBT_CORE,
)
from dbterd.helpers.yaml import YamlParseError, load_yaml_text


if sys.version_info >= (3, 11):
    import tomllib

    TOMLDecodeError: type[Exception] = tomllib.TOMLDecodeError
else:  # pragma: no cover
    try:
        import tomli as tomllib

        TOMLDecodeError: type[Exception] = tomllib.TOMLDecodeError
    except ImportError:
        tomllib = None  # type: ignore
        TOMLDecodeError: type[Exception] = ValueError  # type: ignore


class ConfigError(Exception):
    """Exception raised for configuration file errors."""

    pass


def normalize_config_keys(config: dict[str, Any]) -> dict[str, Any]:
    """Convert kebab-case keys to snake_case for Python compatibility.

    Args:
        config: Configuration dictionary with kebab-case keys

    Returns:
        Dictionary with snake_case keys
    """
    normalized = {}
    for key, value in config.items():
        normalized_key = key.replace("-", "_")
        if isinstance(value, dict):
            normalized[normalized_key] = normalize_config_keys(value)
        else:
            normalized[normalized_key] = value
    return normalized


def has_dbterd_section(toml_path: Path) -> bool:
    """Check if pyproject.toml contains [tool.dbterd] section.

    Args:
        toml_path: Path to pyproject.toml file

    Returns:
        True if [tool.dbterd] section exists, False otherwise
    """
    if tomllib is None:
        return False

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
            return "tool" in data and "dbterd" in data.get("tool", {})
    except (OSError, TOMLDecodeError):
        return False


def load_yaml_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from .dbterd.yml file.

    Args:
        config_path: Path to .dbterd.yml file

    Returns:
        Configuration dictionary

    Raises:
        ConfigError: If YAML file is invalid
    """
    try:
        with open(config_path, encoding="utf-8") as f:
            content = f.read()
            config = load_yaml_text(content, path=str(config_path))
            return config if config else {}
    except YamlParseError as e:
        raise ConfigError(f"Invalid YAML in {config_path}:\n{e}") from e
    except OSError as e:
        raise ConfigError(f"Failed to read config file {config_path}: {e}") from e


def load_toml_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from pyproject.toml [tool.dbterd] section.

    Args:
        config_path: Path to pyproject.toml file

    Returns:
        Configuration dictionary from [tool.dbterd] section

    Raises:
        ConfigError: If TOML file is invalid or tomllib is not available
    """
    if tomllib is None:
        raise ConfigError("TOML support requires 'tomli' package for Python < 3.11. Install with: pip install tomli")

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            config = data.get("tool", {}).get("dbterd", {})
            return config if config else {}
    except OSError as e:
        raise ConfigError(f"Failed to read TOML file {config_path}: {e}") from e
    except TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in {config_path}: {e}") from e


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Search for dbterd configuration file in current directory only.

    Searches in the following order:
    1. pyproject.toml with [tool.dbterd] section
    2. .dbterd.yml

    Args:
        start_dir: Directory to search in. Defaults to current working directory.

    Returns:
        Path to configuration file, or None if not found
    """
    if start_dir is None:
        start_dir = Path.cwd()

    search_dir = start_dir.resolve()

    toml_config = search_dir / CONFIG_FILE_PYPROJECT_TOML
    if toml_config.exists() and has_dbterd_section(toml_config):
        return toml_config

    yaml_config = search_dir / CONFIG_FILE_DBTERD_YML
    if yaml_config.exists():
        return yaml_config

    return None


def load_config(config_path: Optional[str] = None, start_dir: Optional[Path] = None) -> dict[str, Any]:
    """Load dbterd configuration from file.

    Supports both .dbterd.yml and pyproject.toml formats.
    Returns empty dict if no configuration file is found (graceful fallback).

    Args:
        config_path: Explicit path to config file. If None, searches for config file.
        start_dir: Directory to start searching from. Defaults to current working directory.

    Returns:
        Configuration dictionary with normalized (snake_case) keys

    Raises:
        ConfigError: If config file is specified but cannot be loaded
    """
    # If explicit path provided, use it
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        if path.name.endswith(".yml") or path.name.endswith(".yaml"):
            config = load_yaml_config(path)
        elif path.name == CONFIG_FILE_PYPROJECT_TOML:
            config = load_toml_config(path)
        else:
            raise ConfigError(f"Unsupported configuration file format: {path.name}")
    else:
        # Search for config file
        found_path = find_config_file(start_dir=start_dir)
        if found_path is None:
            return {}  # No config file found - graceful fallback

        path = found_path
        if path.name.endswith(".yml") or path.name.endswith(".yaml"):
            config = load_yaml_config(path)
        elif path.name == CONFIG_FILE_PYPROJECT_TOML:
            config = load_toml_config(path)
        else:
            return {}  # Unexpected file type - graceful fallback

    # Normalize keys from kebab-case to snake_case
    return normalize_config_keys(config)


def get_yaml_template(template_type: str = "dbt-core") -> str:
    """Generate YAML configuration template with default values.

    Args:
        template_type: Type of template to generate. Options: "dbt-core", "dbt-cloud"

    Returns:
        Formatted YAML template string with default values
    """
    # Select template file based on type (default: dbt-core)
    template_file = CONFIG_TEMPLATE_DBT_CLOUD if template_type == "dbt-cloud" else CONFIG_TEMPLATE_DBT_CORE
    template_path = Path(__file__).parent.parent / "include" / "config_templates" / template_file

    with open(template_path, encoding="utf-8") as f:
        template_content = f.read()

    # Get default values
    resource_types = default.default_resource_types()
    resource_types_yaml = "\n".join([f"  - {rt}" for rt in resource_types])

    # Format template with default values
    return template_content.format(
        default_target=default.default_target(),
        default_output=default.default_output_path(),
        default_output_file_name=default.default_output_file_name() or "",
        default_artifact_path=default.default_artifact_path(),
        default_manifest_version=default.default_manifest_version() or "",
        default_catalog_version=default.default_catalog_version() or "",
        default_bypass_validation=str(default.default_bypass_validation()).lower(),
        default_algo=default.default_algo(),
        default_entity_name_format=default.default_entity_name_format(),
        default_omit_entity_name_quotes=str(default.default_omit_entity_name_quotes()).lower(),
        default_omit_columns=str(default.default_omit_columns()).lower(),
        default_dbt_project_dir=default.default_dbt_project_dir(),
        default_dbt=str(default.default_dbt()).lower(),
        default_dbt_auto_artifacts=str(default.default_dbt_auto_artifacts()).lower(),
        default_dbt_target=default.default_dbt_target() or "",
        default_dbt_cloud=str(default.default_dbt_cloud()).lower(),
        default_dbt_cloud_host_url=default.default_dbt_cloud_host_url(),
        default_dbt_cloud_api_version=default.default_dbt_cloud_api_version(),
        resource_types=resource_types_yaml,
    )
