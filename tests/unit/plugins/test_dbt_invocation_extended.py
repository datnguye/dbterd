from unittest import mock

from dbt.cli.main import dbtRunnerResult

from dbterd.plugins.dbt_core.dbt_invocation import DbtInvocation


class TestDbtInvocationExtended:
    @mock.patch("dbt.cli.main.dbtRunner.invoke")
    def test_invoke_with_none_args(self, mock_dbt_runner_invoke):
        """Test __invoke with None runner_args parameter."""
        with mock.patch("importlib.util.find_spec") as mock_find_spec:
            # Setup to avoid the dbt import error
            mock_spec = mock.MagicMock()
            mock_spec.loader = mock.MagicMock()
            mock_spec.submodule_search_locations = ["/fake/path"]
            mock_find_spec.return_value = mock_spec

            mock_dbt_runner_invoke.return_value = dbtRunnerResult(success=True, result={})

            # Test with None runner_args
            invoker = DbtInvocation()
            invoker._DbtInvocation__invoke(runner_args=None)

            # Should have called invoke with just the default args
            mock_dbt_runner_invoke.assert_called_once_with(
                ["--quiet", "--log-level", "none", "--project-dir", invoker.project_dir]
            )

    @mock.patch("dbt.cli.main.dbtRunner.invoke")
    def test_get_selection_with_none_params(self, mock_dbt_runner_invoke):
        """Test get_selection with None parameters."""
        with mock.patch("importlib.util.find_spec") as mock_find_spec:
            # Setup to avoid the dbt import error
            mock_spec = mock.MagicMock()
            mock_spec.loader = mock.MagicMock()
            mock_spec.submodule_search_locations = ["/fake/path"]
            mock_find_spec.return_value = mock_spec

            mock_dbt_runner_invoke.return_value = dbtRunnerResult(success=True, result=["pkg.model"])

            # Create invoker
            invoker = DbtInvocation()

            # Test with None select and None exclude
            result = invoker.get_selection(select_rules=None, exclude_rules=None)
            assert result == ["exact:model.pkg.model"]

            # Should have called invoke with the correct args
            mock_dbt_runner_invoke.assert_called_with(
                [
                    "--quiet",
                    "--log-level",
                    "none",
                    "ls",
                    "--resource-type",
                    "model",
                    "--project-dir",
                    invoker.project_dir,
                ]
            )
