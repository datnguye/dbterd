import abc
from asyncio.log import logger
import json
from pathlib import Path
from click import Context
from dbterd.adapters import factory
from dbt_artifacts_parser import parser


class Executor(abc.ABC):
    ctx: Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx

    @abc.abstractmethod
    def run(self, **kwargs):
        self.__run_by_strategy(**kwargs)

    def __read_manifest(self, mp: str, mv: int = None):
        with open(f"{mp}/manifest.json", "r") as fp:
            manifest_dict = json.load(fp)
            parse_func = getattr(parser, "parse_manifest")
            if mv:
                parse_func = getattr(parser, f"parse_manifest_v{mv}")
            manifest_obj = parse_func(manifest=manifest_dict)

            return manifest_obj

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
        result = strategy_func(manifest)
        path = kwargs["output"] + f"/{result[0]}"
        with open(path, "w") as f:
            logger.info(path)
            f.write(result[1])
