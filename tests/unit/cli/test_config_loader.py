from pathlib import Path
from unittest.mock import patch

import pytest

import dbterd.cli.config
from dbterd.cli.config import (
    ConfigError,
    find_config_file,
    has_dbterd_section,
    load_config,
    load_toml_config,
    load_yaml_config,
    normalize_config_keys,
)


class TestNormalizeConfigKeys:
    def test_converts_kebab_to_snake_case(self):
        config = {"dbt-cloud-host-url": "test.com", "resource-type": ["model"]}
        result = normalize_config_keys(config)
        assert result == {"dbt_cloud_host_url": "test.com", "resource_type": ["model"]}

    def test_handles_nested_dicts(self):
        config = {"dbt-cloud": {"host-url": "test.com", "account-id": "123"}}
        result = normalize_config_keys(config)
        assert result == {"dbt_cloud": {"host_url": "test.com", "account_id": "123"}}

    def test_handles_empty_dict(self):
        assert normalize_config_keys({}) == {}

    def test_preserves_snake_case_keys(self):
        config = {"already_snake": "value", "another_key": 123}
        result = normalize_config_keys(config)
        assert result == config

    def test_handles_mixed_values(self):
        config = {
            "string-key": "value",
            "list-key": [1, 2, 3],
            "bool-key": True,
            "none-key": None,
        }
        result = normalize_config_keys(config)
        assert result == {
            "string_key": "value",
            "list_key": [1, 2, 3],
            "bool_key": True,
            "none_key": None,
        }


