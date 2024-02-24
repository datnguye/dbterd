import os
from pathlib import Path
from types import NotImplementedType
from typing import List, Tuple

import click

from dbterd import default
from dbterd.adapters import adapter
from dbterd.adapters.dbt_cloud.administrative import DbtCloudArtifact
from dbterd.adapters.dbt_cloud.discovery import DbtCloudMetadata
from dbterd.adapters.dbt_core.dbt_invocation import DbtInvocation
from dbterd.adapters.filter import has_unsupported_rule
from dbterd.adapters.meta import Ref, Table
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
        self.dbt: DbtInvocation = None

    def run(
        self, node_unique_id: str = None, **kwargs
    ) -> Tuple[List[Table], List[Ref]]:
        """Generate ERD from files"""
        kwargs = self.evaluate_kwargs(**kwargs)
        return self.__run_by_strategy(node_unique_id=node_unique_id, **kwargs)

    def run_metadata(self, **kwargs) -> Tuple[List[Table], List[Ref]]:
        """Generate ERD from API metadata"""
        kwargs = self.evaluate_kwargs(**kwargs)
        return self.__run_metadata_by_strategy(**kwargs)

    def evaluate_kwargs(self, **kwargs) -> dict:
        """Re-calculate the options

        Raises:
            click.UsageError: Not Supported exception

        Returns:
            dict: kwargs dict
        """
        artifacts_dir, dbt_project_dir = self.__get_dir(**kwargs)
        command = self.ctx.command.name

        select = list(kwargs.get("select")) or []
        exclude = list(kwargs.get("exclude")) or []
        unsupported, rule = has_unsupported_rule(
            rules=select.extend(exclude) if exclude else select
        )
        if unsupported:
            message = f"Unsupported Selection found: {rule}"
            logger.error(message)
            raise click.UsageError(message)

        if command == "run":
            if kwargs.get("dbt"):
                logger.info(f"Using dbt project dir at: {dbt_project_dir}")
                self.dbt = DbtInvocation(
                    dbt_project_dir=kwargs.get("dbt_project_dir"),
                    dbt_target=kwargs.get("dbt_target"),
                )
                select = self.__get_selection(**kwargs)
                exclude = []

                if kwargs.get("dbt_auto_artifacts"):
                    self.dbt.get_artifacts_for_erd()
                    artifacts_dir = f"{dbt_project_dir}/target"
            elif kwargs.get("dbt_cloud"):
                artifacts_dir = f"{dbt_project_dir}/target"
            logger.info(f"Using dbt artifact dir at: {artifacts_dir}")

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
        artifact_dir = (
            f"{kwargs.get('artifacts_dir') or kwargs.get('dbt_project_dir')}"  # default
        )
        project_dir = (
            f"{kwargs.get('dbt_project_dir') or kwargs.get('artifacts_dir')}"  # default
        )

        if not artifact_dir:
            return (
                default.default_artifact_path(),
                str(Path(default.default_artifact_path()).parent.absolute()),
            )

        artifact_dir = Path(artifact_dir).absolute()
        project_dir = Path(project_dir).absolute()

        if not os.path.isfile(f"{artifact_dir}/{self.filename_manifest}"):
            artifact_dir = f"{project_dir}/target"  # try child target

        return (str(artifact_dir), str(project_dir))

    def __get_selection(self, **kwargs) -> List[str]:
        """Override the Selection using dbt's one with `--dbt`"""
        if not self.dbt:
            raise click.UsageError("Flag `--dbt` need to be enabled")

        return self.dbt.get_selection(
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

    def __get_operation(self, kwargs):
        """Get target's operation (aka.`parse` function)

        Returns:
            func: Operation function
        """
        target = adapter.load_target(name=kwargs["target"])  # import {target}
        run_operation_dispatcher = getattr(target, "run_operation_dispatcher")
        operation_default = getattr(target, "run_operation_default")
        operation = run_operation_dispatcher.get(
            f"{kwargs['target']}_{kwargs['algo'].split(':')[0]}",
            operation_default,
        )

        return operation

    def __save_result(self, path, data):
        """Save ERD data to file

        Args:
            path (str): Output file path
            data (dict): ERD data

        Raises:
            click.FileError: Can not save the file
        """
        try:
            with open(f"{path}/{data[0]}", "w") as f:
                logger.info(path)
                f.write(data[1])
        except Exception as e:
            logger.error(str(e))
            raise click.FileError(f"Could not save the output: {str(e)}")

    def __set_single_node_selection(
        self, manifest, node_unique_id: str, type: str = None, **kwargs
    ) -> dict:
        """Override the Selection for the specific manifest node

        Args:
            manifest (Union[Manifest, dict]): Manifest data of dbt project
            node_unique_id (str): Manifest node unique ID
            type (str, optional): |
                Determine manifest type e.g. from file or from metadata.
                Defaults to None.

        Returns:
            dict: Editted kwargs dict
        """
        if not node_unique_id:
            return kwargs

        algo_module = adapter.load_algo(name=kwargs["algo"])
        kwargs["select"] = algo_module.find_related_nodes_by_id(
            manifest=manifest, node_unique_id=node_unique_id, type=type, **kwargs
        )
        kwargs["exclude"] = []

        return kwargs

    def __run_by_strategy(
        self, node_unique_id: str = None, **kwargs
    ) -> Tuple[List[Table], List[Ref]]:
        """Local File - Read artifacts and export the diagram file following the target"""
        if kwargs.get("dbt_cloud"):
            DbtCloudArtifact(**kwargs).get(artifacts_dir=kwargs.get("artifacts_dir"))

        manifest = self.__read_manifest(
            mp=kwargs.get("artifacts_dir"),
            mv=kwargs.get("manifest_version"),
        )
        catalog = self.__read_catalog(
            cp=kwargs.get("artifacts_dir"),
            cv=kwargs.get("catalog_version"),
        )

        if node_unique_id:
            kwargs = self.__set_single_node_selection(
                manifest=manifest, node_unique_id=node_unique_id, **kwargs
            )
        operation = self.__get_operation(kwargs)
        result = operation(manifest=manifest, catalog=catalog, **kwargs)

        if not kwargs.get("api"):
            self.__save_result(path=kwargs.get("output"), data=result)

        if type(result) == NotImplementedType:
            return result

        return result[1]

    def __run_metadata_by_strategy(self, **kwargs) -> Tuple[List[Table], List[Ref]]:
        """Metadata - Read artifacts and export the diagram file following the target"""
        data = DbtCloudMetadata(**kwargs).query_erd_data()
        operation = self.__get_operation(kwargs)

        result = operation(manifest=data, catalog="metadata", **kwargs)

        if not kwargs.get("api"):
            self.__save_result(path=kwargs.get("output"), data=result)

        if type(result) == NotImplementedType:
            return result

        return result[1]
