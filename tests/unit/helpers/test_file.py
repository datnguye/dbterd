import contextlib
from unittest import mock

import pytest

from dbterd.helpers import file


class TestFile:
    @pytest.mark.parametrize(
        "schema_version, expected",
        [
            ("https://schemas.getdbt.com/dbt/manifest/v12.json", "12"),
            ("https://schemas.getdbt.com/dbt/catalog/v1.json", "1"),
            ("https://schemas.getdbt.com/dbt/manifest/v10/", "10"),
            ("v12.json", "12"),
            ("v12", "12"),
            ("invalid", None),
            ("", None),
        ],
    )
    def test_extract_artifact_version_from_file(self, schema_version, expected):
        assert file.extract_artifact_version_from_file(schema_version) == expected

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
            mock.mock_open(read_data=str.encode("data with trailing space ", encoding="utf-8")),
        ) as mock_file:
            assert file.load_file_contents(path="path/to/open", strip=False) == "data with trailing space "
            mock_file.assert_called_with("path/to/open", "rb")

    @mock.patch("dbterd.helpers.file.load_file_contents")
    def test_open_json(self, mock_load_file_contents):
        json_data = '{"data": "dummy"}'
        mock_load_file_contents.return_value = json_data
        assert file.open_json(file.load_file_contents(path="path/to/open")) == {"data": "dummy"}

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
        with contextlib.ExitStack() as stack:
            mock_supports_long_paths = stack.enter_context(
                mock.patch("dbterd.helpers.file.supports_long_paths", return_value=False)
            )
            mock_win_prepare_path = stack.enter_context(
                mock.patch("dbterd.helpers.file.win_prepare_path", return_value="win/path")
            )
            assert file.convert_path(path=path_250_noprefix) == "\\\\?\\win/path"
        mock_supports_long_paths.assert_called_once()
        mock_win_prepare_path.assert_called_with(path_250_noprefix)

    @pytest.mark.parametrize("version", [(-1), (1)])
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_manifest_error(self, mock_open_json, version):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ValueError):
            file.read_manifest(path="path/to/manifest", version=version)
        mock_open_json.assert_called_with("path/to/manifest/manifest.json")

    @mock.patch("dbterd.helpers.file.patch_parser_compatibility")
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_manifest_with_compat_patch(self, mock_open_json, mock_patch):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ValueError):
            file.read_manifest(path="path/to/manifest", version=12, enable_compat_patch=True)
        mock_patch.assert_called_once_with(artifact="manifest", artifact_version=12)

    @pytest.mark.parametrize("version", [(-1), (1)])
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_catalog_error(self, mock_open_json, version):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ValueError):
            file.read_catalog(path="path/to/catalog", version=version)
        mock_open_json.assert_called_with("path/to/catalog/catalog.json")

    @mock.patch("dbterd.helpers.file.patch_parser_compatibility")
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_catalog_with_compat_patch(self, mock_open_json, mock_patch):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ValueError):
            file.read_catalog(path="path/to/catalog", version=1, enable_compat_patch=True)
        mock_patch.assert_called_once_with(artifact="catalog", artifact_version=1)

    @mock.patch("builtins.open")
    def test_write_json(self, mock_open):
        file.write_json(data={}, path="path/to/catalog/catalog.json")
        mock_open.assert_called_with("path/to/catalog/catalog.json", "w", encoding="utf-8")

    def test_patch_parser_compatibility_catalog(self):
        with contextlib.ExitStack() as stack:
            mock_metadata = mock.MagicMock()
            mock_metadata.model_config = {"extra": "forbid"}
            mock_catalog = mock.MagicMock()

            mock_module = mock.MagicMock()
            mock_module.Metadata = mock_metadata
            mock_module.CatalogV1 = mock_catalog

            stack.enter_context(mock.patch("builtins.__import__", return_value=mock_module))

            file.patch_parser_compatibility(artifact="catalog", artifact_version=1)

            assert mock_metadata.model_config["extra"] == "ignore"
            mock_metadata.model_rebuild.assert_called_once_with(force=True)
            mock_catalog.model_rebuild.assert_called_once_with(force=True)

    def test_patch_parser_compatibility_manifest(self):
        with contextlib.ExitStack() as stack:
            mock_metadata = mock.MagicMock()
            mock_metadata.model_config = {"extra": "forbid"}
            mock_manifest = mock.MagicMock()

            mock_module = mock.MagicMock()
            mock_module.Metadata = mock_metadata
            mock_module.ManifestV12 = mock_manifest

            stack.enter_context(mock.patch("builtins.__import__", return_value=mock_module))

            file.patch_parser_compatibility(artifact="manifest", artifact_version=12)

            assert mock_metadata.model_config["extra"] == "ignore"
            mock_metadata.model_rebuild.assert_called_once_with(force=True)
            mock_manifest.model_rebuild.assert_called_once_with(force=True)

    def test_patch_parser_compatibility_import_error(self):
        with mock.patch("builtins.__import__", side_effect=ImportError("module not found")):
            file.patch_parser_compatibility(artifact="catalog", artifact_version=999)

    def test_patch_parser_compatibility_attribute_error(self):
        mock_module = mock.MagicMock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch("builtins.__import__", return_value=mock_module))
            stack.enter_context(
                mock.patch("dbterd.helpers.file.getattr", side_effect=AttributeError("class not found"))
            )

            file.patch_parser_compatibility(artifact="catalog", artifact_version=1)