class TestHasDbterdSection:
    def test_returns_true_when_section_exists(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        toml_path = fixtures_dir / "pyproject.toml"
        assert has_dbterd_section(toml_path) is True

    def test_returns_false_when_section_missing(self, tmp_path):
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text("[project]\nname = 'test'\n")
        assert has_dbterd_section(toml_path) is False

    def test_returns_false_when_file_not_exists(self, tmp_path):
        toml_path = tmp_path / "nonexistent.toml"
        assert has_dbterd_section(toml_path) is False

    def test_returns_false_when_invalid_toml(self, tmp_path):
        toml_path = tmp_path / "invalid.toml"
        toml_path.write_text("invalid toml content [[[")
        assert has_dbterd_section(toml_path) is False


class TestLoadYamlConfig:
    def test_loads_valid_yaml_config(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        config_path = fixtures_dir / ".dbterd.yml"
        config = load_yaml_config(config_path)

        assert config["target"] == "mermaid"
        assert config["output"] == "./test_output"
        assert config["select"] == ["fct_*", "dim_*"]
        assert config["exclude"] == ["stg_*"]
        assert config["resource-type"] == ["model", "source"]
        assert config["algo"] == "semantic"
        assert config["omit-columns"] is True

    def test_raises_error_on_invalid_yaml(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        invalid_path = fixtures_dir / "invalid.yml"

        with pytest.raises(ConfigError) as exc_info:
            load_yaml_config(invalid_path)
        assert "Invalid YAML" in str(exc_info.value)

    def test_raises_error_on_file_not_found(self):
        nonexistent_path = Path("/nonexistent/config.yml")
        with pytest.raises(ConfigError) as exc_info:
            load_yaml_config(nonexistent_path)
        assert "Failed to read config file" in str(exc_info.value)

    def test_returns_empty_dict_for_empty_yaml(self, tmp_path):
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text("")
        config = load_yaml_config(config_path)
        assert config == {}

    def test_returns_empty_dict_for_yaml_with_comments_only(self, tmp_path):
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text("# Only comments\n# No actual config\n")
        config = load_yaml_config(config_path)
        assert config == {}


class TestLoadTomlConfig:
    def test_loads_valid_toml_config(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        config_path = fixtures_dir / "pyproject.toml"
        config = load_toml_config(config_path)

        assert config["target"] == "dbml"
        assert config["output"] == "./toml_output"
        assert config["select"] == ["model_*"]
        assert config["resource-type"] == ["model"]
        assert config["algo"] == "test_relationship"

    def test_raises_error_on_invalid_toml(self, tmp_path):
        config_path = tmp_path / "invalid.toml"
        config_path.write_text("[invalid toml content")

        with pytest.raises(ConfigError) as exc_info:
            load_toml_config(config_path)
        assert "Invalid TOML" in str(exc_info.value)

    def test_raises_error_when_tomllib_not_available(self, tmp_path, monkeypatch):
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[tool.dbterd]\ntarget = 'dbml'\n")

        monkeypatch.setattr(dbterd.cli.config, "tomllib", None)

        with pytest.raises(ConfigError) as exc_info:
            load_toml_config(config_path)
        assert "TOML support requires 'tomli' package" in str(exc_info.value)

    def test_returns_empty_dict_when_no_tool_dbterd_section(self, tmp_path):
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[project]\nname = 'test'\n")
        config = load_toml_config(config_path)
        assert config == {}

    def test_returns_empty_dict_when_tool_exists_but_no_dbterd(self, tmp_path):
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[tool.other]\nvalue = 'test'\n")
        config = load_toml_config(config_path)
        assert config == {}

    def test_raises_error_on_file_read_failure(self, tmp_path):
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[tool.dbterd]\ntarget = 'dbml'\n")

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                load_toml_config(config_path)
            assert "Failed to read TOML file" in str(exc_info.value)


class TestFindConfigFile:
    def test_finds_yaml_in_current_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text("target: dbml\n")

        found = find_config_file(tmp_path)
        assert found == config_path

    def test_finds_toml_when_no_yaml(self, tmp_path):
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[tool.dbterd]\ntarget = 'dbml'\n")

        found = find_config_file(tmp_path)
        assert found == config_path

    def test_prefers_toml_over_yaml(self, tmp_path):
        yaml_path = tmp_path / ".dbterd.yml"
        yaml_path.write_text("target: mermaid\n")

        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text("[tool.dbterd]\ntarget = 'dbml'\n")

        found = find_config_file(tmp_path)
        assert found == toml_path

    def test_returns_none_when_no_config_found(self, tmp_path):
        found = find_config_file(tmp_path)
        assert found is None

    def test_ignores_pyproject_without_dbterd_section(self, tmp_path):
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text("[project]\nname = 'test'\n")

        found = find_config_file(tmp_path)
        assert found is None

    def test_uses_cwd_when_start_dir_not_provided(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text("target: dbml\n")

        found = find_config_file()
        assert found == config_path


class TestLoadConfig:
    def test_loads_yaml_config_with_normalization(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        config = load_config(config_path=str(fixtures_dir / ".dbterd.yml"))

        # Keys should be normalized to snake_case
        assert config["target"] == "mermaid"
        assert config["resource_type"] == ["model", "source"]
        assert config["entity_name_format"] == "schema.table"
        assert config["omit_columns"] is True

    def test_loads_toml_config_with_normalization(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        config = load_config(config_path=str(fixtures_dir / "pyproject.toml"))

        # Keys should be normalized to snake_case
        assert config["target"] == "dbml"
        assert config["resource_type"] == ["model"]
        assert config["dbt_cloud_host_url"] == "test.cloud.getdbt.com"
        assert config["dbt_cloud_account_id"] == "12345"

    def test_raises_error_when_explicit_path_not_found(self):
        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path="/nonexistent/config.yml")
        assert "Configuration file not found" in str(exc_info.value)

    def test_raises_error_on_unsupported_format(self, tmp_path):
        config_path = tmp_path / "config.json"
        config_path.write_text('{"target": "dbml"}')

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path=str(config_path))
        assert "Unsupported configuration file format" in str(exc_info.value)

    def test_returns_empty_dict_when_no_config_found(self, tmp_path):
        config = load_config(start_dir=tmp_path)
        assert config == {}

    def test_searches_for_config_when_no_path_provided(self, tmp_path):
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text("target: graphviz\n")

        config = load_config(start_dir=tmp_path)
        assert config["target"] == "graphviz"

    def test_handles_yaml_extension_variations(self, tmp_path):
        # Test .yaml extension
        config_path = tmp_path / "config.yaml"
        config_path.write_text("target: d2\n")

        config = load_config(config_path=str(config_path))
        assert config["target"] == "d2"

    def test_gracefully_handles_unexpected_file_type_in_search(self, tmp_path, monkeypatch):
        # Create a file with unexpected name that might be found
        unexpected_file = tmp_path / ".dbterd.txt"
        unexpected_file.write_text("target: dbml\n")

        # Mock find_config_file to return unexpected file
        with patch("dbterd.cli.config.find_config_file", return_value=unexpected_file):
            config = load_config(start_dir=tmp_path)
            assert config == {}  # Should gracefully return empty dict

    def test_propagates_yaml_parse_errors(self):
        fixtures_dir = Path(__file__).parent / "fixtures"
        invalid_path = fixtures_dir / "invalid.yml"

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path=str(invalid_path))
        assert "Invalid YAML" in str(exc_info.value)

    def test_loads_toml_config_from_search_path(self, tmp_path):
        # Test loading TOML config when found via search (not explicit path)
        config_path = tmp_path / "pyproject.toml"
        config_path.write_text("[tool.dbterd]\ntarget = 'plantuml'\noutput = './search_output'\n")

        config = load_config(start_dir=tmp_path)
        assert config["target"] == "plantuml"
        assert config["output"] == "./search_output"

    def test_has_dbterd_section_when_tomllib_is_none(self, tmp_path, monkeypatch):
        # Test has_dbterd_section when tomllib is not available
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text("[tool.dbterd]\ntarget = 'dbml'\n")

        # Mock tomllib as None to simulate it not being available
        monkeypatch.setattr(dbterd.cli.config, "tomllib", None)
        assert has_dbterd_section(toml_path) is False
