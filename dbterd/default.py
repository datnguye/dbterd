from pathlib import Path
from typing import List


def default_artifact_path() -> str:
    return str(Path.cwd() / "target")


def default_output_path() -> str:
    return str(Path.cwd() / "target")


def default_target() -> str:
    return "dbml"


def default_algo() -> str:
    return "test_relationship"


def default_resource_types() -> List[str]:
    return ["model"]


def default_entity_name_format() -> str:
    return "resource.package.model"
