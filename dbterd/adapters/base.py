import abc
from click import Context
from dbterd.adapters import factory


class Executor(abc.ABC):
    ctx: Context

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx

    @abc.abstractmethod
    def run(self, **kwargs):
        self.__run_by_strategy(**kwargs)

    def __run_by_strategy(self, **kwargs):
        target_module = factory.load_executor(name=kwargs["target"])
        operation_dispatcher = getattr(target_module, "run_operation_dispatcher")
        strategy_func = operation_dispatcher.get(
            f"{kwargs['target']}_{kwargs['algo']}",
            getattr(target_module, "operation_default"),
        )
        strategy_func(manifest_path=kwargs["manifest_path"])
