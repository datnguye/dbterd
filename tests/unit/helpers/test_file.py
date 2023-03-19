from unittest import mock

import pytest

from dbterd.helpers import file


class TestFile:
    def test_load_file_contents(self):
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data=str.encode("data", encoding="utf-8")),
        ) as mock_file:
            assert file.load_file_contents(path="path/to/open") == "data"
        mock_file.assert_called_with("path/to/open", "rb")

    def test_load_file_contents_without_strip(self):
        with mock.patch(
            "builtins.open",
            mock.mock_open(
                read_data=str.encode("data with trailing space ", encoding="utf-8")
            ),
        ) as mock_file:
            assert (
                file.load_file_contents(path="path/to/open", strip=False)
                == "data with trailing space "
            )
            mock_file.assert_called_with("path/to/open", "rb")

    @mock.patch("dbterd.helpers.file.load_file_contents")
    def test_open_json(self, mock_load_file_contents):
        json_data = '{"data": "dummy"}'
        mock_load_file_contents.return_value = json_data
        assert file.open_json(file.load_file_contents(path="path/to/open")) == dict(
            {"data": "dummy"}
        )

    def test_convert_path_length_249(self):
        path_249 = 249 * "x"
        assert file.convert_path(path=path_249) == path_249

    @mock.patch("dbterd.helpers.file.supports_long_paths", return_value=True)
    def test_convert_path_supports_long_paths(self, mock_supports_long_paths):
        path_250 = 250 * "x"
        assert file.convert_path(path=path_250) == path_250
        mock_supports_long_paths.assert_called_once()

    @mock.patch("dbterd.helpers.file.supports_long_paths", return_value=False)
    def test_convert_path_not_supports_long_path_1(self, mock_supports_long_paths):
        path_250_prefix = "\\\\?\\" + 250 * "x"  # with prefix
        assert file.convert_path(path=path_250_prefix) == path_250_prefix
        mock_supports_long_paths.assert_called_once()

    def test_convert_path_not_supports_long_path_2(self):
        path_250_noprefix = 250 * "x"
        with mock.patch(
            "dbterd.helpers.file.supports_long_paths", return_value=False
        ) as mock_supports_long_paths:
            with mock.patch(
                "dbterd.helpers.file.win_prepare_path", return_value="win/path"
            ) as mock_win_prepare_path:
                assert file.convert_path(path=path_250_noprefix) == "\\\\?\\win/path"
        mock_supports_long_paths.assert_called_once()
        mock_win_prepare_path.assert_called_with(path_250_noprefix)

    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_manifest_error(self, mock_open_json):
        mock_open_json.return_value = dict({"data": "dummy"})
        with pytest.raises(ValueError):
            file.read_manifest(path="path/to/manifest")
        mock_open_json.assert_called_with("path/to/manifest/manifest.json")

    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_catalog_error(self, mock_open_json):
        mock_open_json.return_value = dict({"data": "dummy"})
        with pytest.raises(ValueError):
            file.read_catalog(path="path/to/catalog")
        mock_open_json.assert_called_with("path/to/catalog/catalog.json")
