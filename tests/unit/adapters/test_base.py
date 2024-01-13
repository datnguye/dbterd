from pathlib import Path
from unittest import mock

import click
import pytest

from dbterd import default
from dbterd.adapters.base import Executor
from dbterd.adapters.dbt_invocation import DbtInvocation


class TestBase:
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
        "kwargs, expected",
        [
            (
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
    @mock.patch("dbterd.adapters.dbt_cloud.DbtCloudArtifact.get")
    @mock.patch("dbterd.adapters.base.Executor._Executor__get_dir")
    @mock.patch("dbterd.adapters.base.Executor._Executor__get_selection")
    @mock.patch("dbterd.adapters.base.DbtInvocation.get_artifacts_for_erd")
    def test_evaluate_kwargs(
        self,
        mock_get_artifacts_for_erd,
        mock_get_selection,
        mock_get_dir,
        mock_dbt_cloud_get,
        kwargs,
        expected,
    ):
        worker = Executor(ctx=click.Context(command=click.BaseCommand("dummy")))
        mock_get_dir.return_value = ("/path/ad", "/path/dpd")
        mock_get_selection.return_value = ["yolo"]
        assert expected == worker.evaluate_kwargs(**kwargs)
        mock_get_dir.assert_called_once()
        if kwargs.get("dbt_auto_artifacts"):
            mock_get_artifacts_for_erd.assert_called_once()
        if kwargs.get("dbt_cloud"):
            mock_dbt_cloud_get.assert_called_once()

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
