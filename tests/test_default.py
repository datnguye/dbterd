from dbterd import default
from pathlib import Path


def test_default_manifest_path():
    assert default.default_manifest_path() == str(Path.cwd() / "target")


def test_default_output_path():
    assert default.default_output_path() == str(Path.cwd() / "target")


def test_default_target():
    assert default.default_target() == "dbml"


def test_deafult_algo():
    assert default.deafult_algo() == "test_relationship"
