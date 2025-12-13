from importlib import util
from importlib.metadata import version
import os
from pathlib import Path
from typing import Optional

import click

from dbterd.helpers.log import logger


try:
    from dbt.cli.main import dbtRunner as DbtRunner
except ImportError:
    DbtRunner = None


class DbtInvocation:
    """Runner of dbt (https://docs.getdbt.com/reference/programmatic-invocations)."""

    def __init__(self, dbt_project_dir: Optional[str] = None, dbt_target: Optional[str] = None) -> None:
        """
        Initialization.

        Args:
            dbt_project_dir (str, optional): Custom dbt project directory path. Defaults to None.
            dbt_target (str, optional): Custom dbt target name. Defaults to None - using default target

        """
        self.__ensure_dbt_installed()
        self.dbt = DbtRunner()
        self.project_dir = dbt_project_dir or os.environ.get("DBT_PROJECT_DIR") or str(Path.cwd())
        self.target = dbt_target
        self.args = ["--quiet", "--log-level", "none"]

    def __invoke(self, runner_args: Optional[list[str]] = None):
        """
        Base function of the dbt invocation.

        Args:
            runner_args (List[str], optional): Actual dbt arguments. Defaults to [].

        Raises:
            click.UsageError: Invocation failed for a reason

        Returns:
            dbtRunnerResult.result: dbtRunnerResult.result

        """
        if runner_args is None:
            runner_args = []
        args = self.__construct_arguments(*runner_args)
        logger.debug(f"Invoking: `dbt {' '.join(args)}` at {self.project_dir}")
        r = self.dbt.invoke(args)

        if not r.success:
            logger.error(str(r))
            raise click.UsageError(str(r))

        return r.result

    def __construct_arguments(self, *args) -> list[str]:
        """
        Enrich the dbt arguments with the based options.

        Returns:
            List[str]: Actual dbt arguments

        """
        evaluated_args = args
        if self.args:
            evaluated_args = [*self.args, *args]
        if self.project_dir:
            evaluated_args.extend(["--project-dir", self.project_dir])
        if self.target:
            evaluated_args.extend(["--target", self.target])

        return evaluated_args

    def __ensure_dbt_installed(self):
        """
        Verify if dbt get installed.

        Raises:
            click.UsageError: dbt is not installed

        """
        dbt_spec = util.find_spec("dbt")
        if dbt_spec and dbt_spec.loader:
            installed_path = dbt_spec.submodule_search_locations[0]
            logger.debug(f"Found dbt v{version('dbt-core')} installed at {installed_path}")
        else:
            message = (
                "dbt module is not found or unsupported version, "
                "please try to install dbt-core v1.5 or later, "
                "OR let's try again without `--dbt` flag"
            )
            logger.error(message)
            raise click.UsageError(message)

    def get_selection(
        self,
        select_rules: Optional[list[str]] = None,
        exclude_rules: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Get dbt selected models.

        Args:
            select_rules (List[str], optional): Model inclusives. Defaults to [].
            exclude_rules (List[str], optional): Model exclusives. Defaults to [].

        Returns:
            List[str]: Selected node names with 'exact' rule

        """
        if exclude_rules is None:
            exclude_rules = []
        if select_rules is None:
            select_rules = []
        args = ["ls", "--resource-type", "model"]
        if select_rules:
            args.extend(["--select", " ".join(select_rules)])
        if exclude_rules:
            args.extend(["--exclude", " ".join(exclude_rules)])

        result = self.__invoke(runner_args=args)
        return [f"exact:model.{str(x).split('.')[0]}.{str(x).split('.')[-1]}" for x in result]

    def get_artifacts_for_erd(self):
        """
        Generate dbt artifacts using `dbt docs generate` command.

        Returns:
            dbtRunnerResult: dbtRunnerResult

        """
        return self.__invoke(runner_args=["docs", "generate"])
