import contextlib
from unittest import mock

import click
import pytest

from dbterd.cli.config import ConfigError
from dbterd.cli.main import DbterdRunner
from dbterd.default import default_output_path


class TestRunner:
    @pytest.fixture
    def dbterd(self) -> DbterdRunner:
        return DbterdRunner()

    def test_runner_unhandled_exception(self, dbterd: DbterdRunner) -> None:
        with mock.patch("dbterd.cli.main.dbterd.make_context", side_effect=click.exceptions.Exit(-1)):
            with pytest.raises(Exception) as excinfo:
                dbterd.invoke(["debug"])
            assert "unhandled exit code" in str(excinfo.value)

    def test_group_invalid_option(self, dbterd: DbterdRunner) -> None:
        with pytest.raises(Exception) as excinfo:
            dbterd.invoke(["--invalid-option"])
        assert "No such option" in str(excinfo.value)

    def test_command_invalid_option(self, dbterd: DbterdRunner) -> None:
        with pytest.raises(Exception) as excinfo:
            dbterd.invoke(["run", "--invalid-option"])
        assert "No such option" in str(excinfo.value)

    def test_invalid_command(self, dbterd: DbterdRunner) -> None:
        with pytest.raises(Exception) as excinfo:
            dbterd.invoke(["invalid-command"])
        assert "No such command" in str(excinfo.value)

    def test_invoke_version(self, dbterd: DbterdRunner) -> None:
        dbterd.invoke(["--version"])

    def test_invoke_help(self, dbterd: DbterdRunner) -> None:
        dbterd.invoke(["-h"])
        dbterd.invoke(["--help"])

    def test_invoke_debug(self, dbterd: DbterdRunner) -> None:
        dbterd.invoke(["debug"])

    def test_invoke_run_with_invalid_artifact_path(self, dbterd: DbterdRunner) -> None:
        with (
            mock.patch("dbterd.cli.main.load_config", return_value={}),
            pytest.raises(click.exceptions.FileError),
        ):
            dbterd.invoke(["run", "--artifacts-dir", "/path/invalid", "--dbt-project-dir", "/path/invalid"])

    def test_invoke_run_with_invalid_target(self, dbterd: DbterdRunner) -> None:
        invalid_target = "invalid-target"
        with pytest.raises(Exception) as e:
            dbterd.invoke(["run", "--target", invalid_target])
            assert str(e) == (f"Could not find adapter target type {invalid_target}!")

    def test_invoke_run_with_invalid_strategy(self, dbterd: DbterdRunner) -> None:
        invalid_strategy = "invalid-strategy"
        with contextlib.ExitStack() as stack:
            mock_read_m = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None)
            )
            mock_read_c = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_catalog", return_value=None)
            )
            mock_save = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__save_result", return_value=None)
            )
            with pytest.raises(Exception) as excinfo:
                dbterd.invoke(["run", "--algo", invalid_strategy])
            assert "Could not find adapter algo" in str(excinfo.value)
            mock_read_m.assert_called_once()
            mock_read_c.assert_called_once()
            assert mock_save.call_count == 0

    @pytest.mark.parametrize(
        "target, output",
        [
            ("dbml", "output.dbml"),
            ("mermaid", "output.md"),
            ("plantuml", "output.plantuml"),
            ("graphviz", "output.graphviz"),
            ("d2", "output.d2"),
        ],
    )
    def test_invoke_run_ok(self, target, output, dbterd: DbterdRunner) -> None:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch("dbterd.cli.main.load_config", return_value={}))
            mock_read_m = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None)
            )
            mock_read_c = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_catalog", return_value=None)
            )
            mock_engine_parse = stack.enter_context(
                mock.patch(f"dbterd.adapters.targets.{target}.parse", return_value="--irrelevant--")
            )
            mock_open_w = stack.enter_context(mock.patch("builtins.open", mock.mock_open()))
            dbterd.invoke(["run", "--target", target])
            mock_read_m.assert_called_once()
            mock_read_c.assert_called_once()
            mock_engine_parse.assert_called_once()
            # Check that open was called with the output file (version detection also calls open for manifest/catalog)
            mock_open_w.assert_any_call(f"{default_output_path()}/{output}", "w")

            dbterd.invoke(["run", "--target", target, "--output", "/custom/path"])
            mock_open_w.assert_any_call(f"/custom/path/{output}", "w")

    def test_command_invalid_selection_rule(self, dbterd: DbterdRunner) -> None:
        with pytest.raises(Exception) as excinfo:
            dbterd.invoke(["run", "--select", "notexist:dummy"])
        assert "Unsupported Selection found" in str(excinfo.value)

    @pytest.mark.parametrize(
        "target, output",
        [
            ("dbml", "output.dbml"),
        ],
    )
    def test_invoke_run_failed_to_write_output(self, target, output, dbterd: DbterdRunner) -> None:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch("dbterd.cli.main.load_config", return_value={}))
            mock_read_m = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None)
            )
            mock_read_c = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_catalog", return_value=None)
            )
            mock_engine_parse = stack.enter_context(
                mock.patch(f"dbterd.adapters.targets.{target}.parse", return_value="--irrelevant--")
            )

            # Mock open to raise PermissionError only for write mode (version detection uses read mode)
            def mock_open_side_effect(filename, mode="r", *args, **kwargs):
                if mode == "w":
                    raise PermissionError()
                return mock.mock_open()()

            mock_open_w = stack.enter_context(mock.patch("builtins.open", side_effect=mock_open_side_effect))
            with pytest.raises(click.FileError):
                dbterd.invoke(["run", "--target", target])
            mock_read_m.assert_called_once()
            mock_read_c.assert_called_once()
            mock_engine_parse.assert_called_once()
            # Check that open was called with write mode for the output file
            mock_open_w.assert_any_call(f"{default_output_path()}/{output}", "w")

    def test_invoke_run_metadata_ok(self, dbterd: DbterdRunner) -> None:
        with mock.patch("dbterd.cli.main.Executor.run_metadata", return_value=None) as mock_run_metadata:
            dbterd.invoke(["run-metadata"])
            mock_run_metadata.assert_called_once()

    def test_config_error_handling(self, dbterd: DbterdRunner) -> None:
        with (
            mock.patch("dbterd.cli.main.load_config", side_effect=ConfigError("Test config error")),
            pytest.raises(click.ClickException) as exc_info,
        ):
            dbterd.invoke(["run"])
        assert "Test config error" in str(exc_info.value)

    def test_nested_dbt_cloud_config_flattening(self, dbterd: DbterdRunner, tmp_path, monkeypatch) -> None:
        # Test that nested dbt-cloud config in dict form gets flattened
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / ".dbterd.yml"
        config_path.write_text(
            """
dbt-cloud:
  host-url: test.cloud.getdbt.com
  account-id: "12345"
  service-token: dummy_token
target: dbml
"""
        )

        # Need to allow config file to be read but mock other file operations
        original_open = open

        def selective_mock_open(filename, mode="r", *args, **kwargs):
            # Allow reading the config file and template files
            if (
                ".dbterd.yml" in str(filename)
                or "config_template" in str(filename)
                or "manifest.json" in str(filename)
                or "catalog.json" in str(filename)
            ):
                return original_open(filename, mode, *args, **kwargs)
            # Mock writing output file
            if mode == "w":
                return mock.mock_open()()
            return original_open(filename, mode, *args, **kwargs)

        with contextlib.ExitStack() as stack:
            mock_read_m = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None)
            )
            mock_read_c = stack.enter_context(
                mock.patch("dbterd.adapters.base.Executor._Executor__read_catalog", return_value=None)
            )
            stack.enter_context(mock.patch("dbterd.adapters.targets.dbml.parse", return_value="--irrelevant--"))
            stack.enter_context(mock.patch("builtins.open", selective_mock_open))
            dbterd.invoke(["run"])
            mock_read_m.assert_called_once()
            mock_read_c.assert_called_once()
