import contextlib
from pathlib import Path
from unittest import mock

import click
import pytest

from dbterd import default
from dbterd.core.base import Executor
from dbterd.plugins.dbt_core.dbt_invocation import DbtInvocation


class TestBase:
    @mock.patch("dbterd.core.base.Executor.evaluate_kwargs")
    @mock.patch("dbterd.core.base.Executor._Executor__run_metadata_by_strategy")
    def test_run_metadata(self, mock_run_metadata_by_strategy, mock_evaluate_kwargs):
        Executor(ctx=click.Context(command=click.Command("dummy"))).run_metadata()
        mock_evaluate_kwargs.assert_called_once()
        mock_run_metadata_by_strategy.assert_called_once()

    @mock.patch("dbterd.core.base.DbtCloudMetadata.query_erd_data")
    @mock.patch("dbterd.core.base.Executor._Executor__save_result")
    def test___run_metadata_by_strategy(self, mock_query_erd_data, mock_save_result):
        Executor(ctx=click.Context(command=click.Command("dummy")))._Executor__run_metadata_by_strategy(
            target="dbml", algo="test_relationship"
        )
        mock_query_erd_data.assert_called_once()
        mock_save_result.assert_called_once()

    @mock.patch("dbterd.core.base.DbtCloudMetadata.query_erd_data")
    @mock.patch("dbterd.core.base.Executor._Executor__save_result")
    def test___run_metadata_by_strategy_with_not_implemented_algo(self, mock_save_result, mock_query_erd_data):
        with pytest.raises(Exception) as excinfo:
            Executor(ctx=click.Context(command=click.Command("dummy")))._Executor__run_metadata_by_strategy(
                target="dbml", algo="notfound"
            )
        assert "Parser 'notfound' not found in registry" in str(excinfo.value)
        mock_query_erd_data.assert_called_once()
        assert mock_save_result.call_count == 0

    @mock.patch("builtins.open")
    def test___save_result(self, mock_open):
        Executor(ctx=click.Context(command=click.Command("dummy")))._Executor__save_result(
            path="irrelevant", data=("file_name", {})
        )
        mock_open.assert_called_once_with("irrelevant/file_name", "w")

    @mock.patch("dbterd.core.base.DbtCloudArtifact.get")
    @mock.patch("dbterd.core.base.Executor._Executor__read_manifest")
    @mock.patch("dbterd.core.base.Executor._Executor__read_catalog")
    @mock.patch("dbterd.core.base.Executor._Executor__save_result")
    def test___run_by_strategy_w_dbt_cloud(
        self,
        mock_cloud_artifact_get,
        mock_read_manifest,
        mock_read_catalog,
        mock_save_result,
    ):
        Executor(ctx=click.Context(command=click.Command("dummy")))._Executor__run_by_strategy(
            target="dbml", algo="test_relationship", dbt_cloud=True
        )
        mock_cloud_artifact_get.assert_called_once()
        mock_read_manifest.assert_called_once()
        mock_read_catalog.assert_called_once()
        mock_save_result.assert_called_once()

    def test_worker(self):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        assert worker.filename_manifest == "manifest.json"
        assert worker.filename_catalog == "catalog.json"

    @pytest.mark.parametrize(
        "mv, default_version_return, expected_version, should_call_default",
        [
            (None, None, None, True),
            (None, "12", 12, True),
            (10, "12", 10, False),
        ],
    )
    def test___read_manifest(self, mv, default_version_return, expected_version, should_call_default):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        with contextlib.ExitStack() as stack:
            mock_read_manifest = stack.enter_context(mock.patch("dbterd.helpers.file.read_manifest", return_value={}))
            mock_check_existence = stack.enter_context(mock.patch("dbterd.helpers.cli_messaging.check_existence"))
            mock_default_manifest_version = stack.enter_context(
                mock.patch("dbterd.default.default_manifest_version", return_value=default_version_return)
            )
            assert worker._Executor__read_manifest(mp=Path.cwd(), mv=mv) == {}
        mock_check_existence.assert_called_once_with(Path.cwd(), "manifest.json")
        if should_call_default:
            mock_default_manifest_version.assert_called_once_with(artifacts_dir=Path.cwd())
        else:
            assert mock_default_manifest_version.call_count == 0
        mock_read_manifest.assert_called_once_with(path=Path.cwd(), version=expected_version, enable_compat_patch=False)

    @pytest.mark.parametrize(
        "cv, default_version_return, expected_version, should_call_default",
        [
            (None, None, None, True),
            (None, "12", 12, True),
            (10, "12", 10, False),
        ],
    )
    def test___read_catalog(self, cv, default_version_return, expected_version, should_call_default):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        with contextlib.ExitStack() as stack:
            mock_read_catalog = stack.enter_context(mock.patch("dbterd.helpers.file.read_catalog", return_value={}))
            mock_check_existence = stack.enter_context(mock.patch("dbterd.helpers.cli_messaging.check_existence"))
            mock_default_catalog_version = stack.enter_context(
                mock.patch("dbterd.default.default_catalog_version", return_value=default_version_return)
            )
            assert worker._Executor__read_catalog(cp=Path.cwd(), cv=cv) == {}
        mock_check_existence.assert_called_once_with(Path.cwd(), "catalog.json")
        if should_call_default:
            mock_default_catalog_version.assert_called_once_with(artifacts_dir=Path.cwd())
        else:
            assert mock_default_catalog_version.call_count == 0
        mock_read_catalog.assert_called_once_with(path=Path.cwd(), version=expected_version, enable_compat_patch=False)

    @mock.patch("dbterd.core.base.DbtInvocation.get_selection", return_value="dummy")
    def test__get_selection(self, mock_dbt_invocation):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        worker.dbt = DbtInvocation()
        assert worker._Executor__get_selection(select_rules=[], exclude_rules=[]) == "dummy"
        mock_dbt_invocation.assert_called_once()

    @mock.patch("dbterd.core.base.DbtInvocation.get_selection", return_value="dummy")
    def test__get_selection__error(self, mock_dbt_invocation):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        with pytest.raises(click.UsageError):
            worker._Executor__get_selection()

    @pytest.mark.parametrize(
        "command, kwargs, select_result, expected",
        [
            (
                "run",
                {
                    "select": [],
                    "exclude": [],
                },
                ["yolo"],
                {
                    "artifacts_dir": "/path/ad",
                    "dbt_project_dir": "/path/dpd",
                    "select": [],
                    "exclude": [],
                },
            ),
            (
                "run",
                {"select": ["dummy"], "exclude": [], "dbt": True},
                [],
                {
                    "dbt": True,
                    "artifacts_dir": "/path/ad",
                    "dbt_project_dir": "/path/dpd",
                    "select": ["exact:none"],
                    "exclude": [],
                },
            ),
            (
                "run",
                {"select": [], "exclude": [], "dbt": True},
                ["yolo"],
                {
                    "dbt": True,
                    "artifacts_dir": "/path/ad",
                    "dbt_project_dir": "/path/dpd",
                    "select": ["yolo"],
                    "exclude": [],
                },
            ),
            (
                "run",
                {"select": [], "exclude": [], "dbt": True, "dbt_auto_artifacts": True},
                ["yolo"],
                {
                    "dbt": True,
                    "dbt_auto_artifacts": True,
                    "artifacts_dir": "/path/dpd/target",
                    "dbt_project_dir": "/path/dpd",
                    "select": ["yolo"],
                    "exclude": [],
                },
            ),
            (
                "run",
                {"select": [], "exclude": [], "dbt_cloud": True},
                ["yolo"],
                {
                    "dbt_cloud": True,
                    "artifacts_dir": "/path/dpd/target",
                    "dbt_project_dir": "/path/dpd",
                    "select": [],
                    "exclude": [],
                },
            ),
        ],
    )
    @mock.patch("dbterd.core.base.Executor._Executor__check_if_any_unsupported_selection")
    @mock.patch("dbterd.core.base.Executor._Executor__get_dir")
    @mock.patch("dbterd.core.base.Executor._Executor__get_selection")
    @mock.patch("dbterd.core.base.DbtInvocation.get_artifacts_for_erd")
    def test_evaluate_kwargs(
        self,
        mock_get_artifacts_for_erd,
        mock_get_selection,
        mock_get_dir,
        mock_check_if_any_unsupported_selection,
        command,
        kwargs,
        select_result,
        expected,
    ):
        worker = Executor(ctx=click.Context(command=click.Command(command)))
        mock_get_dir.return_value = ("/path/ad", "/path/dpd")
        mock_get_selection.return_value = select_result
        assert expected == worker.evaluate_kwargs(**kwargs)
        mock_get_dir.assert_called_once()
        if not kwargs.get("dbt"):
            mock_check_if_any_unsupported_selection.assert_called_once()
        if command == "run":
            if kwargs.get("dbt") and kwargs.get("dbt_auto_artifacts"):
                mock_get_artifacts_for_erd.assert_called_once()
        else:
            assert mock_get_artifacts_for_erd.called_count == 0

    @pytest.mark.parametrize(
        "kwargs, mock_isfile_se, expected",
        [
            (
                {"artifacts_dir": Path.cwd(), "dbt_project_dir": Path.cwd()},
                [False],
                (str(f"{Path.cwd()}/target"), str(Path.cwd())),
            ),
            (
                {"artifacts_dir": Path.cwd(), "dbt_project_dir": Path.cwd()},
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                {"artifacts_dir": None, "dbt_project_dir": Path.cwd()},
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                {"artifacts_dir": Path.cwd(), "dbt_project_dir": None},
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                {"artifacts_dir": "", "dbt_project_dir": ""},
                [True],
                (
                    str(default.default_artifact_path()),
                    str(Path(default.default_artifact_path()).parent.absolute()),
                ),
            ),
        ],
    )
    @mock.patch("os.path.isfile")
    def test__get_dir(self, mock_isfile, kwargs, mock_isfile_se, expected):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        mock_isfile.side_effect = mock_isfile_se
        assert worker._Executor__get_dir(**kwargs) == expected

    def test__set_single_node_selection__none_id(self):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        assert worker._Executor__set_single_node_selection(
            manifest="irrelevant", node_unique_id=None, **{"i": "irr"}
        ) == {"i": "irr"}

    @mock.patch("dbterd.core.registry.registry.get_parser")
    def test__set_single_node_selection(self, mock_get_parser):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))
        mock_algorithm = mock.Mock()
        mock_algorithm.find_related_nodes_by_id.return_value = ["irr"]
        mock_get_parser.return_value = mock_algorithm
        assert worker._Executor__set_single_node_selection(
            manifest="irrelevant",
            node_unique_id="irrelevant",
            **{"algo": "test_relationship"},
        ) == {"algo": "test_relationship", "select": ["irr"], "exclude": []}
        assert mock_algorithm.find_related_nodes_by_id.call_count == 1

    @mock.patch("dbterd.core.base.Executor._Executor__get_operation")
    @mock.patch("dbterd.core.base.Executor._Executor__read_manifest")
    @mock.patch("dbterd.core.base.Executor._Executor__read_catalog")
    @mock.patch("dbterd.core.base.Executor._Executor__set_single_node_selection")
    def test__run_by_strategy__for_api_simple(
        self,
        mock_set_single_node_selection,
        mock_read_catalog,
        mock_read_manifest,
        mock_get_operation,
    ):
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))

        mock_parent = mock.Mock()
        mock_run_func = mock.Mock(return_value=("irr", {"i": "irr"}))
        mock_get_operation.return_value = mock_run_func
        mock_parent.attach_mock(mock_get_operation, "mock_get_operation")
        mock_read_catalog.return_value = {}
        mock_parent.attach_mock(mock_read_catalog, "mock_read_catalog")
        mock_read_manifest.return_value = {}
        mock_parent.attach_mock(mock_read_manifest, "mock_read_manifest")
        mock_set_single_node_selection.return_value = {"api": True}
        mock_parent.attach_mock(mock_set_single_node_selection, "mock_set_single_node_selection")
        mock_parent.attach_mock(mock_run_func, "mock_run_func")

        assert worker._Executor__run_by_strategy(node_unique_id="irr") == {"i": "irr"}
        assert mock_parent.mock_calls == [
            mock.call.mock_read_manifest(mp=None, mv=None, bypass_validation=None),
            mock.call.mock_read_catalog(cp=None, cv=None, bypass_validation=None),
            mock.call.mock_set_single_node_selection(manifest={}, node_unique_id="irr"),
            mock.call.mock_get_operation({"api": True}),
            mock.call.mock_run_func(manifest={}, catalog={}, **{"api": True}),
        ]
