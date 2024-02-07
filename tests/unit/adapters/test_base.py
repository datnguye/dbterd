from pathlib import Path
from unittest import mock

import click
import pytest

from dbterd import default
from dbterd.adapters.base import Executor
from dbterd.adapters.dbt_core.dbt_invocation import DbtInvocation


class TestBase:
    @mock.patch("dbterd.adapters.base.Executor.evaluate_kwargs")
    @mock.patch("dbterd.adapters.base.Executor._Executor__run_metadata_by_strategy")
    def test_run_metadata(self, mock_run_metadata_by_strategy, mock_evaluate_kwargs):
        Executor(ctx=click.Context(command=click.BaseCommand("dummy"))).run_metadata()
        mock_evaluate_kwargs.assert_called_once()
        mock_run_metadata_by_strategy.assert_called_once()

    @mock.patch("dbterd.adapters.base.DbtCloudMetadata.query_erd_data")
    @mock.patch("dbterd.adapters.base.Executor._Executor__save_result")
    def test___run_metadata_by_strategy(self, mock_query_erd_data, mock_save_result):
        Executor(
            ctx=click.Context(command=click.BaseCommand("dummy"))
        )._Executor__run_metadata_by_strategy(target="dbml", algo="test_relationship")
        mock_query_erd_data.assert_called_once()
        mock_save_result.assert_called_once()

    @mock.patch("builtins.open")
    def test___save_result(self, mock_open):
        Executor(
            ctx=click.Context(command=click.BaseCommand("dummy"))
        )._Executor__save_result(path="irrelevant", data=("file_name", {}))
        mock_open.assert_called_once_with("irrelevant/file_name", "w")

    @mock.patch("dbterd.adapters.base.DbtCloudArtifact.get")
    @mock.patch("dbterd.adapters.base.Executor._Executor__read_manifest")
    @mock.patch("dbterd.adapters.base.Executor._Executor__read_catalog")
    @mock.patch("dbterd.adapters.base.Executor._Executor__save_result")
    def test___run_by_strategy_w_dbt_cloud(
        self,
        mock_cloud_artifact_get,
        mock_read_manifest,
        mock_read_catalog,
        mock_save_result,
    ):
        Executor(
            ctx=click.Context(command=click.BaseCommand("dummy"))
        )._Executor__run_by_strategy(
            target="dbml", algo="test_relationship", dbt_cloud=True
        )
        mock_cloud_artifact_get.assert_called_once()
        mock_read_manifest.assert_called_once()
        mock_read_catalog.assert_called_once()
        mock_save_result.assert_called_once()

    def test_worker(self):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        assert worker.filename_manifest == "manifest.json"
        assert worker.filename_catalog == "catalog.json"

    def test___read_manifest(self):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        with mock.patch(
            "dbterd.helpers.file.read_manifest", return_value=dict({})
        ) as mock_read_manifest:
            with mock.patch(
                "dbterd.helpers.cli_messaging.check_existence"
            ) as mock_check_existence:
                assert worker._Executor__read_manifest(mp=Path.cwd()) == dict({})
        mock_check_existence.assert_called_once_with(Path.cwd(), "manifest.json")
        mock_read_manifest.assert_called_once_with(path=Path.cwd(), version=None)

    def test___read_catalog(self):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        with mock.patch(
            "dbterd.helpers.file.read_catalog", return_value=dict({})
        ) as mock_read_catalog:
            with mock.patch(
                "dbterd.helpers.cli_messaging.check_existence"
            ) as mock_check_existence:
                assert worker._Executor__read_catalog(cp=Path.cwd()) == dict({})
        mock_check_existence.assert_called_once_with(Path.cwd(), "catalog.json")
        mock_read_catalog.assert_called_once_with(path=Path.cwd(), version=None)

    @mock.patch(
        "dbterd.adapters.base.DbtInvocation.get_selection", return_value="dummy"
    )
    def test__get_selection(self, mock_dbt_invocation):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        worker.dbt = DbtInvocation()
        assert "dummy" == worker._Executor__get_selection(
            select_rules=[], exclude_rules=[]
        )
        mock_dbt_invocation.assert_called_once()

    @mock.patch(
        "dbterd.adapters.base.DbtInvocation.get_selection", return_value="dummy"
    )
    def test__get_selection__error(self, mock_dbt_invocation):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        with pytest.raises(click.UsageError):
            worker._Executor__get_selection()

    @pytest.mark.parametrize(
        "command, kwargs, expected",
        [
            (
                "run",
                dict(
                    select=[],
                    exclude=[],
                ),
                dict(
                    artifacts_dir="/path/ad",
                    dbt_project_dir="/path/dpd",
                    select=[],
                    exclude=[],
                ),
            ),
            (
                "run",
                dict(select=[], exclude=[], dbt=True),
                dict(
                    dbt=True,
                    artifacts_dir="/path/ad",
                    dbt_project_dir="/path/dpd",
                    select=["yolo"],
                    exclude=[],
                ),
            ),
            (
                "run",
                dict(select=[], exclude=[], dbt=True, dbt_auto_artifacts=True),
                dict(
                    dbt=True,
                    dbt_auto_artifacts=True,
                    artifacts_dir="/path/dpd/target",
                    dbt_project_dir="/path/dpd",
                    select=["yolo"],
                    exclude=[],
                ),
            ),
            (
                "run",
                dict(select=[], exclude=[], dbt_cloud=True),
                dict(
                    dbt_cloud=True,
                    artifacts_dir="/path/dpd/target",
                    dbt_project_dir="/path/dpd",
                    select=[],
                    exclude=[],
                ),
            ),
        ],
    )
    @mock.patch("dbterd.adapters.base.Executor._Executor__get_dir")
    @mock.patch("dbterd.adapters.base.Executor._Executor__get_selection")
    @mock.patch("dbterd.adapters.base.DbtInvocation.get_artifacts_for_erd")
    def test_evaluate_kwargs(
        self,
        mock_get_artifacts_for_erd,
        mock_get_selection,
        mock_get_dir,
        command,
        kwargs,
        expected,
    ):
        worker = Executor(ctx=click.Context(command=click.BaseCommand(command)))
        mock_get_dir.return_value = ("/path/ad", "/path/dpd")
        mock_get_selection.return_value = ["yolo"]
        assert expected == worker.evaluate_kwargs(**kwargs)
        mock_get_dir.assert_called_once()
        if command == "run":
            if kwargs.get("dbt") and kwargs.get("dbt_auto_artifacts"):
                mock_get_artifacts_for_erd.assert_called_once()
        else:
            assert mock_get_artifacts_for_erd.called_count == 0

    @pytest.mark.parametrize(
        "kwargs, mock_isfile_se, expected",
        [
            (
                dict(artifacts_dir=Path.cwd(), dbt_project_dir=Path.cwd()),
                [False],
                (str(f"{Path.cwd()}/target"), str(Path.cwd())),
            ),
            (
                dict(artifacts_dir=Path.cwd(), dbt_project_dir=Path.cwd()),
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                dict(artifacts_dir=None, dbt_project_dir=Path.cwd()),
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                dict(artifacts_dir=Path.cwd(), dbt_project_dir=None),
                [True],
                (str(Path.cwd()), str(Path.cwd())),
            ),
            (
                dict(artifacts_dir="", dbt_project_dir=""),
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
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        mock_isfile.side_effect = mock_isfile_se
        assert worker._Executor__get_dir(**kwargs) == expected
