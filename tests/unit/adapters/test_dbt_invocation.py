from importlib.machinery import ModuleSpec
from unittest import mock

import click
import pytest
from dbt.cli.main import dbtRunnerResult

from dbterd.adapters.dbt_core.dbt_invocation import DbtInvocation


class TestDbtInvocation:
    @mock.patch("importlib.util.find_spec")
    def test__ensure_dbt_installed__no_dbt_installed(self, mock_find_spec):
        mock_find_spec.return_value = ModuleSpec(name="dbt", loader=None)
        with pytest.raises(click.UsageError):
            DbtInvocation()._DbtInvocation__ensure_dbt_installed()

    @pytest.mark.parametrize(
        "select_rules, exclude_rules, mock_dbtRunner_invoke_rv, expected",
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
    @mock.patch("dbterd.adapters.dbt_core.dbt_invocation.dbtRunner.invoke")
    def test_get_selection(
        self,
        mock_dbtRunner_invoke,
        select_rules,
        exclude_rules,
        mock_dbtRunner_invoke_rv,
        expected,
    ):
        mock_dbtRunner_invoke.return_value = mock_dbtRunner_invoke_rv
        invoker = DbtInvocation()
        actual = invoker.get_selection(
            select_rules=select_rules, exclude_rules=exclude_rules
        )
        assert actual == expected

        args = ["ls", "--resource-type", "model"]
        if select_rules:
            args.extend(["--select", " ".join(select_rules)])
        if exclude_rules:
            args.extend(["--exclude", " ".join(exclude_rules)])
        mock_dbtRunner_invoke.assert_called_once_with(
            [
                *["--quiet", "--log-level", "none"],
                *args,
                *["--project-dir", invoker.project_dir],
            ]
        )

    @mock.patch("dbterd.adapters.dbt_core.dbt_invocation.dbtRunner.invoke")
    def test_get_selection__failed(self, mock_dbtRunner_invoke):
        mock_dbtRunner_invoke.return_value = dbtRunnerResult(success=False)
        with pytest.raises(click.UsageError):
            DbtInvocation(dbt_target="dummy").get_selection(
                select_rules=[], exclude_rules=[]
            )

    @mock.patch("dbterd.adapters.dbt_core.dbt_invocation.dbtRunner.invoke")
    def test_get_artifacts_for_erd(self, mock_dbtRunner_invoke):
        invoker = DbtInvocation()
        _ = invoker.get_artifacts_for_erd()

        args = ["docs", "generate"]
        mock_dbtRunner_invoke.assert_called_once_with(
            [
                *["--quiet", "--log-level", "none"],
                *args,
                *["--project-dir", invoker.project_dir],
            ]
        )
