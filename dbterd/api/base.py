from typing import List, Tuple

from click import Command, Context

from dbterd import default
from dbterd.adapters.base import Executor
from dbterd.adapters.meta import Ref, Table


class DbtErd:
    """dbt ERD official API functions"""

    def __init__(self, **kwargs) -> None:
        """Initialize the main Executor given similar input CLI parameters"""
        ctx_command = kwargs.get("api_context_command")
        self.executor = Executor(
            Context(Command(name=ctx_command if ctx_command else "run"))
        )
        self.params = kwargs
        self.__set_params_default_if_not_specified()

    def __set_params_default_if_not_specified(self) -> None:
        """Set base params' default value (mimic CLI behaviors where possible)"""
        self.params["api"] = True

        self.params["select"] = self.params.get("select", [])
        self.params["exclude"] = self.params.get("exclude", [])
        self.params["resource_type"] = self.params.get(
            "resource_type", default.default_resource_types()
        )
        self.params["algo"] = self.params.get("algo", default.deafult_algo())
        self.params["entity_name_format"] = self.params.get(
            "entity_name_format", default.default_entity_name_format()
        )
        self.params["omit_columns"] = self.params.get("omit_columns", False)

    def get_erd(self) -> Tuple[List[Table], List[Ref]]:
        """Generate ERD code for a whole project

        Usage:
        ```python
        from dbterd.api.base import DbtErd
        erd = DbtErd().get_erd()
        ```

        Returns:
            Tuple[List[Table], List[Ref]]: Tables and Refs
        """
        return self.executor.run(**self.params)

    def get_model_erd(self, node_fqn: str) -> Tuple[List[Table], List[Ref]]:
        """Generate ERD code for a model.

        Result contains this model and 1 level relationship models (if any).

        Usage:
        ```python
        from dbterd.api.base import DbtErd
        erd = DbtErd().get_model_erd(node_fqn="model")
        ```

        Returns:
            Tuple[List[Table], List[Ref]]: Tables and Refs
        """
        find_nodes = [node_fqn]
        # TODO - find FK models of this model

        params = self.params
        params["select"] = [f"exact:{x}" for x in find_nodes]
        params["exclude"] = []

        return self.executor.run(**params)
