import abc

import click

from dbterd.adapters import factory
from dbterd.helpers import cli_messaging
from dbterd.helpers import file as file_handlers
from dbterd.helpers.log import logger


class Executor(abc.ABC):
    """Base executor"""

    ctx: click.Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.filename_manifest = "manifest.json"
        self.filename_catalog = "catalog.json"

    @abc.abstractmethod
    def run(self, **kwargs):
        """Main function helps to run by the target strategy"""
        self.__run_by_strategy(**kwargs)

    def __read_manifest(self, mp: str, mv: int = None):
        """Read the Manifest content

        Args:
            mp (str): manifest.json json file path
            mv (int, optional): Manifest version. Defaults to None.

        Returns:
            dict: Manifest dict
        """
        cli_messaging.check_existence(mp, self.filename_manifest)
        conditional = f" or provided version {mv} is incorrect" if mv else ""
        with cli_messaging.handle_read_errors(self.filename_manifest, conditional):
            return file_handlers.read_manifest(mp, mv)

    def __read_catalog(self, cp: str):
        """Read the Catalog content

        Args:
            cp (str): catalog.json file path

        Returns:
            dict: Catalog dict
        """
        cli_messaging.check_existence(cp, self.filename_catalog)
        with cli_messaging.handle_read_errors(self.filename_catalog):
            return file_handlers.read_catalog(cp)

    def __run_by_strategy(self, **kwargs):
        """Read artifacts and export the diagram file following the target"""
        target = factory.load_executor(name=kwargs["target"])  # import {target}
        run_operation_dispatcher = getattr(target, "run_operation_dispatcher")
        operation_default = getattr(target, "run_operation_default")
        operation = run_operation_dispatcher.get(
            f"{kwargs['target']}_{kwargs['algo']}",
            operation_default,
        )
        manifest = self.__read_manifest(
            mp=kwargs.get("manifest_path") or kwargs["artifacts_dir"],
            mv=kwargs["manifest_version"],
        )
        catalog = self.__read_catalog(
            cp=kwargs.get("manifest_path") or kwargs["artifacts_dir"]
        )

        result = operation(manifest=manifest, catalog=catalog, **kwargs)
        path = kwargs["output"] + f"/{result[0]}"
        with open(path, "w") as f:
            logger.info(path)
            f.write(result[1])
