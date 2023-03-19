from pathlib import Path

import pytest

from dbterd import default


class TestDefault:
    def test_default_artifact_path(self):
        assert default.default_artifact_path() == str(Path.cwd() / "target")

    def test_default_output_path(self):
        assert default.default_output_path() == str(Path.cwd() / "target")

    @pytest.mark.parametrize("target", [("dbml")])
    def test_default_target(self, target):
        assert default.default_target() == target

    @pytest.mark.parametrize("algo", [("test_relationship")])
    def test_deafult_algo(self, algo):
        assert default.deafult_algo() == algo
