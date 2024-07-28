import os
from pathlib import Path

import pytest

from dbterd import default


class TestDefault:
    def test_default_artifact_path(self):
        assert default.default_artifact_path() == os.environ.get(
            "DBTERD_ARTIFACT_PATH", str(Path.cwd() / "target")
        )

    def test_default_output_path(self):
        assert default.default_output_path() == os.environ.get(
            "DBTERD_OUTPUT_PATH", str(Path.cwd() / "target")
        )

    @pytest.mark.parametrize("target", [("dbml")])
    def test_default_target(self, target):
        assert default.default_target() == os.environ.get("DBTERD_TARGET", target)

    @pytest.mark.parametrize("algo", [("test_relationship")])
    def test_default_algo(self, algo):
        assert default.default_algo() == os.environ.get("DBTERD_ALGO", algo)
