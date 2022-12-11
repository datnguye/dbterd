from importlib import import_module


def load_executor(name: str):
    try:
        return import_module(name=f".{name}", package="dbterd.adapters.executors")
    except ModuleNotFoundError as exc:
        if exc.name == "dbterd.adapters.executors." + name:
            raise Exception(f"Could not find adapter executor type {name}!")
        raise
