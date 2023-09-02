from pathlib import Path
from unittest import mock

import click

from dbterd.adapters.worker import DbtWorker


class TestBase:
    # .run(
    #     target="dbml",
    #     algo="test_relationship",
    #     artifacts_dir="/",
    #     output="/"
    # )

    def test_worker(self):
        worker = DbtWorker(ctx=click.Context(command=click.BaseCommand("dummy")))
        assert worker.filename_manifest == "manifest.json"
        assert worker.filename_catalog == "catalog.json"

    def test___read_manifest(self):
        worker = DbtWorker(ctx=click.Context(command=click.BaseCommand("dummy")))
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
        worker = DbtWorker(ctx=click.Context(command=click.BaseCommand("dummy")))
        with mock.patch(
            "dbterd.helpers.file.read_catalog", return_value=dict({})
        ) as mock_read_catalog:
            with mock.patch(
                "dbterd.helpers.cli_messaging.check_existence"
            ) as mock_check_existence:
                assert worker._Executor__read_catalog(cp=Path.cwd()) == dict({})
        mock_check_existence.assert_called_once_with(Path.cwd(), "catalog.json")
        mock_read_catalog.assert_called_once_with(path=Path.cwd(), version=None)
