import os
from pathlib import Path

import click

from dbterd import default
from dbterd.adapters import adapter
from dbterd.adapters.dbt_invocation import DbtInvocation
from dbterd.adapters.filter import has_unsupported_rule
from dbterd.helpers import cli_messaging
from dbterd.helpers import file as file_handlers
from dbterd.helpers.log import logger


class Executor:
    """Main Executor"""

    ctx: click.Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.filename_manifest = "manifest.json"
        self.filename_catalog = "catalog.json"

    def run(self, **kwargs):
        """Main function helps to run by the target strategy"""
        kwargs = self.evaluate_kwargs(**kwargs)
        logger.info(f"Using dbt artifact dir at: {kwargs.get('artifacts_dir')}")
        logger.info(f"Using dbt project  dir at: {kwargs.get('dbt_project_dir')}")
        self.__run_by_strategy(**kwargs)

    def evaluate_kwargs(self, **kwargs) -> dict:
        """Re-calculate the options

        Raises:
            click.UsageError: Not Supported exception

        Returns:
            dict: kwargs dict
        """
        artifacts_dir, dbt_project_dir = self.__get_dir(**kwargs)

        select = list(kwargs.get("select")) or []
        exclude = list(kwargs.get("exclude")) or []
        if kwargs.get("dbt"):
            select = self.__get_selection(**kwargs)
            exclude = []
        else:
            unsupported, rule = has_unsupported_rule(
                rules=select.extend(exclude) if exclude else select
            )
            if unsupported:
                message = f"Unsupported Selection found: {rule}"
                logger.error(message)
                raise click.UsageError(message)

        kwargs["artifacts_dir"] = artifacts_dir
        kwargs["dbt_project_dir"] = dbt_project_dir
        kwargs["select"] = select
        kwargs["exclude"] = exclude

        return kwargs

    def __get_dir(self, **kwargs) -> str:
        """Calculate the dbt artifact directory and dbt project directory

        Returns:
            tuple(str, str): Path to target directory and dbt project directory
        """
        artifact_dir = Path(
            f"{kwargs.get('artifacts_dir') or kwargs.get('dbt_project_dir')}"
        ).absolute()  # default
        project_dir = Path(
            f"{kwargs.get('dbt_project_dir') or kwargs.get('artifacts_dir')}"
        ).absolute()  # default

        if not os.path.isfile(f"{artifact_dir}/{self.filename_manifest}"):
            artifact_dir = f"{project_dir}/target"  # try child target
        if not os.path.isfile(f"{artifact_dir}/{self.filename_manifest}"):
            artifact_dir = default.default_artifact_path()  # fallback to CWD
        if not os.path.isfile(f"{project_dir}/dbt_project.yml"):
            # fallback to CWD
            project_dir = Path(default.default_artifact_path()).parent.absolute()

        return (str(artifact_dir), str(project_dir))

    def __get_selection(self, **kwargs):
        """Override the Selection using dbt's one with `--dbt`"""
        return DbtInvocation(
            dbt_project_dir=kwargs.get("dbt_project_dir"),
            dbt_target=kwargs.get("dbt_target"),
        ).get_selection(
            select_rules=kwargs.get("select"),
            exclude_rules=kwargs.get("exclude"),
        )

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
            return file_handlers.read_manifest(path=mp, version=mv)

    def __read_catalog(self, cp: str, cv: int = None):
        """Read the Catalog content

        Args:
            cp (str): catalog.json file path
            cv (int, optional): Catalog version. Defaults to None.

        Returns:
            dict: Catalog dict
        """
        cli_messaging.check_existence(cp, self.filename_catalog)
        with cli_messaging.handle_read_errors(self.filename_catalog):
            return file_handlers.read_catalog(path=cp, version=cv)

    def __run_by_strategy(self, **kwargs):
        """Read artifacts and export the diagram file following the target"""
        target = adapter.load_executor(name=kwargs["target"])  # import {target}
        run_operation_dispatcher = getattr(target, "run_operation_dispatcher")
        operation_default = getattr(target, "run_operation_default")
        operation = run_operation_dispatcher.get(
            f"{kwargs['target']}_{kwargs['algo'].split(':')[0]}",
            operation_default,
        )

        manifest = self.__read_manifest(
            mp=kwargs.get("artifacts_dir"),
            mv=kwargs.get("manifest_version"),
        )
        catalog = self.__read_catalog(
            cp=kwargs.get("artifacts_dir"),
            cv=kwargs.get("catalog_version"),
        )

        result = operation(manifest=manifest, catalog=catalog, **kwargs)
        path = kwargs.get("output") + f"/{result[0]}"
        try:
            with open(path, "w") as f:
                logger.info(path)
                f.write(result[1])
        except Exception as e:
            logger.error(str(e))
            raise click.FileError(f"Could not save the output: {str(e)}")
