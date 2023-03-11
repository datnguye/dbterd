from pathlib import Path


def default_artifact_path() -> str:
    return str(Path.cwd() / "target")


def default_output_path() -> str:
    return str(Path.cwd() / "target")


def default_target() -> str:
    return "dbml"


def deafult_algo() -> str:
    return "test_relationship"
