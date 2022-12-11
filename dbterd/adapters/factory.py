from importlib import import_module


def load_executor(name: str):
    try:
        return import_module(name=f".{name}", package="dbterd.adapters.targets")
    except ModuleNotFoundError as exc:
        if exc.name == "dbterd.adapters.targets." + name:
            raise Exception(f"Could not find adapter target type {name}!")
        raise
