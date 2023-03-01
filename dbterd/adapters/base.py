import abc
from asyncio.log import logger

import click

from dbterd.adapters import factory
from dbterd.helpers import cli_messaging
from dbterd.helpers import file as file_handlers


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
        cli_messaging.check_existence(mp, self.filename_manifest)
        conditional = f" or provided version {mv} is incorrect" if mv else ""
        with cli_messaging.handle_read_errors(self.filename_manifest, conditional):
            return file_handlers.read_manifest(mp, mv)

    def __read_catalog(self, cp: str):
        cli_messaging.check_existence(cp, self.filename_catalog)
        with cli_messaging.handle_read_errors(self.filename_catalog):
            return file_handlers.read_catalog(cp)

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
        _ = self.__read_catalog(
            # TODO: Find a cleaner way to pass these args
            cp=kwargs.get("catalog_path", kwargs["manifest_path"])
        )

        result = strategy_func(manifest=manifest, **kwargs)
        path = kwargs["output"] + f"/{result[0]}"
        with open(path, "w") as f:
            logger.info(path)
            f.write(result[1])
