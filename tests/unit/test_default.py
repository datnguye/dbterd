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
