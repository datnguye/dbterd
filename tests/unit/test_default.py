import os
from pathlib import Path

import pytest

from dbterd import default


class TestDefault:
    def test_default_artifact_path(self):
        assert default.default_artifact_path() == os.environ.get("DBTERD_ARTIFACT_PATH", str(Path.cwd() / "target"))

    def test_default_output_path(self):
        assert default.default_output_path() == os.environ.get("DBTERD_OUTPUT_PATH", str(Path.cwd() / "target"))

    @pytest.mark.parametrize("target", [("dbml")])
    def test_default_target(self, target):
        assert default.default_target() == os.environ.get("DBTERD_TARGET", target)

    @pytest.mark.parametrize("algo", [("test_relationship")])
    def test_default_algo(self, algo):
        assert default.default_algo() == os.environ.get("DBTERD_ALGO", algo)

    def test_default_resource_types_with_list(self, monkeypatch):
        """Test default_resource_types when DBTERD_RESOURCE_TYPES is a list."""
        test_list = ["model", "source"]
        monkeypatch.setattr(
            os.environ, "get", lambda *args, **kwargs: test_list if args[0] == "DBTERD_RESOURCE_TYPES" else None
        )
        assert default.default_resource_types() == test_list

    def test_default_entity_name_format(self):
        """Test default_entity_name_format returns the expected value."""
        expected = os.environ.get("DBTERD_ENTITY_NAME_FORMAT", "resource.package.model")
        assert default.default_entity_name_format() == expected

    def test_default_manifest_version_from_env(self, monkeypatch):
        """Test default_manifest_version returns environment variable when set."""
        monkeypatch.setenv("DBTERD_MANIFEST_VERSION", "11")
        assert default.default_manifest_version() == "11"

    def test_default_catalog_version_from_env(self, monkeypatch):
        """Test default_catalog_version returns environment variable when set."""
        monkeypatch.setenv("DBTERD_CATALOG_VERSION", "2")
        assert default.default_catalog_version() == "2"

    def test_default_manifest_version_with_none_artifacts_dir(self, tmp_path, monkeypatch):
        """Test default_manifest_version falls back to default paths when artifacts_dir is None."""
        monkeypatch.delenv("DBTERD_MANIFEST_VERSION", raising=False)
        monkeypatch.setenv("DBTERD_ARTIFACTS_DIR", "")
        monkeypatch.setenv("DBTERD_ARTIFACT_PATH", str(tmp_path))

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v11.json"}}'
        )

        assert default.default_manifest_version(None) == "11"

    def test_default_manifest_version_with_json_decode_error(self, tmp_path, monkeypatch):
        """Test default_manifest_version handles JSON decode errors gracefully."""
        monkeypatch.delenv("DBTERD_MANIFEST_VERSION", raising=False)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text("invalid json{")

        assert default.default_manifest_version(str(tmp_path)) is None

    def test_default_manifest_version_with_key_error(self, tmp_path, monkeypatch):
        """Test default_manifest_version handles missing keys gracefully."""
        monkeypatch.delenv("DBTERD_MANIFEST_VERSION", raising=False)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{"metadata": {}}')

        assert default.default_manifest_version(str(tmp_path)) is None

    def test_default_catalog_version_with_none_artifacts_dir(self, tmp_path, monkeypatch):
        """Test default_catalog_version falls back to default paths when artifacts_dir is None."""
        monkeypatch.delenv("DBTERD_CATALOG_VERSION", raising=False)
        monkeypatch.setenv("DBTERD_ARTIFACTS_DIR", "")
        monkeypatch.setenv("DBTERD_ARTIFACT_PATH", str(tmp_path))

        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text(
            '{"metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/catalog/v2.json"}}'
        )

        assert default.default_catalog_version(None) == "2"

    def test_default_catalog_version_with_json_decode_error(self, tmp_path, monkeypatch):
        """Test default_catalog_version handles JSON decode errors gracefully."""
        monkeypatch.delenv("DBTERD_CATALOG_VERSION", raising=False)
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text("invalid json{")

        assert default.default_catalog_version(str(tmp_path)) is None

    def test_default_catalog_version_with_key_error(self, tmp_path, monkeypatch):
        """Test default_catalog_version handles missing keys gracefully."""
        monkeypatch.delenv("DBTERD_CATALOG_VERSION", raising=False)
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text('{"metadata": {}}')

        assert default.default_catalog_version(str(tmp_path)) is None
