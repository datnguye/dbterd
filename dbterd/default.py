from pathlib import Path


def default_manifest_path() -> str:
    paths = list(Path.cwd().parents)
    paths.insert(0, Path.cwd())
    return str(
        next((x for x in paths if (x / "target/manifest.json").exists()), Path.cwd())
        / "target"
    )


def default_output_path() -> str:
    return str(Path.cwd() / "target")


def default_target() -> str:
    return "dbml"


def deafult_algo() -> str:
    return "test_relationship"
