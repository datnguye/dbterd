from pathlib import Path


def default_manifest_path():
    paths = list(Path.cwd().parents)
    paths.insert(0, Path.cwd())
    return str(
        next((x for x in paths if (x / "/target/manifest.json").exists()), Path.cwd())
        / "targets"
    )


def default_target():
    return "dbml"


def deafult_algo():
    return "test_relationship"
