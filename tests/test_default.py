from dbterd import default
from pathlib import Path


class TestDefault:
    def test_default_artifact_path(self):
        assert default.default_artifact_path() == str(Path.cwd() / "target")


    def test_default_output_path(self):
        assert default.default_output_path() == str(Path.cwd() / "target")


    def test_default_target(self):
        assert default.default_target() == "dbml"


    def test_deafult_algo(self):
        assert default.deafult_algo() == "test_relationship"
