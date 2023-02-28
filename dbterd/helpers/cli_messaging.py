import contextlib
import json
from pathlib import Path

import click


@contextlib.contextmanager
def handle_read_errors(filename, conditional_msg: str = ""):
    try:
        yield
    except (json.JSONDecodeError, ValueError):
        raise click.FileError(
            filename,
            f"File {filename} is corrupted{conditional_msg}, please rebuild",
        )


def check_existence(path_str: str, filename: str) -> None:
    path = Path(path_str)
    if not path.is_dir():
        raise click.FileError(filename, f"Path {path_str} does not exist")
    elif not (path / filename).is_file():
        raise click.FileError(
            filename, f"File {filename} does not exist in directory {path_str}"
        )
