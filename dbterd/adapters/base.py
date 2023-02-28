import abc
import contextlib
import json
from asyncio.log import logger
from pathlib import Path

import click

from dbterd.adapters import factory
from dbterd.adapters.sources.file_io import read_catalog, read_manifest


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


class Executor(abc.ABC):
    ctx: click.Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.filename_manifest = "manifest.json"
        self.filename_catalog = "catalog.json"

    @abc.abstractmethod
    def run(self, **kwargs):
        self.__run_by_strategy(**kwargs)

    def __read_manifest(self, mp: str, mv: int = None):
        check_existence(mp, self.filename_manifest)
        conditional = f" or provided version {mv} is incorrect" if mv else ""
        with handle_read_errors(self.filename_manifest, conditional):
            return read_manifest(mp, mv)

    def __read_catalog(self, cp: str):
        check_existence(cp, self.filename_catalog)
        with handle_read_errors(self.filename_catalog):
            return read_catalog(cp)

    def __run_by_strategy(self, **kwargs):
        target_module = factory.load_executor(name=kwargs["target"])
        operation_dispatcher = getattr(target_module, "run_operation_dispatcher")
        strategy_func = operation_dispatcher.get(
            f"{kwargs['target']}_{kwargs['algo']}",
            getattr(target_module, "operation_default"),
        )
        manifest = self.__read_manifest(
            mp=kwargs["manifest_path"], mv=kwargs["manifest_version"]
        )
        catalog = self.__read_catalog(
            # TODO: Find a cleaner way to pass these args
            cp=kwargs.get("catalog_path", kwargs["manifest_path"])
        )

        result = strategy_func(manifest=manifest, catalog=catalog, **kwargs)
        path = kwargs["output"] + f"/{result[0]}"
        with open(path, "w") as f:
            logger.info(path)
            f.write(result[1])
