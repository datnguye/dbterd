import contextlib
from enum import Enum
import types
from typing import Optional
from unittest import mock

from artifact_parser.core.exceptions import ArtifactParserError
from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError
import pytest

from dbterd.helpers import file


@contextlib.contextmanager
def _patch_parser_import(fake_module: types.ModuleType):
    """Intercept only the artifact-parser model import, delegating everything else.

    A blanket ``__import__`` mock would also hijack Pydantic's own internal imports,
    so we route just the parser module to the fake and pass the rest through.
    """
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("artifact_parser.dbt.generated.models."):
            return fake_module
        return real_import(name, *args, **kwargs)

    with mock.patch("builtins.__import__", side_effect=fake_import):
        yield


def _build_fake_parser_module(artifact: str, version: int) -> types.ModuleType:
    """Build a throwaway parser-like module mirroring the artifact-parser layout.

    Patching against real parser models would mutate global parser state across the
    test session, so each test gets its own isolated module with fresh model classes.
    """

    class SupportedLanguage(str, Enum):
        python = "python"
        sql = "sql"

    class ConstraintType(str, Enum):
        primary_key = "primary_key"
        foreign_key = "foreign_key"

    class Metadata(BaseModel):
        model_config = ConfigDict(extra="forbid")
        name: Optional[str] = None

    class Macros(BaseModel):
        model_config = ConfigDict(extra="forbid")
        name: Optional[str] = None
        supported_languages: Optional[list[SupportedLanguage]] = None
        # PEP 604 union (`X | None`) exercises the types.UnionType rebuild branch.
        primary_language: SupportedLanguage | None = None
        # `type` is a consumed enum field (read via `.value`) and must stay an enum.
        type: Optional[ConstraintType] = None

    module = types.ModuleType(f"{artifact.lower()}_v{version}")
    module.SupportedLanguage = SupportedLanguage
    module.ConstraintType = ConstraintType
    module.Metadata = Metadata
    module.Macros = Macros
    setattr(module, f"{artifact}V{version}", Macros)
    return module


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
        with pytest.raises(ArtifactParserError):
            file.read_manifest(path="path/to/manifest", version=version)
        mock_open_json.assert_called_with("path/to/manifest/manifest.json")

    @mock.patch("dbterd.helpers.file.patch_parser_compatibility")
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_manifest_with_compat_patch(self, mock_open_json, mock_patch):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ArtifactParserError):
            file.read_manifest(path="path/to/manifest", version=12, policies=["relax_extra_fields"])
        mock_patch.assert_called_once_with(artifact="manifest", artifact_version=12, policies=["relax_extra_fields"])

    @pytest.mark.parametrize("version", [(-1), (1)])
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_catalog_error(self, mock_open_json, version):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ArtifactParserError):
            file.read_catalog(path="path/to/catalog", version=version)
        mock_open_json.assert_called_with("path/to/catalog/catalog.json")

    @mock.patch("dbterd.helpers.file.patch_parser_compatibility")
    @mock.patch("dbterd.helpers.file.open_json")
    def test_read_catalog_with_compat_patch(self, mock_open_json, mock_patch):
        mock_open_json.return_value = {"data": "dummy"}
        with pytest.raises(ArtifactParserError):
            file.read_catalog(path="path/to/catalog", version=1, policies=["relax_extra_fields"])
        mock_patch.assert_called_once_with(artifact="catalog", artifact_version=1, policies=["relax_extra_fields"])

    @mock.patch("builtins.open")
    def test_write_json(self, mock_open):
        file.write_json(data={}, path="path/to/catalog/catalog.json")
        mock_open.assert_called_with("path/to/catalog/catalog.json", "w", encoding="utf-8")

    def test_patch_parser_compatibility_catalog(self):
        fake_module = _build_fake_parser_module("Catalog", 1)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="catalog", artifact_version=1)

        assert fake_module.Metadata.model_config["extra"] == "ignore"

    def test_patch_parser_compatibility_manifest(self):
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12)

        # Every forbid-ing model is relaxed, not just Metadata.
        assert fake_module.Metadata.model_config["extra"] == "ignore"
        assert fake_module.Macros.model_config["extra"] == "ignore"

    def test_patch_parser_compatibility_tolerates_extra_field(self):
        """dbt 1.11 added a `config` property to macro nodes (same manifest v12)."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12)

        instance = fake_module.Macros(name="m", config={"meta": {}})
        assert instance.name == "m"

    def test_patch_parser_compatibility_tolerates_unknown_enum_value(self):
        """dbt 1.11 added `javascript` to supported_languages enum (same manifest v12)."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12)

        instance = fake_module.Macros(
            name="m",
            supported_languages=["python", "javascript"],
            primary_language="javascript",
        )
        # The non-consumed enum fields are widened to str, so unknown values pass.
        assert instance.supported_languages == ["python", "javascript"]
        assert instance.primary_language == "javascript"

    def test_patch_parser_compatibility_preserves_consumed_enum_field(self):
        """`type` fields are read via `.value` by dbterd and must remain enums."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12)

        instance = fake_module.Macros(name="m", type="primary_key")
        assert isinstance(instance.type, fake_module.ConstraintType)
        assert instance.type.value == "primary_key"

    def test_patch_parser_compatibility_empty_policies_skips_patching(self):
        """An empty policy list applies no relaxation: extra fields still rejected."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12, policies=[])

        with pytest.raises(PydanticValidationError):
            fake_module.Macros(name="m", config={"meta": {}})

    def test_patch_parser_compatibility_single_policy(self):
        """Only the listed policy runs: extra fields relaxed but enums stay strict."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12, policies=["relax_extra_fields"])

        # Extra field is tolerated...
        assert fake_module.Macros(name="m", config={"meta": {}}).name == "m"
        # ...but an unknown enum value is still rejected (relax_enum_values not listed).
        with pytest.raises(PydanticValidationError):
            fake_module.Macros(name="m", supported_languages=["javascript"])

    def test_patch_parser_compatibility_unknown_policy_raises(self):
        """An unregistered policy name raises a helpful error."""
        fake_module = _build_fake_parser_module("Manifest", 12)
        with _patch_parser_import(fake_module), pytest.raises(ValueError, match="Unknown validation policy"):
            file.patch_parser_compatibility(artifact="manifest", artifact_version=12, policies=["nope"])

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
