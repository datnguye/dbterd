from unittest import mock

import click
import pytest

from dbterd.cli.main import dbterdRunner
from dbterd.default import default_output_path


class TestRunner:
    @pytest.fixture
    def dbterd(self) -> dbterdRunner:
        return dbterdRunner()

    def test_runner_unhandled_exception(self, dbterd: dbterdRunner) -> None:
        with mock.patch(
            "dbterd.cli.main.dbterd.make_context", side_effect=click.exceptions.Exit(-1)
        ):
            with pytest.raises(Exception):
                dbterd.invoke(["debug"])

    def test_group_invalid_option(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["--invalid-option"])

    def test_command_invalid_option(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["run", "--invalid-option"])

    def test_invalid_command(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["invalid-command"])

    def test_invoke_version(self, dbterd: dbterdRunner) -> None:
        dbterd.invoke(["--version"])

    def test_invoke_help(self, dbterd: dbterdRunner) -> None:
        dbterd.invoke(["-h"])
        dbterd.invoke(["--help"])

    def test_invoke_debug(self, dbterd: dbterdRunner) -> None:
        dbterd.invoke(["debug"])

    def test_invoke_run_with_invalid_artifact_path(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(click.exceptions.FileError):
            dbterd.invoke(["run", "--artifacts-dir", "/path/invalid"])

    def test_invoke_run_with_invalid_target(self, dbterd: dbterdRunner) -> None:
        invalid_target = "invalid-target"
        with pytest.raises(Exception) as e:
            dbterd.invoke(["run", "--target", invalid_target])
            assert str(e) == (f"Could not find adapter target type {invalid_target}!")

    def test_invoke_run_with_invalid_strategy(self, dbterd: dbterdRunner) -> None:
        invalid_strategy = "invalid-strategy"
        with mock.patch(
            "dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None
        ) as mock_read_m:
            with mock.patch(
                "dbterd.adapters.base.Executor._Executor__read_catalog",
                return_value=None,
            ) as mock_read_c:
                with mock.patch(
                    "dbterd.adapters.base.Executor._Executor__save_result",
                    return_value=None,
                ) as mock_save:
                    with pytest.raises(Exception):
                        dbterd.invoke(["run", "--algo", invalid_strategy])
                    mock_read_m.assert_called_once()
                    mock_read_c.assert_called_once()
                    mock_save.call_count == 0

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
    def test_invoke_run_ok(self, target, output, dbterd: dbterdRunner) -> None:
        with mock.patch(
            "dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None
        ) as mock_read_m:
            with mock.patch(
                "dbterd.adapters.base.Executor._Executor__read_catalog",
                return_value=None,
            ) as mock_read_c:
                with mock.patch(
                    f"dbterd.adapters.targets.{target}.parse",
                    return_value="--irrelevant--",
                ) as mock_engine_parse:
                    with mock.patch("builtins.open", mock.mock_open()) as mock_open_w:
                        dbterd.invoke(["run", "--target", target])
                        mock_read_m.assert_called_once()
                        mock_read_c.assert_called_once()
                        mock_engine_parse.assert_called_once()
                        mock_open_w.assert_called_once_with(
                            f"{default_output_path()}/{output}", "w"
                        )

                        dbterd.invoke(
                            ["run", "--target", target, "--output", "/custom/path"]
                        )
                        mock_open_w.assert_called_with(f"/custom/path/{output}", "w")

    def test_command_invalid_selection_rule(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["run", "--select", "notexist:dummy"])

    @pytest.mark.parametrize(
        "target, output",
        [
            ("dbml", "output.dbml"),
        ],
    )
    def test_invoke_run_failed_to_write_output(
        self, target, output, dbterd: dbterdRunner
    ) -> None:
        with mock.patch(
            "dbterd.adapters.base.Executor._Executor__read_manifest", return_value=None
        ) as mock_read_m:
            with mock.patch(
                "dbterd.adapters.base.Executor._Executor__read_catalog",
                return_value=None,
            ) as mock_read_c:
                with mock.patch(
                    f"dbterd.adapters.targets.{target}.parse",
                    return_value="--irrelevant--",
                ) as mock_engine_parse:
                    with mock.patch(
                        "builtins.open", return_value=PermissionError()
                    ) as mock_open_w:
                        with pytest.raises(click.FileError):
                            dbterd.invoke(["run", "--target", target])
                        mock_read_m.assert_called_once()
                        mock_read_c.assert_called_once()
                        mock_engine_parse.assert_called_once()
                        mock_open_w.assert_called_once()

    def test_invoke_run_metadata_ok(self, dbterd: dbterdRunner) -> None:
        with mock.patch(
            "dbterd.cli.main.Executor.run_metadata", return_value=None
        ) as mock_run_metadata:
            dbterd.invoke(["run-metadata"])
            mock_run_metadata.assert_called_once()
