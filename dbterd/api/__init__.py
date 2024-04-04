import logging
from pathlib import Path

from click import Command, Context

from dbterd import default
from dbterd.adapters.base import Executor
from dbterd.helpers.log import logger

logger.setLevel(logging.WARNING)  # hide log


class DbtErd:
    """
    dbt ERD official API functions.


    **Usage**:

    ## Get a whole ERD

    ```python
    from dbterd.api import DbtErd
    erd = DbtErd().get_erd()
    ```

    ## Get a whole ERD given all models attached to `my_exposure_name`

    ```python
    from dbterd.api import DbtErd
    erd = DbtErd(select="exposure:my_exposure_name").get_erd()
    ```
    See the
    [Selection](https://dbterd.datnguyen.de/latest/nav/guide/cli-references.html#dbterd-run-select-s)
    page for more details.

    ## Get a model (named `model.jaffle_shop.my_model`)'s ERD

    ```python
    from dbterd.api import DbtErd
    erd = DbtErd().get_model_erd(s
        node_fqn="model.jaffle_shop.my_model"
    )
    ```
    """

    def __init__(self, **kwargs) -> None:
        """Initialize the main Executor given similar input CLI parameters"""

        self.params: dict = kwargs
        """
        Mimic CLI params with overriding `api = True`.\n
        Check
        [CLI reference page](https://dbterd.datnguyen.de/latest/nav/guide/cli-references.html)
        for more details of how the params are used.
        """
        self.__set_params_default_if_not_specified()
        ctx_command = self.params.get("api_context_command")
        self.executor: Executor = Executor(
            Context(Command(name=ctx_command if ctx_command else "run"))
        )
        """
        Mimic CLI's executor.\n
        The context command is `run` by default
        unless specifying a param named `api_context_command`
        """

    def __set_params_default_if_not_specified(self) -> None:
        """Set base params' default value (mimic CLI behaviors where possible)"""
        self.params["api"] = True

        self.params["select"] = self.params.get("select", [])
        self.params["exclude"] = self.params.get("exclude", [])
        self.params["resource_type"] = self.params.get(
            "resource_type", default.default_resource_types()
        )
        self.params["algo"] = self.params.get("algo", default.default_algo())
        self.params["entity_name_format"] = self.params.get(
            "entity_name_format", default.default_entity_name_format()
        )
        self.params["omit_columns"] = self.params.get("omit_columns", False)
        self.params["artifacts_dir"] = self.params.get("artifacts_dir", Path.cwd())
        self.params["target"] = self.params.get("target", default.default_target())

    def get_erd(self) -> str:
        """Generate ERD code for a whole project

        Usage:
        ```python
        from dbterd.api import DbtErd
        erd = DbtErd().get_erd()
        ```

        Returns:
            str: ERD text
        """
        return self.executor.run(**self.params)

    def get_model_erd(self, node_unique_id: str) -> str:
        """Generate ERD code for a model.

        Result contains the input model and 1 level relationship model(s) (if any).

        Usage:

            ```python
            from dbterd.api import DbtErd
            erd = DbtErd().get_model_erd(
                node_unique_id="model.jaffle_shop.my_model"
            )
            ```

        Args:
            - node_unique_id (str): Manifest node unique ID

        Returns:
            str: ERD text
        """
        return self.executor.run(node_unique_id=node_unique_id, **self.params)
