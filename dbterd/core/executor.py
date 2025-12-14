"""Base executor module for dbterd.

This module provides the main Executor class that orchestrates
ERD generation from dbt artifacts.
"""

import importlib
import os
from pathlib import Path
import pkgutil
from typing import Optional

import click

from dbterd import default
from dbterd.adapters import algos, targets
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.filter import has_unsupported_rule
from dbterd.core.models import Ref, Table
from dbterd.core.registry.plugin_registry import PluginRegistry
from dbterd.helpers import cli_messaging, file as file_handlers
from dbterd.helpers.log import logger
from dbterd.plugins.dbt_cloud.administrative import DbtCloudArtifact
from dbterd.plugins.dbt_cloud.discovery import DbtCloudMetadata
from dbterd.plugins.dbt_core.dbt_invocation import DbtInvocation


def _register_adapters() -> None:
    """Import adapter modules to trigger plugin registration via decorators."""
    adapter_packages = [algos, targets]
    for package in adapter_packages:
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{package.__name__}.{module_name}")


_register_adapters()


class Executor:
    """Main Executor for ERD generation."""

    ctx: click.Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.filename_manifest = "manifest.json"
        self.filename_catalog = "catalog.json"
        self.dbt: DbtInvocation = None

    def run(self, node_unique_id: Optional[str] = None, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Generate ERD from files."""
        logger.info(f"Using algorithm [{kwargs.get('algo')}]")
        kwargs = self.evaluate_kwargs(**kwargs)
        return self._run_by_strategy(node_unique_id=node_unique_id, **kwargs)

    def run_metadata(self, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Generate ERD from API metadata."""
        logger.info(f"Using algorithm [{kwargs.get('algo')}]")
        kwargs = self.evaluate_kwargs(**kwargs)
        return self._run_metadata_by_strategy(**kwargs)

    def evaluate_kwargs(self, **kwargs) -> dict:
        """Re-calculate the options.

        Raises:
            click.UsageError: Not Supported exception

        Returns:
            Evaluated kwargs dict

        """
        artifacts_dir, dbt_project_dir = self._get_dir(**kwargs)
        command = self.ctx.command.name

        select = list(kwargs.get("select")) or []
        exclude = list(kwargs.get("exclude")) or []

        if not kwargs.get("dbt"):
            self._check_if_any_unsupported_selection(select, exclude)

        if command == "run":
            if kwargs.get("dbt"):
                logger.info(f"Using dbt project dir at: {dbt_project_dir}")
                self.dbt = DbtInvocation(
                    dbt_project_dir=kwargs.get("dbt_project_dir"),
                    dbt_target=kwargs.get("dbt_target"),
                )
                select = self._get_selection(**kwargs)
                exclude = []
                if not select:
                    select = ["exact:none"]  # 'cause [] is all, so let's select nothing here

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

    def load_target(self, name: str) -> BaseTargetAdapter:
        """Load and instantiate a target adapter."""
        adapter_class = PluginRegistry.get_target(name)
        return adapter_class()

    def load_algo(self, name: str) -> BaseAlgoAdapter:
        """Load and instantiate an algo adapter."""
        module_name = name.split(":")[0]
        adapter_class = PluginRegistry.get_algo(module_name)
        return adapter_class()

    def _check_if_any_unsupported_selection(self, select: Optional[list] = None, exclude: Optional[list] = None):
        """Throw an error if detected any unsupported selections.

        Args:
            select: Select rules
            exclude: Exclude rules

        Raises:
            click.UsageError: Unsupported selection

        """
        if exclude is None:
            exclude = []
        if select is None:
            select = []
        rules = list(select)
        rules.extend(exclude)
        unsupported, rule = has_unsupported_rule(rules=rules)
        if unsupported:
            message = f"Unsupported Selection found: {rule}"
            logger.error(message)
            raise click.UsageError(message)

    def _get_dir(self, **kwargs) -> str:
        """Calculate the dbt artifact directory and dbt project directory.

        Returns:
            Tuple of (artifact_dir, project_dir)

        """
        artifact_dir = f"{kwargs.get('artifacts_dir') or kwargs.get('dbt_project_dir')}"
        project_dir = f"{kwargs.get('dbt_project_dir') or kwargs.get('artifacts_dir')}"

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

    def _get_selection(self, **kwargs) -> list[str]:
        """Override the Selection using dbt's one with `--dbt`."""
        if not self.dbt:
            raise click.UsageError("Flag `--dbt` need to be enabled")

        return self.dbt.get_selection(
            select_rules=kwargs.get("select"),
            exclude_rules=kwargs.get("exclude"),
        )

    def _read_manifest(self, mp: str, mv: Optional[int] = None, bypass_validation: bool = False):
        """Read the Manifest content.

        Args:
            mp: manifest.json file path
            mv: Manifest version (None for auto-detect)
            bypass_validation: Skip validation

        Returns:
            Manifest object

        """
        if mv is None:
            detected_version = default.default_manifest_version(artifacts_dir=mp)
            if detected_version:
                mv = int(detected_version)
                logger.info(f"Auto-detected manifest version: {mv}")

        cli_messaging.check_existence(mp, self.filename_manifest)
        conditional = f" or provided version {mv} is incorrect" if mv else ""
        with cli_messaging.handle_read_errors(self.filename_manifest, conditional):
            return file_handlers.read_manifest(path=mp, version=mv, enable_compat_patch=bypass_validation)

    def _read_catalog(self, cp: str, cv: Optional[int] = None, bypass_validation: bool = False):
        """Read the Catalog content.

        Args:
            cp: catalog.json file path
            cv: Catalog version (None for auto-detect)
            bypass_validation: Skip validation

        Returns:
            Catalog object

        """
        if cv is None:
            detected_version = default.default_catalog_version(artifacts_dir=cp)
            if detected_version:
                cv = int(detected_version)
                logger.info(f"Auto-detected catalog version: {cv}")

        cli_messaging.check_existence(cp, self.filename_catalog)
        with cli_messaging.handle_read_errors(self.filename_catalog):
            return file_handlers.read_catalog(path=cp, version=cv, enable_compat_patch=bypass_validation)

    def _save_result(self, path, data):
        """Save ERD data to file.

        Args:
            path: Output directory path
            data: Tuple of (filename, content)

        Raises:
            click.FileError: Cannot save the file

        """
        try:
            file_path = f"{path}/{data[0]}"
            with open(file_path, "w", encoding="utf-8") as f:
                logger.info(f"Output saved to {file_path}")
                f.write(data[1])
        except OSError as e:
            logger.error(str(e))
            raise click.FileError(f"Could not save the output: {e!s}") from e

    def _set_single_node_selection(self, manifest, node_unique_id: str, type: Optional[str] = None, **kwargs) -> dict:
        """Override the Selection for the specific manifest node.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type (file or metadata)

        Returns:
            Edited kwargs dict

        """
        if not node_unique_id:
            return kwargs

        algo_adapter = self.load_algo(name=kwargs["algo"])
        kwargs["select"] = algo_adapter.find_related_nodes_by_id(
            manifest=manifest, node_unique_id=node_unique_id, type=type, **kwargs
        )
        kwargs["exclude"] = []

        return kwargs

    def _run_by_strategy(self, node_unique_id: Optional[str] = None, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Local File - Read artifacts and export the diagram file following the target."""
        if kwargs.get("dbt_cloud"):
            DbtCloudArtifact(**kwargs).get(artifacts_dir=kwargs.get("artifacts_dir"))

        manifest = self._read_manifest(
            mp=kwargs.get("artifacts_dir"),
            mv=kwargs.get("manifest_version"),
            bypass_validation=kwargs.get("bypass_validation"),
        )
        catalog = self._read_catalog(
            cp=kwargs.get("artifacts_dir"),
            cv=kwargs.get("catalog_version"),
            bypass_validation=kwargs.get("bypass_validation"),
        )

        if node_unique_id:
            kwargs = self._set_single_node_selection(manifest=manifest, node_unique_id=node_unique_id, **kwargs)

        # Load adapters
        algo_adapter = self.load_algo(name=kwargs["algo"])
        target_adapter = self.load_target(name=kwargs["target"])

        # Parse artifacts to get tables and relationships
        tables, relationships = algo_adapter.parse(manifest=manifest, catalog=catalog, **kwargs)

        # Generate ERD content
        result = target_adapter.run(tables=tables, relationships=relationships, manifest=manifest, **kwargs)

        if not kwargs.get("api"):
            self._save_result(path=kwargs.get("output"), data=result)

        return result[1]

    def _run_metadata_by_strategy(self, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Metadata - Read artifacts and export the diagram file following the target."""
        data = DbtCloudMetadata(**kwargs).query_erd_data()

        # Load adapters
        algo_adapter = self.load_algo(name=kwargs["algo"])
        target_adapter = self.load_target(name=kwargs["target"])

        # Parse metadata to get tables and relationships
        tables, relationships = algo_adapter.parse(manifest=data, catalog="metadata", **kwargs)

        # Generate ERD content
        result = target_adapter.run(tables=tables, relationships=relationships, **kwargs)

        if not kwargs.get("api"):
            self._save_result(path=kwargs.get("output"), data=result)

        return result[1]
