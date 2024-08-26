import os
from pathlib import Path
from typing import List


def default_artifact_path() -> str:
    return os.environ.get("DBTERD_ARTIFACT_PATH", str(Path.cwd() / "target"))


def default_output_path() -> str:
    return os.environ.get("DBTERD_OUTPUT_PATH", str(Path.cwd() / "target"))


def default_target() -> str:
    return os.environ.get("DBTERD_TARGET", "dbml")


def default_algo() -> str:
    return os.environ.get("DBTERD_ALGO", "test_relationship")


def default_resource_types() -> List[str]:
    return os.environ.get("DBTERD_RESOURCE_TYPES", ["model"])


def default_entity_name_format() -> str:
    return os.environ.get("DBTERD_ENTITY_NAME_FORMAT", "resource.package.model")
