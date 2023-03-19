from pathlib import Path
from unittest import mock

import click
import pytest
from dbt_artifacts_parser import parser

from dbterd.helpers import cli_messaging, file


class TestCliMessaging:
    def test_check_existence_invalid_dir(self):
        with pytest.raises(click.FileError):
            cli_messaging.check_existence(path_str="not-exist-dir", filename="dummy")

    def test_check_existence_invalid_file(self):
        with pytest.raises(click.FileError):
            cli_messaging.check_existence(path_str=str(Path.cwd()), filename="dummy")

    @mock.patch("dbterd.helpers.file.open_json")
    def test_handle_read_errors(self, mock_file_open_json):
        mock_file_open_json.return_value = "not json"
        with pytest.raises(click.FileError):
            with cli_messaging.handle_read_errors("dummy-file", "dummy-message"):
                parser.parse_catalog(catalog=file.open_json("dummy-path"))
