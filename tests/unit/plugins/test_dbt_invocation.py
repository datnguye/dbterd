import importlib
from importlib.machinery import ModuleSpec
import sys
from unittest import mock

import click
from dbt.cli.main import dbtRunnerResult
import pytest

from dbterd.plugins.dbt_core import dbt_invocation
from dbterd.plugins.dbt_core.dbt_invocation import DbtInvocation


class TestDbtInvocation:
    def test_import_error_dbt_runner(self):
        """Test that ImportError when importing DbtRunner is handled gracefully."""
        # Save original modules
        orig_dbt_cli_main = sys.modules.get("dbt.cli.main")
        orig_dbt_invocation = sys.modules.get("dbterd.plugins.dbt_core.dbt_invocation")

        try:
            # Remove the module from cache to force reimport
            if "dbt.cli.main" in sys.modules:
                del sys.modules["dbt.cli.main"]
            if "dbterd.plugins.dbt_core.dbt_invocation" in sys.modules:
                del sys.modules["dbterd.plugins.dbt_core.dbt_invocation"]

            # Mock the import to raise ImportError
            with mock.patch(
                "builtins.__import__",
                side_effect=lambda name, *args, **kwargs: (
                    (_ for _ in ()).throw(ImportError(f"No module named '{name}'"))
                    if name == "dbt.cli.main"
                    else importlib.__import__(name, *args, **kwargs)
                ),
            ):
                # Import the module which should catch the ImportError
                import dbterd.plugins.dbt_core.dbt_invocation as reloaded_module  # noqa: PLC0415

                # Verify that DbtRunner is None when import fails
                assert reloaded_module.DbtRunner is None
        finally:
            # Restore original modules
            if orig_dbt_cli_main:
                sys.modules["dbt.cli.main"] = orig_dbt_cli_main
            if orig_dbt_invocation:
                sys.modules["dbterd.plugins.dbt_core.dbt_invocation"] = orig_dbt_invocation
            # Reload to restore the normal state
            importlib.reload(dbt_invocation)

    @mock.patch("importlib.util.find_spec")
    def test__ensure_dbt_installed__no_dbt_installed(self, mock_find_spec):
        mock_find_spec.return_value = ModuleSpec(name="dbt", loader=None)
        with pytest.raises(click.UsageError):
            DbtInvocation()._DbtInvocation__ensure_dbt_installed()

    @pytest.mark.parametrize(
        "select_rules, exclude_rules, mock_dbt_runner_invoke_rv, expected",
        [
            ([], [], dbtRunnerResult(success=True, result=[]), []),
            (
                [],
                [],
                dbtRunnerResult(success=True, result=["p1.p2.p3.p4"]),
                ["exact:model.p1.p4"],
            ),
            (
                ["dummy"],
                ["dummy"],
                dbtRunnerResult(success=True, result=["p1.p2.p3.p4"]),
                ["exact:model.p1.p4"],
            ),
        ],
    )
    @mock.patch("dbt.cli.main.dbtRunner.invoke")
    def test_get_selection(
        self,
        mock_dbt_runner_invoke,
        select_rules,
        exclude_rules,
        mock_dbt_runner_invoke_rv,
        expected,
    ):
        mock_dbt_runner_invoke.return_value = mock_dbt_runner_invoke_rv
        invoker = DbtInvocation()
        actual = invoker.get_selection(select_rules=select_rules, exclude_rules=exclude_rules)
        assert actual == expected

        args = ["ls", "--resource-type", "model"]
        if select_rules:
            args.extend(["--select", " ".join(select_rules)])
        if exclude_rules:
            args.extend(["--exclude", " ".join(exclude_rules)])
        mock_dbt_runner_invoke.assert_called_once_with(
            [
                *["--quiet", "--log-level", "none"],
                *args,
                *["--project-dir", invoker.project_dir],
            ]
        )

    @mock.patch("dbt.cli.main.dbtRunner.invoke")
    def test_get_selection__failed(self, mock_dbt_runner_invoke):
        mock_dbt_runner_invoke.return_value = dbtRunnerResult(success=False)
        with pytest.raises(click.UsageError):
            DbtInvocation(dbt_target="dummy").get_selection(select_rules=[], exclude_rules=[])

    @mock.patch("dbt.cli.main.dbtRunner.invoke")
    def test_get_artifacts_for_erd(self, mock_dbt_runner_invoke):
        invoker = DbtInvocation()
        _ = invoker.get_artifacts_for_erd()

        args = ["docs", "generate"]
        mock_dbt_runner_invoke.assert_called_once_with(
            [
                *["--quiet", "--log-level", "none"],
                *args,
                *["--project-dir", invoker.project_dir],
            ]
        )
