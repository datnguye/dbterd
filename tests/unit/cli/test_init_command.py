from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
import yaml

from dbterd.cli.main import dbterd


class TestInitCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_init_creates_yaml_config_by_default(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(dbterd, ["init"])
            assert result.exit_code == 0
            assert Path(".dbterd.yml").exists()

            # Verify content
            content = Path(".dbterd.yml").read_text()
            assert "# dbterd Configuration File" in content
            assert "target: dbml" in content
            assert "algo: test_relationship" in content

    def test_init_fails_when_yaml_config_already_exists(self):
        with self.runner.isolated_filesystem():
            # Create existing config
            Path(".dbterd.yml").write_text("target: mermaid\n")

            result = self.runner.invoke(dbterd, ["init"])
            assert result.exit_code != 0
            assert "already exists" in result.output

    def test_init_overwrites_yaml_with_force_flag(self):
        with self.runner.isolated_filesystem():
            # Create existing config
            Path(".dbterd.yml").write_text("target: mermaid\n")

            result = self.runner.invoke(dbterd, ["init", "--force"])
            assert result.exit_code == 0

            # Verify content was overwritten
            content = Path(".dbterd.yml").read_text()
            assert "target: dbml" in content
            assert "# dbterd Configuration File" in content

    def test_init_yaml_template_contains_all_common_parameters(self):
        with self.runner.isolated_filesystem():
            self.runner.invoke(dbterd, ["init"])
            content = Path(".dbterd.yml").read_text()

            # Check for key parameters
            assert "target:" in content
            assert "output:" in content
            assert "select:" in content
            assert "exclude:" in content
            assert "resource-type:" in content
            assert "algo:" in content
            assert "entity-name-format:" in content
            # dbt-core template should NOT have dbt-cloud parameters
            assert "dbt-cloud-host-url:" not in content
            assert "dbt-cloud:" not in content

    def test_init_shows_success_message(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(dbterd, ["init"])
            assert result.exit_code == 0
            assert "Created configuration file:" in result.output
            assert ".dbterd.yml" in result.output
            assert "Template type: dbt-core" in result.output

    def test_init_help_text(self):
        result = self.runner.invoke(dbterd, ["init", "--help"])
        assert result.exit_code == 0
        assert "force" in result.output.lower()
        assert ".dbterd.yml" in result.output

    def test_yaml_template_has_proper_structure(self):
        with self.runner.isolated_filesystem():
            self.runner.invoke(dbterd, ["init"])
            content = Path(".dbterd.yml").read_text()

            config = yaml.safe_load(content)
            assert isinstance(config, dict)
            assert config["target"] == "dbml"
            assert config["algo"] == "test_relationship"

    def test_init_command_appears_in_help(self):
        result = self.runner.invoke(dbterd, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output

    def test_init_fails_on_write_error(self):
        with self.runner.isolated_filesystem():
            # Mock open to raise PermissionError only for .dbterd.yml write
            original_open = open

            def mock_open_func(filename, mode="r", *args, **kwargs):
                if ".dbterd.yml" in str(filename) and mode == "w":
                    raise PermissionError("Permission denied")
                return original_open(filename, mode, *args, **kwargs)

            with patch("builtins.open", mock_open_func):
                result = self.runner.invoke(dbterd, ["init"])
                assert result.exit_code != 0
                assert "Failed to create configuration file" in result.output
